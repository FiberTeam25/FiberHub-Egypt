"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useTranslation } from "@/store/language";
import { useCreateRfq, usePublishRfq, useInviteCompanies } from "@/hooks/useRfqs";
import { useCategories } from "@/hooks/useSearch";
import { useSearchCompanies } from "@/hooks/useSearch";
import api from "@/lib/api";
import type { Category, Governorate } from "@/types/category";
import type { Company } from "@/types/company";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface FormData {
  title: string;
  request_type: string;
  description: string;
  category_id: string;
  category_type: string;
  location: string;
  governorate: string;
  timeline: string;
  quantity_scope: string;
  deadline: string;
  notes: string;
}

const INITIAL_FORM: FormData = {
  title: "",
  request_type: "",
  description: "",
  category_id: "",
  category_type: "product",
  location: "",
  governorate: "",
  timeline: "",
  quantity_scope: "",
  deadline: "",
  notes: "",
};

export default function CreateRfqPage() {
  const router = useRouter();
  const t = useTranslation();
  const createRfq = useCreateRfq();
  const publishRfq = usePublishRfq();
  const inviteCompanies = useInviteCompanies();
  const { data: categories, isLoading: categoriesLoading } = useCategories();

  const [step, setStep] = useState(1);
  const [form, setForm] = useState<FormData>(INITIAL_FORM);
  const [rfqId, setRfqId] = useState<string | null>(null);

  // Attachments state
  const [attachments, setAttachments] = useState<{ file_url: string; file_name: string }[]>([]);
  const [uploading, setUploading] = useState(false);

  // Invite companies state
  const [companySearch, setCompanySearch] = useState("");
  const [selectedCompanies, setSelectedCompanies] = useState<Company[]>([]);
  const { data: searchResults } = useSearchCompanies(
    companySearch.length >= 2 ? { q: companySearch } : {}
  );
  const searchedCompanies: Company[] =
    (searchResults as { items?: Company[] })?.items ?? (Array.isArray(searchResults) ? searchResults : []);

  const [error, setError] = useState<string | null>(null);

  function updateField(field: keyof FormData, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  async function handleSaveDraft() {
    setError(null);
    try {
      const payload: Record<string, unknown> = { ...form };
      if (!payload.category_id) delete payload.category_id;
      if (attachments.length > 0) payload.attachments = attachments;

      if (rfqId) {
        await api.patch(`/rfqs/${rfqId}`, payload);
      } else {
        const res = await createRfq.mutateAsync(payload);
        setRfqId(res.id);
      }
      router.push("/rfqs");
    } catch {
      setError(t("rfqs.saveDraftFailed"));
    }
  }

  async function handleNextStep() {
    setError(null);
    if (step === 1) {
      if (!form.title || !form.deadline) {
        setError("Title and deadline are required.");
        return;
      }
      // Create or update draft
      try {
        const payload: Record<string, unknown> = { ...form };
        if (!payload.category_id) delete payload.category_id;

        if (rfqId) {
          await api.patch(`/rfqs/${rfqId}`, payload);
        } else {
          const res = await createRfq.mutateAsync(payload);
          setRfqId(res.id);
        }
        setStep(2);
      } catch {
        setError(t("rfqs.saveFailed"));
      }
    } else if (step === 2) {
      setStep(3);
    }
  }

  async function handleFileUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const files = e.target.files;
    if (!files || files.length === 0 || !rfqId) return;

    setUploading(true);
    try {
      for (const file of Array.from(files)) {
        const formData = new FormData();
        formData.append("file", file);
        const res = await api.post(`/rfqs/${rfqId}/attachments`, formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });
        setAttachments((prev) => [
          ...prev,
          { file_url: res.data.file_url, file_name: res.data.file_name ?? file.name },
        ]);
      }
    } catch {
      setError("File upload failed.");
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  }

  function toggleCompany(company: Company) {
    setSelectedCompanies((prev) => {
      const exists = prev.find((c) => c.id === company.id);
      if (exists) return prev.filter((c) => c.id !== company.id);
      return [...prev, company];
    });
  }

  async function handlePublish() {
    if (!rfqId) return;
    setError(null);
    try {
      if (selectedCompanies.length > 0) {
        await inviteCompanies.mutateAsync({
          rfqId,
          companyIds: selectedCompanies.map((c) => c.id),
        });
      }
      await publishRfq.mutateAsync(rfqId);
      router.push(`/rfqs/${rfqId}`);
    } catch {
      setError(t("rfqs.publishFailed"));
    }
  }

  const productCategories: Category[] = categories?.products ?? [];
  const serviceCategories: Category[] = categories?.services ?? [];
  const governorates: Governorate[] = categories?.governorates ?? [];
  const activeCategories =
    form.category_type === "service" ? serviceCategories : productCategories;

  return (
    <div className="max-w-3xl space-y-6">
      <h1 className="text-2xl font-bold">Create RFQ</h1>

      {/* Step indicator */}
      <div className="flex items-center gap-2">
        {[1, 2, 3].map((s) => (
          <div
            key={s}
            className={`flex items-center justify-center h-8 w-8 rounded-full text-sm font-medium ${
              s === step
                ? "bg-primary text-primary-foreground"
                : s < step
                  ? "bg-primary/20 text-primary"
                  : "bg-muted text-muted-foreground"
            }`}
          >
            {s}
          </div>
        ))}
        <span className="ml-2 text-sm text-muted-foreground">
          {step === 1 && "Basic Details"}
          {step === 2 && "Attachments"}
          {step === 3 && "Invite Companies"}
        </span>
      </div>

      {error && (
        <p className="text-sm text-destructive">{error}</p>
      )}

      {/* Step 1: Basic details */}
      {step === 1 && (
        <Card>
          <CardHeader>
            <CardTitle>Basic Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="title">Title *</Label>
              <Input
                id="title"
                value={form.title}
                onChange={(e) => updateField("title", e.target.value)}
                placeholder="e.g., FTTH Materials for Cairo Project"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="request_type">Request Type</Label>
              <Select
                value={form.request_type}
                onValueChange={(v) => updateField("request_type", v as string)}
              >
                <SelectTrigger id="request_type">
                  <SelectValue placeholder="Select type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="product">Product</SelectItem>
                  <SelectItem value="service">Service</SelectItem>
                  <SelectItem value="both">Product & Service</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={form.description}
                onChange={(e) => updateField("description", e.target.value)}
                rows={4}
                placeholder="Describe what you need..."
              />
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label>Category Type</Label>
                <Select
                  value={form.category_type}
                  onValueChange={(v) => {
                    updateField("category_type", v as string);
                    updateField("category_id", "");
                  }}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="product">Product</SelectItem>
                    <SelectItem value="service">Service</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Category</Label>
                <Select
                  value={form.category_id}
                  onValueChange={(v) => updateField("category_id", v as string)}
                  disabled={categoriesLoading}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select category" />
                  </SelectTrigger>
                  <SelectContent>
                    {activeCategories.map((cat) => (
                      <SelectItem key={cat.id} value={cat.id}>
                        {cat.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="location">Location</Label>
                <Input
                  id="location"
                  value={form.location}
                  onChange={(e) => updateField("location", e.target.value)}
                  placeholder="Project site / city"
                />
              </div>

              <div className="space-y-2">
                <Label>Governorate</Label>
                <Select
                  value={form.governorate}
                  onValueChange={(v) => updateField("governorate", v as string)}
                  disabled={categoriesLoading}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select governorate" />
                  </SelectTrigger>
                  <SelectContent>
                    {governorates.map((gov) => (
                      <SelectItem key={gov.id} value={gov.name}>
                        {gov.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="timeline">Timeline</Label>
                <Input
                  id="timeline"
                  value={form.timeline}
                  onChange={(e) => updateField("timeline", e.target.value)}
                  placeholder="e.g., 2 weeks, 1 month"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="quantity_scope">Quantity / Scope</Label>
                <Input
                  id="quantity_scope"
                  value={form.quantity_scope}
                  onChange={(e) => updateField("quantity_scope", e.target.value)}
                  placeholder="e.g., 500 meters, full installation"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="deadline">Deadline *</Label>
              <Input
                id="deadline"
                type="date"
                value={form.deadline}
                onChange={(e) => updateField("deadline", e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="notes">Additional Notes</Label>
              <Textarea
                id="notes"
                value={form.notes}
                onChange={(e) => updateField("notes", e.target.value)}
                rows={3}
              />
            </div>
          </CardContent>
        </Card>
      )}

      {/* Step 2: Attachments */}
      {step === 2 && (
        <Card>
          <CardHeader>
            <CardTitle>Attachments</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="file-upload">Upload Files</Label>
              <Input
                id="file-upload"
                type="file"
                multiple
                onChange={handleFileUpload}
                disabled={uploading}
              />
              {uploading && (
                <p className="text-sm text-muted-foreground">Uploading...</p>
              )}
            </div>

            {attachments.length > 0 && (
              <div className="space-y-2">
                <Label>Uploaded Files</Label>
                <ul className="space-y-1">
                  {attachments.map((att, i) => (
                    <li
                      key={i}
                      className="flex items-center justify-between rounded border px-3 py-2 text-sm"
                    >
                      <span>{att.file_name}</span>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() =>
                          setAttachments((prev) => prev.filter((_, idx) => idx !== i))
                        }
                      >
                        Remove
                      </Button>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {attachments.length === 0 && !uploading && (
              <p className="text-sm text-muted-foreground">
                No attachments yet. You can upload BOQs, drawings, or specs.
              </p>
            )}
          </CardContent>
        </Card>
      )}

      {/* Step 3: Invite Companies */}
      {step === 3 && (
        <Card>
          <CardHeader>
            <CardTitle>Invite Companies</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="company-search">Search Companies</Label>
              <Input
                id="company-search"
                value={companySearch}
                onChange={(e) => setCompanySearch(e.target.value)}
                placeholder="Search by company name..."
              />
            </div>

            {companySearch.length >= 2 && searchedCompanies.length > 0 && (
              <div className="max-h-48 overflow-y-auto rounded border divide-y">
                {searchedCompanies.map((company) => {
                  const isSelected = selectedCompanies.some((c) => c.id === company.id);
                  return (
                    <button
                      key={company.id}
                      type="button"
                      onClick={() => toggleCompany(company)}
                      className={`w-full px-3 py-2 text-left text-sm hover:bg-muted/50 transition-colors ${
                        isSelected ? "bg-primary/10" : ""
                      }`}
                    >
                      <span className="font-medium">{company.name}</span>
                      <span className="ml-2 text-xs text-muted-foreground">
                        {company.company_type} - {company.governorate ?? "Egypt"}
                      </span>
                    </button>
                  );
                })}
              </div>
            )}

            {selectedCompanies.length > 0 && (
              <div className="space-y-2">
                <Label>Selected Companies ({selectedCompanies.length})</Label>
                <div className="flex flex-wrap gap-2">
                  {selectedCompanies.map((company) => (
                    <Badge
                      key={company.id}
                      variant="secondary"
                      className="cursor-pointer"
                      onClick={() => toggleCompany(company)}
                    >
                      {company.name} x
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {selectedCompanies.length === 0 && (
              <p className="text-sm text-muted-foreground">
                Search and select companies to invite. You can also publish without
                invitations to make the RFQ visible to all suppliers.
              </p>
            )}
          </CardContent>
        </Card>
      )}

      {/* Navigation buttons */}
      <div className="flex items-center gap-3">
        {step > 1 && (
          <Button variant="outline" onClick={() => setStep((s) => s - 1)}>
            Back
          </Button>
        )}

        {step < 3 && (
          <Button
            onClick={handleNextStep}
            disabled={createRfq.isPending}
          >
            {createRfq.isPending ? "Saving..." : "Next"}
          </Button>
        )}

        {step === 3 && (
          <Button
            onClick={handlePublish}
            disabled={publishRfq.isPending || inviteCompanies.isPending}
          >
            {publishRfq.isPending ? "Publishing..." : "Publish RFQ"}
          </Button>
        )}

        <Button
          variant="outline"
          onClick={handleSaveDraft}
          disabled={createRfq.isPending}
        >
          Save as Draft
        </Button>
      </div>
    </div>
  );
}
