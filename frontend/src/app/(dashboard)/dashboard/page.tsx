"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useAuthStore } from "@/store/auth";
import api from "@/lib/api";
import type { User } from "@/types/user";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";

const ACCOUNT_TYPE_LABELS: Record<string, string> = {
  buyer: "Buyer",
  supplier: "Supplier",
  manufacturer: "Manufacturer",
  distributor: "Distributor",
  contractor: "Contractor",
  subcontractor: "Subcontractor",
  individual: "Individual Professional",
};

const SUPPLIER_TYPES = new Set([
  "supplier",
  "manufacturer",
  "distributor",
  "contractor",
  "subcontractor",
]);

function QuickActions({ accountType }: { accountType: string }) {
  if (accountType === "buyer") {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Quick Actions</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-3">
          <Button render={<Link href="/rfqs/create" />}>Create RFQ</Button>
          <Button variant="outline" render={<Link href="/search" />}>
            Search Suppliers
          </Button>
        </CardContent>
      </Card>
    );
  }

  if (SUPPLIER_TYPES.has(accountType)) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Quick Actions</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-3">
          <Button render={<Link href="/rfqs" />}>
            View Incoming RFQs
          </Button>
          <Button variant="outline" render={<Link href="/company/profile" />}>
            Company Profile
          </Button>
        </CardContent>
      </Card>
    );
  }

  if (accountType === "individual") {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Quick Actions</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-3">
          <Button render={<Link href="/profile" />}>Edit Profile</Button>
          <Button variant="outline" render={<Link href="/search" />}>
            Browse Companies
          </Button>
        </CardContent>
      </Card>
    );
  }

  return null;
}

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user) as User | null;
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

  return (
    <div className="space-y-6">
      {/* Welcome card */}
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl">
            Welcome back{displayName ? `, ${displayName}` : ""}
          </CardTitle>
          <CardDescription>
            Account type:{" "}
            {ACCOUNT_TYPE_LABELS[accountType] ?? accountType}
          </CardDescription>
        </CardHeader>
      </Card>

      {/* Notifications card */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Unread Notifications</CardDescription>
            <CardTitle className="text-3xl">{unreadCount}</CardTitle>
          </CardHeader>
          <CardContent>
            <Button
              variant="outline"
              size="sm"
              render={<Link href="/notifications" />}
            >
              View Notifications
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Role-based quick actions */}
      <QuickActions accountType={accountType} />
    </div>
  );
}
