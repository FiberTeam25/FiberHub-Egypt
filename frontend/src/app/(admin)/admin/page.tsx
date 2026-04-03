"use client";

import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Users, Building2, ShieldCheck, Flag, Loader2 } from "lucide-react";

export default function AdminDashboardPage() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ["adminStats"],
    queryFn: async () => { const res = await api.get("/admin/dashboard"); return res.data; },
  });

  if (isLoading) return <div className="flex justify-center py-12"><Loader2 className="h-6 w-6 animate-spin" /></div>;

  const cards = [
    { label: "Total Users", value: stats?.total_users || 0, icon: Users },
    { label: "Total Companies", value: stats?.total_companies || 0, icon: Building2 },
    { label: "Verified Companies", value: stats?.verified_companies || 0, icon: ShieldCheck },
    { label: "Pending Verifications", value: stats?.pending_verifications || 0, icon: ShieldCheck },
    { label: "Flagged Reviews", value: stats?.flagged_reviews || 0, icon: Flag },
  ];

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Admin Dashboard</h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
        {cards.map((card) => (
          <Card key={card.label}>
            <CardHeader className="pb-2"><CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2"><card.icon className="h-4 w-4" />{card.label}</CardTitle></CardHeader>
            <CardContent><p className="text-2xl font-bold">{card.value}</p></CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
