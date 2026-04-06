"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import { useTranslation } from "@/store/language";
import { NoCompanyPrompt } from "@/components/layout/NoCompanyPrompt";
import type { VerificationStatus } from "@/types/company";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface VerificationInfo {
  status: VerificationStatus;
  rejection_notes?: string | null;
  submitted_at?: string | null;
  reviewed_at?: string | null;
}

const DOCUMENT_TYPES = [
  "commercial_register",
  "tax_card",
  "engineering_license",
  "company_profile",
  "other",
];

function statusBadgeVariant(
  status: VerificationStatus,
): "default" | "secondary" | "destructive" | "outline" {
  switch (status) {
    case "approved":
      return "default";
    case "pending":
      return "secondary";
    case "rejected":
    case "expired":
      return "destructive";
    default:
      return "outline";
  }
}

function statusLabel(status: VerificationStatus, t: (k: string) => string): string {
  const labels: Record<VerificationStatus, string> = {
    not_submitted: t("verification.statusNotSubmitted"),
    pending: t("verification.statusPending"),
    approved: t("verification.statusApproved"),
    rejected: t("verification.statusRejected"),
    expired: t("verification.statusExpired"),
    needs_update: t("verification.statusNeedsUpdate"),
  };
  return labels[status];
}

export default function VerificationPage() {
  const t = useTranslation();
  const [info, setInfo] = useState<VerificationInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Upload form
  const [docType, setDocType] = useState(DOCUMENT_TYPES[0]);
  const [file, setFile] = useState<File | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  const fetchStatus = async () => {
    try {
      const res = await api.get("/verification/status");
      setInfo(res.data);
    } catch {
      setError(t("verification.loadFailed"));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  const handleSubmit = async () => {
    if (!file) return;
    setSubmitting(true);
    setSubmitSuccess(false);
    try {
      const formData = new FormData();
      formData.append("document_type", docType);
      formData.append("file", file);
      await api.post("/verification/submit", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setSubmitSuccess(true);
      setFile(null);
      await fetchStatus();
    } catch {
      setError(t("verification.submitFailed"));
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  if (error && !info) {
    return <NoCompanyPrompt />;
  }

  const status = info?.status ?? "not_submitted";

  return (
    <div className="max-w-2xl space-y-6">
      <h1 className="text-2xl font-bold">{t("verification.title")}</h1>

      <Card>
        <CardHeader>
          <CardTitle>{t("verification.statusTitle")}</CardTitle>
          <CardDescription>{t("verification.statusDesc")}</CardDescription>
        </CardHeader>
        <CardContent>
          <Badge variant={statusBadgeVariant(status)} className="text-sm">
            {statusLabel(status, t as (k: string) => string)}
          </Badge>
          {info?.submitted_at && (
            <p className="mt-2 text-sm text-muted-foreground">
              {t("verification.submittedOn")}{" "}
              {new Date(info.submitted_at).toLocaleDateString()}
            </p>
          )}
          {info?.reviewed_at && (
            <p className="text-sm text-muted-foreground">
              {t("verification.reviewedOn")}{" "}
              {new Date(info.reviewed_at).toLocaleDateString()}
            </p>
          )}
        </CardContent>
      </Card>

      {/* Approved */}
      {status === "approved" && (
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-full bg-green-100 flex items-center justify-center text-green-700 font-bold text-lg">
                V
              </div>
              <div>
                <p className="font-semibold text-green-700">
                  {t("verification.approvedMsg")}
                </p>
                <p className="text-sm text-muted-foreground">
                  {t("verification.approvedDesc")}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Pending */}
      {status === "pending" && (
        <Card>
          <CardContent className="pt-6">
            <p className="font-medium">{t("verification.pendingMsg")}</p>
            <p className="text-sm text-muted-foreground mt-1">
              {t("verification.pendingDesc")}
            </p>
          </CardContent>
        </Card>
      )}

      {/* Rejected */}
      {(status === "rejected" || status === "needs_update") && (
        <Card>
          <CardContent className="pt-6 space-y-3">
            <p className="font-medium text-destructive">
              {t("verification.rejectedMsg")}
            </p>
            {info?.rejection_notes && (
              <div className="rounded-md border border-destructive/30 bg-destructive/5 p-3">
                <p className="text-sm font-medium">{t("verification.reviewerNotes")}</p>
                <p className="text-sm text-muted-foreground mt-1">
                  {info.rejection_notes}
                </p>
              </div>
            )}
            <p className="text-sm text-muted-foreground">
              {t("verification.rejectedDesc")}
            </p>
          </CardContent>
        </Card>
      )}

      {/* Upload form (show for not_submitted, rejected, needs_update, expired) */}
      {(status === "not_submitted" ||
        status === "rejected" ||
        status === "needs_update" ||
        status === "expired") && (
        <Card>
          <CardHeader>
            <CardTitle>
              {status === "not_submitted"
                ? t("verification.submitTitle")
                : t("verification.resubmitTitle")}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>{t("verification.docType")}</Label>
              <Select value={docType} onValueChange={(v) => setDocType(v ?? DOCUMENT_TYPES[0])}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {DOCUMENT_TYPES.map((dt) => (
                    <SelectItem key={dt} value={dt}>
                      {dt
                        .split("_")
                        .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
                        .join(" ")}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="doc-file">{t("verification.uploadDoc")}</Label>
              <Input
                id="doc-file"
                type="file"
                accept=".pdf,.jpg,.jpeg,.png"
                onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              />
              <p className="text-xs text-muted-foreground">
                {t("verification.uploadFormats")}
              </p>
            </div>

            {error && <p className="text-sm text-destructive">{error}</p>}
            {submitSuccess && (
              <p className="text-sm text-green-600">
                {t("verification.submitSuccess")}
              </p>
            )}

            <Button
              onClick={handleSubmit}
              disabled={!file || submitting}
            >
              {submitting ? t("verification.submitting") : t("verification.submitBtn")}
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
