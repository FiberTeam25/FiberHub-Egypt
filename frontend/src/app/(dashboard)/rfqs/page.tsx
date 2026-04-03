"use client";

import { useState } from "react";
import Link from "next/link";
import { useAuthStore } from "@/store/auth";
import { useRfqs } from "@/hooks/useRfqs";
import type { RFQ, RFQStatus } from "@/types/rfq";
import type { PaginatedResponse } from "@/types/api";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
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

const STATUS_VARIANTS: Record<RFQStatus, "default" | "secondary" | "outline" | "destructive"> = {
  draft: "outline",
  open: "default",
  closed: "secondary",
  awarded: "secondary",
  cancelled: "destructive",
};

function RfqTable({ rfqs }: { rfqs: RFQ[] }) {
  if (rfqs.length === 0) {
    return (
      <div className="py-12 text-center text-muted-foreground">
        No RFQs found.
      </div>
    );
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Title</TableHead>
          <TableHead>Status</TableHead>
          <TableHead>Deadline</TableHead>
          <TableHead>Responses</TableHead>
          <TableHead>Created</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {rfqs.map((rfq) => (
          <TableRow key={rfq.id}>
            <TableCell>
              <Link
                href={`/rfqs/${rfq.id}`}
                className="font-medium hover:underline"
              >
                {rfq.title}
              </Link>
            </TableCell>
            <TableCell>
              <Badge variant={STATUS_VARIANTS[rfq.status]}>{rfq.status}</Badge>
            </TableCell>
            <TableCell>
              {new Date(rfq.deadline).toLocaleDateString()}
            </TableCell>
            <TableCell>{rfq.response_count ?? 0}</TableCell>
            <TableCell>
              {new Date(rfq.created_at).toLocaleDateString()}
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

export default function RfqsPage() {
  const user = useAuthStore((s) => s.user);
  const isBuyer = user?.account_type === "buyer";

  const [tab, setTab] = useState<string>(isBuyer ? "my" : "incoming");
  const [statusFilter, setStatusFilter] = useState<string>("all");

  const params: Record<string, string | number> = {};
  if (tab === "incoming") {
    params.role = "supplier";
  } else {
    params.role = "buyer";
  }
  if (statusFilter !== "all") {
    params.status = statusFilter;
  }

  const { data, isLoading, isError } = useRfqs(params);
  const rfqs: RFQ[] = (data as PaginatedResponse<RFQ>)?.items ?? (Array.isArray(data) ? data : []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  if (isError) {
    return (
      <div className="py-20 text-center">
        <p className="text-destructive">Failed to load RFQs.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">RFQs</h1>
        {isBuyer && (
          <Button render={<Link href="/rfqs/create" />}>Create RFQ</Button>
        )}
      </div>

      <Tabs value={tab} onValueChange={(v) => setTab(v as string)}>
        <div className="flex items-center justify-between gap-4">
          <TabsList>
            <TabsTrigger value="my">My RFQs</TabsTrigger>
            <TabsTrigger value="incoming">Incoming RFQs</TabsTrigger>
          </TabsList>

          <Select value={statusFilter} onValueChange={(v) => setStatusFilter(v as string ?? "")}>
            <SelectTrigger className="w-[160px]">
              <SelectValue placeholder="Filter status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Statuses</SelectItem>
              <SelectItem value="draft">Draft</SelectItem>
              <SelectItem value="open">Open</SelectItem>
              <SelectItem value="closed">Closed</SelectItem>
              <SelectItem value="awarded">Awarded</SelectItem>
              <SelectItem value="cancelled">Cancelled</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <TabsContent value="my">
          <RfqTable rfqs={rfqs} />
        </TabsContent>
        <TabsContent value="incoming">
          <RfqTable rfqs={rfqs} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
