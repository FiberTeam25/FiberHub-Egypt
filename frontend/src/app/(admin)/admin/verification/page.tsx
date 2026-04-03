"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Loader2, Check, X } from "lucide-react";

export default function AdminVerificationPage() {
  const queryClient = useQueryClient();
  const [page] = useState(1);
  const [reviewDialog, setReviewDialog] = useState<{ id: string; company_id?: string; status: string } | null>(null);
  const [notes, setNotes] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["verificationQueue", page],
    queryFn: async () => { const res = await api.get("/verification/queue", { params: { page, page_size: 20 } }); return res.data; },
  });

  const approve = useMutation({
    mutationFn: async ({ id, notes }: { id: string; notes: string }) => api.post("/verification/" + id + "/approve", { admin_notes: notes || null }),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["verificationQueue"] }); setReviewDialog(null); setNotes(""); },
  });

  const reject = useMutation({
    mutationFn: async ({ id, notes }: { id: string; notes: string }) => api.post("/verification/" + id + "/reject", { admin_notes: notes || null }),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["verificationQueue"] }); setReviewDialog(null); setNotes(""); },
  });

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Verification Queue</h1>
      {isLoading ? <div className="flex justify-center py-8"><Loader2 className="h-5 w-5 animate-spin" /></div> : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>ID</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Submitted</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data?.items?.map((r: { id: string; company_id?: string; status: string; created_at: string }) => (
              <TableRow key={r.id}>
                <TableCell className="text-sm font-mono">{r.id.slice(0, 8)}...</TableCell>
                <TableCell className="text-sm">{r.company_id ? "Company" : "Profile"}</TableCell>
                <TableCell><Badge variant="outline" className="text-xs capitalize">{r.status}</Badge></TableCell>
                <TableCell className="text-sm">{new Date(r.created_at).toLocaleDateString()}</TableCell>
                <TableCell className="flex gap-2">
                  <Button size="sm" variant="outline" className="text-green-600" onClick={() => { setReviewDialog(r); setNotes(""); }}><Check className="h-3 w-3 mr-1" />Review</Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}

      <Dialog open={!!reviewDialog} onOpenChange={() => setReviewDialog(null)}>
        <DialogContent>
          <DialogHeader><DialogTitle>Review Verification Request</DialogTitle></DialogHeader>
          <div className="space-y-4">
            <div><label className="text-sm font-medium">Admin Notes</label><Textarea value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="Optional notes..." /></div>
            <div className="flex gap-2">
              <Button onClick={() => approve.mutate({ id: reviewDialog!.id, notes })} disabled={approve.isPending} className="bg-green-600 hover:bg-green-700"><Check className="h-4 w-4 mr-2" />Approve</Button>
              <Button variant="destructive" onClick={() => reject.mutate({ id: reviewDialog!.id, notes })} disabled={reject.isPending}><X className="h-4 w-4 mr-2" />Reject</Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
