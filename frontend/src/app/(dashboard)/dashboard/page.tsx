"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useAuthStore } from "@/store/auth";
import api from "@/lib/api";
import type { User } from "@/types/user";
import type { RFQ } from "@/types/rfq";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

interface DashboardStats {
  active_rfqs: number;
  pending_responses: number;
  unread_messages: number;
  incoming_rfqs: number;
  review_count: number;
  profile_completion: number;
  unread_notifications: number;
}

function StatCard({
  title,
  value,
  description,
}: {
  title: string;
  value: number | string;
  description?: string;
}) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardDescription>{title}</CardDescription>
        <CardTitle className="text-3xl">{value}</CardTitle>
      </CardHeader>
      {description && (
        <CardContent>
          <p className="text-xs text-muted-foreground">{description}</p>
        </CardContent>
      )}
    </Card>
  );
}

function RecentRfqList({ rfqs, label }: { rfqs: RFQ[]; label: string }) {
  if (rfqs.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">{label}</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">No RFQs yet.</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">{label}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {rfqs.map((rfq) => (
          <Link
            key={rfq.id}
            href={`/rfqs/${rfq.id}`}
            className="flex items-center justify-between rounded-lg border p-3 hover:bg-muted/50 transition-colors"
          >
            <div className="min-w-0 flex-1">
              <p className="text-sm font-medium truncate">{rfq.title}</p>
              <p className="text-xs text-muted-foreground">
                Deadline: {new Date(rfq.deadline).toLocaleDateString()}
              </p>
            </div>
            <Badge
              variant={
                rfq.status === "open"
                  ? "default"
                  : rfq.status === "awarded"
                    ? "secondary"
                    : "outline"
              }
            >
              {rfq.status}
            </Badge>
          </Link>
        ))}
      </CardContent>
    </Card>
  );
}

function BuyerDashboard({ stats }: { stats: DashboardStats }) {
  const [recentRfqs, setRecentRfqs] = useState<RFQ[]>([]);

  useEffect(() => {
    api
      .get("/rfqs", { params: { page_size: 5 } })
      .then((res) => setRecentRfqs(res.data.items ?? []))
      .catch(() => {});
  }, []);

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-3">
        <StatCard title="Active RFQs" value={stats.active_rfqs} />
        <StatCard title="Pending Responses" value={stats.pending_responses} />
        <StatCard title="Unread Messages" value={stats.unread_messages} />
      </div>

      <RecentRfqList rfqs={recentRfqs} label="Recent RFQs" />

      <div className="flex gap-3">
        <Button render={<Link href="/rfqs/create" />}>
          Create RFQ
        </Button>
        <Button variant="outline" render={<Link href="/search" />}>
          Search Suppliers
        </Button>
      </div>
    </div>
  );
}

function SupplierDashboard({ stats }: { stats: DashboardStats }) {
  const [incomingRfqs, setIncomingRfqs] = useState<RFQ[]>([]);

  useEffect(() => {
    api
      .get("/rfqs/incoming", { params: { page_size: 5 } })
      .then((res) => setIncomingRfqs(res.data.items ?? []))
      .catch(() => {});
  }, []);

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-3">
        <StatCard title="Incoming RFQs" value={stats.incoming_rfqs} />
        <StatCard title="Reviews" value={stats.review_count} />
        <StatCard
          title="Profile Completion"
          value={`${stats.profile_completion}%`}
        />
      </div>

      <RecentRfqList rfqs={incomingRfqs} label="Recent Incoming RFQs" />
    </div>
  );
}

function IndividualDashboard({ stats }: { stats: DashboardStats }) {
  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-3">
        <StatCard
          title="Profile Completion"
          value={`${stats.profile_completion}%`}
          description="Complete your profile to attract more opportunities"
        />
        <StatCard title="Reviews" value={stats.review_count} />
        <StatCard
          title="Unread Notifications"
          value={stats.unread_notifications}
        />
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Profile Completion</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="w-full bg-muted rounded-full h-3">
            <div
              className="bg-primary h-3 rounded-full transition-all"
              style={{ width: `${stats.profile_completion}%` }}
            />
          </div>
          <p className="mt-2 text-sm text-muted-foreground">
            {stats.profile_completion < 100
              ? "Complete your profile to get more visibility."
              : "Your profile is complete!"}
          </p>
          {stats.profile_completion < 100 && (
            <Button className="mt-3" variant="outline" size="sm" render={<Link href="/profile" />}>
              Complete Profile
            </Button>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user) as User | null;
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .get("/dashboard/stats")
      .then((res) => setStats(res.data))
      .catch(() => setError("Failed to load dashboard data."))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  if (error || !stats) {
    return (
      <div className="py-20 text-center">
        <p className="text-destructive">{error ?? "Something went wrong."}</p>
        <Button
          variant="outline"
          className="mt-4"
          onClick={() => window.location.reload()}
        >
          Retry
        </Button>
      </div>
    );
  }

  const accountType = user?.account_type;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">
        Welcome back{user?.first_name ? `, ${user.first_name}` : ""}
      </h1>

      {accountType === "buyer" && <BuyerDashboard stats={stats} />}
      {(accountType === "supplier" ||
        accountType === "manufacturer" ||
        accountType === "distributor" ||
        accountType === "contractor" ||
        accountType === "subcontractor") && (
        <SupplierDashboard stats={stats} />
      )}
      {accountType === "individual" && <IndividualDashboard stats={stats} />}
    </div>
  );
}
