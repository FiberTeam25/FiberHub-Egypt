"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import { useAuthStore } from "@/store/auth";
import { useTranslation } from "@/store/language";
import { useRfq, useRfqResponses, useSubmitResponse } from "@/hooks/useRfqs";
import api from "@/lib/api";
import type { RFQ, RFQResponse, RFQAttachment, RFQInvitation, RFQStatus } from "@/types/rfq";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Separator } from "@/components/ui/separator";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

const STATUS_VARIANTS: Record<RFQStatus, "default" | "secondary" | "outline" | "destructive"> = {
  draft: "outline",
  open: "default",
  closed: "secondary",
  awarded: "secondary",
  cancelled: "destructive",
};

interface ResponseFormData {
  cover_note: string;
  quoted_amount: string;
  currency: string;
  delivery_time: string;
  notes: string;
}

const INITIAL_RESPONSE: ResponseFormData = {
  cover_note: "",
  quoted_amount: "",
  currency: "EGP",
  delivery_time: "",
  notes: "",
};

function SupplierResponseForm({ rfqId }: { rfqId: string }) {
  const submitResponse = useSubmitResponse();
  const t = useTranslation();
  const [form, setForm] = useState<ResponseFormData>(INITIAL_RESPONSE);
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState(false);

  function updateField(field: keyof ResponseFormData, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    try {
      let file_url: string | null = null;
      let file_name: string | null = null;

      if (file) {
        const formData = new FormData();
        formData.append("file", file);
        const uploadRes = await api.post("/upload", formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });
        file_url = uploadRes.data.file_url;
        file_name = uploadRes.data.file_name ?? file.name;
      }

      await submitResponse.mutateAsync({
        rfqId,
        data: {
          cover_note: form.cover_note || null,
          quoted_amount: form.quoted_amount ? parseFloat(form.quoted_amount) : null,
          currency: form.currency || null,
          delivery_time: form.delivery_time || null,
          notes: form.notes || null,
          file_url,
          file_name,
        },
      });
      setSubmitted(true);
    } catch {
      setError(t("rfqs.submitResponseFailed"));
    }
  }

  if (submitted) {
    return (
      <Card>
        <CardContent className="pt-6 text-center">
          <p className="text-sm text-muted-foreground">
            Your response has been submitted successfully.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Submit Response</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="cover_note">Cover Note</Label>
            <Textarea
              id="cover_note"
              value={form.cover_note}
              onChange={(e) => updateField("cover_note", e.target.value)}
              rows={3}
              placeholder="Introduce your proposal..."
            />
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="quoted_amount">Quoted Amount</Label>
              <Input
                id="quoted_amount"
                type="number"
                step="0.01"
                value={form.quoted_amount}
                onChange={(e) => updateField("quoted_amount", e.target.value)}
                placeholder="0.00"
              />
            </div>

            <div className="space-y-2">
              <Label>Currency</Label>
              <Select
                value={form.currency}
                onValueChange={(v) => updateField("currency", v as string)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="EGP">EGP</SelectItem>
                  <SelectItem value="USD">USD</SelectItem>
                  <SelectItem value="EUR">EUR</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="delivery_time">Delivery Time</Label>
            <Input
              id="delivery_time"
              value={form.delivery_time}
              onChange={(e) => updateField("delivery_time", e.target.value)}
              placeholder="e.g., 2 weeks, 30 days"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="response_notes">Additional Notes</Label>
            <Textarea
              id="response_notes"
              value={form.notes}
              onChange={(e) => updateField("notes", e.target.value)}
              rows={2}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="response_file">Attachment</Label>
            <Input
              id="response_file"
              type="file"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            />
          </div>

          {error && <p className="text-sm text-destructive">{error}</p>}

          <Button type="submit" disabled={submitResponse.isPending}>
            {submitResponse.isPending ? "Submitting..." : "Submit Response"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}

function BuyerResponsesView({ rfqId, rfq }: { rfqId: string; rfq: RFQ }) {
  const { data, isLoading } = useRfqResponses(rfqId);
  const responses: RFQResponse[] = Array.isArray(data)
    ? data
    : (data as { items?: RFQResponse[] })?.items ?? [];
  const [awardDialogOpen, setAwardDialogOpen] = useState(false);
  const [awarding, setAwarding] = useState(false);
  const [selectedResponseId, setSelectedResponseId] = useState<string | null>(null);

  async function handleAward() {
    if (!selectedResponseId) return;
    setAwarding(true);
    try {
      await api.post(`/rfqs/${rfqId}/award`, { response_id: selectedResponseId });
      window.location.reload();
    } catch {
      // noop
    } finally {
      setAwarding(false);
      setAwardDialogOpen(false);
    }
  }

  const invitations: RFQInvitation[] = rfq.invitations ?? [];

  return (
    <Tabs defaultValue="responses">
      <TabsList>
        <TabsTrigger value="responses">
          Responses ({responses.length})
        </TabsTrigger>
        <TabsTrigger value="invited">
          Invited ({invitations.length})
        </TabsTrigger>
      </TabsList>

      <TabsContent value="responses">
        {isLoading ? (
          <div className="flex items-center justify-center py-10">
            <div className="h-6 w-6 animate-spin rounded-full border-4 border-primary border-t-transparent" />
          </div>
        ) : responses.length === 0 ? (
          <p className="py-6 text-sm text-muted-foreground">
            No responses received yet.
          </p>
        ) : (
          <>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Company</TableHead>
                  <TableHead>Quoted Amount</TableHead>
                  <TableHead>Delivery Time</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {responses.map((resp) => (
                  <TableRow key={resp.id}>
                    <TableCell className="font-medium">
                      {resp.company_name ?? "—"}
                    </TableCell>
                    <TableCell>
                      {resp.quoted_amount != null
                        ? `${resp.quoted_amount.toLocaleString()} ${resp.currency ?? ""}`
                        : "—"}
                    </TableCell>
                    <TableCell>{resp.delivery_time ?? "—"}</TableCell>
                    <TableCell>
                      <Badge variant="outline">{resp.status}</Badge>
                    </TableCell>
                    <TableCell>
                      <Dialog>
                        <DialogTrigger render={<Button variant="outline" size="sm" />}>
                            View
                        </DialogTrigger>
                        <DialogContent>
                          <DialogHeader>
                            <DialogTitle>
                              Response from {resp.company_name ?? "Supplier"}
                            </DialogTitle>
                          </DialogHeader>
                          <div className="space-y-3">
                            {resp.cover_note && (
                              <div>
                                <Label className="text-xs text-muted-foreground">
                                  Cover Note
                                </Label>
                                <p className="text-sm">{resp.cover_note}</p>
                              </div>
                            )}
                            {resp.quoted_amount != null && (
                              <div>
                                <Label className="text-xs text-muted-foreground">
                                  Quoted Amount
                                </Label>
                                <p className="text-sm">
                                  {resp.quoted_amount.toLocaleString()}{" "}
                                  {resp.currency ?? ""}
                                </p>
                              </div>
                            )}
                            {resp.delivery_time && (
                              <div>
                                <Label className="text-xs text-muted-foreground">
                                  Delivery Time
                                </Label>
                                <p className="text-sm">{resp.delivery_time}</p>
                              </div>
                            )}
                            {resp.notes && (
                              <div>
                                <Label className="text-xs text-muted-foreground">
                                  Notes
                                </Label>
                                <p className="text-sm">{resp.notes}</p>
                              </div>
                            )}
                            {resp.file_url && (
                              <div>
                                <a
                                  href={resp.file_url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="text-sm text-primary hover:underline"
                                >
                                  {resp.file_name ?? "Download attachment"}
                                </a>
                              </div>
                            )}
                          </div>
                        </DialogContent>
                      </Dialog>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>

            {(rfq.status === "closed" || rfq.status === "open") && (
              <div className="mt-4">
                <Dialog open={awardDialogOpen} onOpenChange={setAwardDialogOpen}>
                  <DialogTrigger render={<Button />}>Award RFQ</DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Award RFQ</DialogTitle>
                    </DialogHeader>
                    <div className="space-y-4">
                      <div className="space-y-2">
                        <Label>Select Winning Response</Label>
                        <Select
                          value={selectedResponseId ?? ""}
                          onValueChange={(v) => setSelectedResponseId(v as string)}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Select a response" />
                          </SelectTrigger>
                          <SelectContent>
                            {responses
                              .filter((r) => r.status === "submitted")
                              .map((r) => (
                                <SelectItem key={r.id} value={r.id}>
                                  {r.company_name ?? "Unknown"} -{" "}
                                  {r.quoted_amount != null
                                    ? `${r.quoted_amount.toLocaleString()} ${r.currency ?? ""}`
                                    : "No quote"}
                                </SelectItem>
                              ))}
                          </SelectContent>
                        </Select>
                      </div>
                      <Button
                        onClick={handleAward}
                        disabled={!selectedResponseId || awarding}
                      >
                        {awarding ? "Awarding..." : "Confirm Award"}
                      </Button>
                    </div>
                  </DialogContent>
                </Dialog>
              </div>
            )}
          </>
        )}
      </TabsContent>

      <TabsContent value="invited">
        {invitations.length === 0 ? (
          <p className="py-6 text-sm text-muted-foreground">
            No companies were invited.
          </p>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Company</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Invited At</TableHead>
                <TableHead>Viewed At</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {invitations.map((inv) => (
                <TableRow key={inv.id}>
                  <TableCell className="font-medium">
                    {inv.company_name ?? inv.company_id}
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">{inv.status}</Badge>
                  </TableCell>
                  <TableCell>
                    {new Date(inv.invited_at).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    {inv.viewed_at
                      ? new Date(inv.viewed_at).toLocaleDateString()
                      : "—"}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </TabsContent>
    </Tabs>
  );
}

export default function RfqDetailPage() {
  const params = useParams();
  const rfqId = params.id as string;
  const user = useAuthStore((s) => s.user);
  const t = useTranslation();
  const { data: rfq, isLoading, isError } = useRfq(rfqId);
  const { data: responsesData } = useRfqResponses(rfqId);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  if (isError || !rfq) {
    return (
      <div className="py-20 text-center">
        <p className="text-destructive">{t("rfqs.loadOneFailed")}</p>
      </div>
    );
  }

  const typedRfq = rfq as RFQ;
  const isBuyer = user?.account_type === "buyer";
  const attachments: RFQAttachment[] = typedRfq.attachments ?? [];

  // Check if supplier already submitted a response
  const allResponses: RFQResponse[] = Array.isArray(responsesData)
    ? responsesData
    : (responsesData as { items?: RFQResponse[] })?.items ?? [];
  const myResponse = !isBuyer
    ? allResponses.find((r) => r.submitted_by === user?.id)
    : null;

  return (
    <div className="max-w-4xl space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">{typedRfq.title}</h1>
          <div className="mt-1 flex items-center gap-3 text-sm text-muted-foreground">
            <span>
              by {typedRfq.buyer_company_name ?? "—"}
            </span>
            <span>
              Deadline: {new Date(typedRfq.deadline).toLocaleDateString()}
            </span>
          </div>
        </div>
        <Badge variant={STATUS_VARIANTS[typedRfq.status]} className="text-sm">
          {typedRfq.status}
        </Badge>
      </div>

      <Separator />

      {/* Details */}
      <Card>
        <CardHeader>
          <CardTitle>Details</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {typedRfq.description && (
            <div>
              <Label className="text-xs text-muted-foreground">Description</Label>
              <p className="text-sm whitespace-pre-wrap">{typedRfq.description}</p>
            </div>
          )}

          <div className="grid gap-4 sm:grid-cols-2">
            {typedRfq.request_type && (
              <div>
                <Label className="text-xs text-muted-foreground">Request Type</Label>
                <p className="text-sm capitalize">{typedRfq.request_type}</p>
              </div>
            )}
            {typedRfq.quantity_scope && (
              <div>
                <Label className="text-xs text-muted-foreground">Quantity / Scope</Label>
                <p className="text-sm">{typedRfq.quantity_scope}</p>
              </div>
            )}
            {typedRfq.timeline && (
              <div>
                <Label className="text-xs text-muted-foreground">Timeline</Label>
                <p className="text-sm">{typedRfq.timeline}</p>
              </div>
            )}
            {typedRfq.location && (
              <div>
                <Label className="text-xs text-muted-foreground">Location</Label>
                <p className="text-sm">{typedRfq.location}</p>
              </div>
            )}
            {typedRfq.governorate && (
              <div>
                <Label className="text-xs text-muted-foreground">Governorate</Label>
                <p className="text-sm">{typedRfq.governorate}</p>
              </div>
            )}
          </div>

          {typedRfq.notes && (
            <div>
              <Label className="text-xs text-muted-foreground">Notes</Label>
              <p className="text-sm whitespace-pre-wrap">{typedRfq.notes}</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Attachments */}
      {attachments.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Attachments</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {attachments.map((att) => (
                <li key={att.id} className="flex items-center justify-between rounded border px-3 py-2">
                  <span className="text-sm">{att.file_name}</span>
                  <a
                    href={att.file_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-primary hover:underline"
                  >
                    Download
                  </a>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      <Separator />

      {/* Buyer: see responses and invited companies */}
      {isBuyer && <BuyerResponsesView rfqId={rfqId} rfq={typedRfq} />}

      {/* Supplier: respond or view submitted response */}
      {!isBuyer && (
        <>
          {myResponse ? (
            <Card>
              <CardHeader>
                <CardTitle>Your Submitted Response</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {myResponse.cover_note && (
                  <div>
                    <Label className="text-xs text-muted-foreground">Cover Note</Label>
                    <p className="text-sm">{myResponse.cover_note}</p>
                  </div>
                )}
                {myResponse.quoted_amount != null && (
                  <div>
                    <Label className="text-xs text-muted-foreground">Quoted Amount</Label>
                    <p className="text-sm">
                      {myResponse.quoted_amount.toLocaleString()} {myResponse.currency ?? ""}
                    </p>
                  </div>
                )}
                {myResponse.delivery_time && (
                  <div>
                    <Label className="text-xs text-muted-foreground">Delivery Time</Label>
                    <p className="text-sm">{myResponse.delivery_time}</p>
                  </div>
                )}
                {myResponse.notes && (
                  <div>
                    <Label className="text-xs text-muted-foreground">Notes</Label>
                    <p className="text-sm">{myResponse.notes}</p>
                  </div>
                )}
                {myResponse.file_url && (
                  <a
                    href={myResponse.file_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-primary hover:underline"
                  >
                    {myResponse.file_name ?? "Download attachment"}
                  </a>
                )}
                <Badge variant="outline">{myResponse.status}</Badge>
              </CardContent>
            </Card>
          ) : typedRfq.status === "open" ? (
            <SupplierResponseForm rfqId={rfqId} />
          ) : (
            <Card>
              <CardContent className="pt-6 text-center">
                <p className="text-sm text-muted-foreground">
                  This RFQ is no longer accepting responses.
                </p>
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  );
}
