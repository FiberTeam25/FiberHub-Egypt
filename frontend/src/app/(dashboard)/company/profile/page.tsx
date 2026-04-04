"use client";

import { useEffect, useState } from "react";
import { useAuthStore } from "@/store/auth";
import { useUpdateCompany } from "@/hooks/useCompanies";
import api from "@/lib/api";
import { NoCompanyPrompt } from "@/components/layout/NoCompanyPrompt";
import type { Company, CompanyType, CompanySize } from "@/types/company";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";

const COMPANY_TYPES: CompanyType[] = [
  "buyer",
  "supplier",
  "distributor",
  "manufacturer",
  "contractor",
  "subcontractor",
];

const COMPANY_SIZES: CompanySize[] = [
  "1-10",
  "11-50",
  "51-200",
  "201-500",
  "500+",
];

const GOVERNORATES = [
  "Cairo",
  "Giza",
  "Alexandria",
  "Qalyubia",
  "Dakahlia",
  "Sharqia",
  "Gharbia",
  "Monufia",
  "Beheira",
  "Kafr El Sheikh",
  "Damietta",
  "Port Said",
  "Ismailia",
  "Suez",
  "North Sinai",
  "South Sinai",
  "Fayoum",
  "Beni Suef",
  "Minya",
  "Asyut",
  "Sohag",
  "Qena",
  "Luxor",
  "Aswan",
  "Red Sea",
  "New Valley",
  "Matrouh",
];

interface FormState {
  name: string;
  description: string;
  company_type: CompanyType;
  company_size: CompanySize | "";
  year_established: string;
  website: string;
  email: string;
  phone: string;
  address: string;
  city: string;
  governorate: string;
}

export default function CompanyProfilePage() {
  const user = useAuthStore((s) => s.user);
  const updateCompany = useUpdateCompany();

  const [companyId, setCompanyId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  const [form, setForm] = useState<FormState>({
    name: "",
    description: "",
    company_type: "supplier",
    company_size: "",
    year_established: "",
    website: "",
    email: "",
    phone: "",
    address: "",
    city: "",
    governorate: "",
  });

  useEffect(() => {
    if (!user) return;
    api
      .get(`/companies/mine`)
      .then((res) => {
        const c: Company = res.data;
        setCompanyId(c.id);
        setForm({
          name: c.name ?? "",
          description: c.description ?? "",
          company_type: c.company_type,
          company_size: c.company_size ?? "",
          year_established: c.year_established?.toString() ?? "",
          website: c.website ?? "",
          email: c.email ?? "",
          phone: c.phone ?? "",
          address: c.address ?? "",
          city: c.city ?? "",
          governorate: c.governorate ?? "",
        });
      })
      .catch(() => setError("Failed to load company profile."))
      .finally(() => setLoading(false));
  }, [user]);

  const handleChange = (
    field: keyof FormState,
    value: string,
  ) => {
    setForm((prev) => ({ ...prev, [field]: value }));
    setSaved(false);
  };

  const handleSave = async () => {
    if (!companyId) return;
    try {
      await updateCompany.mutateAsync({
        id: companyId,
        data: {
          ...form,
          year_established: form.year_established
            ? parseInt(form.year_established, 10)
            : null,
          company_size: form.company_size || null,
        },
      });
      setSaved(true);
    } catch {
      setError("Failed to save changes.");
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  if (error && !companyId) {
    return <NoCompanyPrompt />;
  }

  return (
    <div className="max-w-3xl space-y-6">
      <h1 className="text-2xl font-bold">Edit Company Profile</h1>

      {/* Basic Info */}
      <Card>
        <CardHeader>
          <CardTitle>Basic Information</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="name">Company Name</Label>
            <Input
              id="name"
              value={form.name}
              onChange={(e) => handleChange("name", e.target.value)}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              value={form.description}
              onChange={(e) => handleChange("description", e.target.value)}
              rows={4}
            />
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label>Company Type</Label>
              <Select
                value={form.company_type}
                onValueChange={(v) => handleChange("company_type", v ?? "")}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {COMPANY_TYPES.map((t) => (
                    <SelectItem key={t} value={t}>
                      {t.charAt(0).toUpperCase() + t.slice(1)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Company Size</Label>
              <Select
                value={form.company_size}
                onValueChange={(v) => handleChange("company_size", v ?? "")}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select size" />
                </SelectTrigger>
                <SelectContent>
                  {COMPANY_SIZES.map((s) => (
                    <SelectItem key={s} value={s}>
                      {s} employees
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <div className="space-y-2">
            <Label htmlFor="year_established">Year Established</Label>
            <Input
              id="year_established"
              type="number"
              value={form.year_established}
              onChange={(e) => handleChange("year_established", e.target.value)}
              placeholder="e.g. 2015"
            />
          </div>
        </CardContent>
      </Card>

      <Separator />

      {/* Contact */}
      <Card>
        <CardHeader>
          <CardTitle>Contact Information</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={form.email}
                onChange={(e) => handleChange("email", e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="phone">Phone</Label>
              <Input
                id="phone"
                value={form.phone}
                onChange={(e) => handleChange("phone", e.target.value)}
              />
            </div>
          </div>
          <div className="space-y-2">
            <Label htmlFor="website">Website</Label>
            <Input
              id="website"
              type="url"
              value={form.website}
              onChange={(e) => handleChange("website", e.target.value)}
              placeholder="https://"
            />
          </div>
        </CardContent>
      </Card>

      <Separator />

      {/* Business Details */}
      <Card>
        <CardHeader>
          <CardTitle>Business Details</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="address">Address</Label>
            <Input
              id="address"
              value={form.address}
              onChange={(e) => handleChange("address", e.target.value)}
            />
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="city">City</Label>
              <Input
                id="city"
                value={form.city}
                onChange={(e) => handleChange("city", e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label>Governorate</Label>
              <Select
                value={form.governorate}
                onValueChange={(v) => handleChange("governorate", v ?? "")}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select governorate" />
                </SelectTrigger>
                <SelectContent>
                  {GOVERNORATES.map((g) => (
                    <SelectItem key={g} value={g}>
                      {g}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {error && <p className="text-sm text-destructive">{error}</p>}
      {saved && (
        <p className="text-sm text-green-600">Changes saved successfully.</p>
      )}

      <div className="flex justify-end">
        <Button
          onClick={handleSave}
          disabled={updateCompany.isPending}
        >
          {updateCompany.isPending ? "Saving..." : "Save Changes"}
        </Button>
      </div>
    </div>
  );
}
