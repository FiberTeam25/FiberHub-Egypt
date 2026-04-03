"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Loader2 } from "lucide-react";

export default function AdminUsersPage() {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);

  const { data, isLoading } = useQuery({
    queryKey: ["adminUsers", search, page],
    queryFn: async () => { const res = await api.get("/admin/users", { params: { search: search || undefined, page, page_size: 20 } }); return res.data; },
  });

  const suspend = useMutation({
    mutationFn: async (id: string) => api.post("/admin/users/" + id + "/suspend"),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["adminUsers"] }),
  });

  const activate = useMutation({
    mutationFn: async (id: string) => api.post("/admin/users/" + id + "/activate"),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["adminUsers"] }),
  });

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">User Management</h1>
      <div className="mb-4 max-w-sm">
        <Input placeholder="Search users..." value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }} />
      </div>
      {isLoading ? <div className="flex justify-center py-8"><Loader2 className="h-5 w-5 animate-spin" /></div> : (
        <>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Email</TableHead>
                <TableHead>Name</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Verified</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data?.items?.map((u: { id: string; email: string; first_name: string; last_name: string; account_type: string; status: string; email_verified: boolean }) => (
                <TableRow key={u.id}>
                  <TableCell className="text-sm">{u.email}</TableCell>
                  <TableCell className="text-sm">{u.first_name} {u.last_name}</TableCell>
                  <TableCell><Badge variant="outline" className="text-xs capitalize">{u.account_type}</Badge></TableCell>
                  <TableCell><Badge variant={u.status === "active" ? "secondary" : "destructive"} className="text-xs">{u.status}</Badge></TableCell>
                  <TableCell className="text-sm">{u.email_verified ? "Yes" : "No"}</TableCell>
                  <TableCell>
                    {u.status === "active" ? (
                      <Button size="sm" variant="destructive" onClick={() => suspend.mutate(u.id)}>Suspend</Button>
                    ) : (
                      <Button size="sm" variant="outline" onClick={() => activate.mutate(u.id)}>Activate</Button>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          {data?.total > 20 && (
            <div className="flex justify-center gap-2 mt-4">
              <Button variant="outline" size="sm" disabled={page === 1} onClick={() => setPage(page - 1)}>Prev</Button>
              <span className="text-sm text-muted-foreground py-2">Page {page}</span>
              <Button variant="outline" size="sm" disabled={page * 20 >= data.total} onClick={() => setPage(page + 1)}>Next</Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
