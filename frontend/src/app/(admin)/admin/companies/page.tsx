"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Loader2 } from "lucide-react";
import Link from "next/link";

export default function AdminCompaniesPage() {
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);

  const { data, isLoading } = useQuery({
    queryKey: ["adminCompanies", search, page],
    queryFn: async () => { const res = await api.get("/admin/companies", { params: { search: search || undefined, page, page_size: 20 } }); return res.data; },
  });

  const statusColor = (s: string) => {
    if (s === "approved") return "secondary";
    if (s === "pending") return "outline";
    if (s === "rejected") return "destructive";
    return "outline";
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Company Management</h1>
      <div className="mb-4 max-w-sm">
        <Input placeholder="Search companies..." value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }} />
      </div>
      {isLoading ? <div className="flex justify-center py-8"><Loader2 className="h-5 w-5 animate-spin" /></div> : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Verification</TableHead>
              <TableHead>Governorate</TableHead>
              <TableHead>Active</TableHead>
              <TableHead>View</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data?.items?.map((c: { id: string; name: string; slug: string; company_type: string; verification_status: string; governorate: string; is_active: boolean }) => (
              <TableRow key={c.id}>
                <TableCell className="font-medium text-sm">{c.name}</TableCell>
                <TableCell><Badge variant="outline" className="text-xs capitalize">{c.company_type}</Badge></TableCell>
                <TableCell><Badge variant={statusColor(c.verification_status)} className="text-xs capitalize">{c.verification_status}</Badge></TableCell>
                <TableCell className="text-sm">{c.governorate || "-"}</TableCell>
                <TableCell className="text-sm">{c.is_active ? "Yes" : "No"}</TableCell>
                <TableCell><Link href={"/companies/" + c.slug} className="text-blue-600 text-sm hover:underline">View</Link></TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
    </div>
  );
}
