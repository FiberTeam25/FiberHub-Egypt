"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useTranslation } from "@/store/language";
import { useAuthStore } from "@/store/auth";
import api from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Building2 } from "lucide-react";

// Map user account_type to company_type (individual/admin have no company type)
const COMPANY_TYPE_MAP: Record<string, string> = {
  buyer: "buyer",
  supplier: "supplier",
  distributor: "distributor",
  manufacturer: "manufacturer",
  contractor: "contractor",
  subcontractor: "subcontractor",
};

export function NoCompanyPrompt() {
  const t = useTranslation();
  const router = useRouter();
  const user = useAuthStore((s) => s.user);
  const [name, setName] = useState("");
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const companyType = user?.account_type ? COMPANY_TYPE_MAP[user.account_type] : "supplier";

  const handleCreate = async () => {
    if (!name.trim()) return;
    setCreating(true);
    setError(null);
    try {
      await api.post("/companies/", { name: name.trim(), company_type: companyType });
      router.refresh();
      window.location.reload();
    } catch {
      setError(t("company.createFailed"));
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="flex items-center justify-center py-20">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
            <Building2 className="h-6 w-6 text-primary" />
          </div>
          <CardTitle>{t("company.noCompanyTitle")}</CardTitle>
          <CardDescription>{t("company.noCompanyDesc")}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="company-name">{t("company.companyName")}</Label>
            <Input
              id="company-name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="FiberHub Egypt"
              onKeyDown={(e) => e.key === "Enter" && handleCreate()}
            />
          </div>
          {error && <p className="text-sm text-destructive">{error}</p>}
          <Button
            className="w-full"
            onClick={handleCreate}
            disabled={creating || !name.trim()}
          >
            {creating ? t("company.creating") : t("company.createCompany")}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
