"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useAuthStore } from "@/store/auth";
import { useTranslation } from "@/store/language";
import api from "@/lib/api";
import type { User } from "@/types/user";
import type { TranslationKey } from "@/lib/i18n";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";

const ACCOUNT_TYPE_KEYS: Record<string, TranslationKey> = {
  buyer: "accountType.buyer",
  supplier: "accountType.supplier",
  manufacturer: "accountType.manufacturer",
  distributor: "accountType.distributor",
  contractor: "accountType.contractor",
  subcontractor: "accountType.subcontractor",
  individual: "accountType.individual",
};

const SUPPLIER_TYPES = new Set([
  "supplier",
  "manufacturer",
  "distributor",
  "contractor",
  "subcontractor",
]);

function QuickActions({ accountType }: { accountType: string }) {
  const t = useTranslation();

  if (accountType === "buyer") {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">{t("dashboard.quickActions")}</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-3">
          <Button render={<Link href="/rfqs/create" />}>{t("dashboard.createRfq")}</Button>
          <Button variant="outline" render={<Link href="/search" />}>
            {t("dashboard.searchSuppliers")}
          </Button>
        </CardContent>
      </Card>
    );
  }

  if (SUPPLIER_TYPES.has(accountType)) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">{t("dashboard.quickActions")}</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-3">
          <Button render={<Link href="/rfqs" />}>
            {t("dashboard.viewIncomingRfqs")}
          </Button>
          <Button variant="outline" render={<Link href="/company/profile" />}>
            {t("dashboard.companyProfile")}
          </Button>
        </CardContent>
      </Card>
    );
  }

  if (accountType === "individual") {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">{t("dashboard.quickActions")}</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-3">
          <Button render={<Link href="/profile" />}>{t("dashboard.editProfile")}</Button>
          <Button variant="outline" render={<Link href="/search" />}>
            {t("dashboard.browseCompanies")}
          </Button>
        </CardContent>
      </Card>
    );
  }

  return null;
}

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user) as User | null;
  const t = useTranslation();
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get("/notifications/unread-count")
      .then((res) => setUnreadCount(res.data.unread_count ?? 0))
      .catch(() => setUnreadCount(0))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  const accountType = user?.account_type ?? "";
  const displayName = [user?.first_name, user?.last_name]
    .filter(Boolean)
    .join(" ");

  const accountTypeKey = ACCOUNT_TYPE_KEYS[accountType];

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl">
            {t("dashboard.welcomeBack")}{displayName ? `, ${displayName}` : ""}
          </CardTitle>
          <CardDescription>
            {t("dashboard.accountType")}:{" "}
            {accountTypeKey ? t(accountTypeKey) : accountType}
          </CardDescription>
        </CardHeader>
      </Card>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>{t("dashboard.unreadNotifications")}</CardDescription>
            <CardTitle className="text-3xl">{unreadCount}</CardTitle>
          </CardHeader>
          <CardContent>
            <Button
              variant="outline"
              size="sm"
              render={<Link href="/notifications" />}
            >
              {t("dashboard.viewNotifications")}
            </Button>
          </CardContent>
        </Card>
      </div>

      <QuickActions accountType={accountType} />
    </div>
  );
}
