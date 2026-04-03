"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import api from "@/lib/api";
import type { Company } from "@/types/company";
import { useAuthStore } from "@/store/auth";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";

export default function CompanySettingsPage() {
  const user = useAuthStore((s) => s.user);
  const [company, setCompany] = useState<Company | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .get("/companies/my")
      .then((res) => setCompany(res.data))
      .catch(() => setError("Failed to load company data."))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  if (error || !company) {
    return (
      <div className="py-20 text-center">
        <p className="text-destructive">{error ?? "Company not found."}</p>
      </div>
    );
  }

  return (
    <div className="max-w-2xl space-y-6">
      <h1 className="text-2xl font-bold">Company Settings</h1>

      <Card>
        <CardHeader>
          <CardTitle>Company Information</CardTitle>
          <CardDescription>
            Overview of your company details.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-3 sm:grid-cols-2">
            <div>
              <p className="text-sm text-muted-foreground">Company Name</p>
              <p className="font-medium">{company.name}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Company Type</p>
              <p className="font-medium capitalize">{company.company_type}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">
                Verification Status
              </p>
              <Badge
                variant={
                  company.verification_status === "approved"
                    ? "default"
                    : "outline"
                }
              >
                {company.verification_status.replace("_", " ")}
              </Badge>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">
                Profile Completion
              </p>
              <p className="font-medium">{company.profile_completion}%</p>
            </div>
          </div>
          <Separator />
          <Button render={<Link href="/company/profile" />}>
            Edit Company Profile
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Account</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div>
            <p className="text-sm text-muted-foreground">Account Type</p>
            <p className="font-medium capitalize">
              {user?.account_type ?? "—"}
            </p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Email</p>
            <p className="font-medium">{user?.email ?? "—"}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Member Since</p>
            <p className="font-medium">
              {company.created_at
                ? new Date(company.created_at).toLocaleDateString()
                : "—"}
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
