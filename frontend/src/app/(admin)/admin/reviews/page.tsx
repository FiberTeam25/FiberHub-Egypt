"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Loader2, EyeOff, Star } from "lucide-react";

export default function AdminReviewsPage() {
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ["adminFlaggedReviews"],
    queryFn: async () => {
      try { const res = await api.get("/admin/flagged-reviews"); return res.data; }
      catch { return { items: [] }; }
    },
  });

  const hide = useMutation({
    mutationFn: async (id: string) => api.post("/reviews/" + id + "/hide"),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["adminFlaggedReviews"] }),
  });

  const items = data?.items || [];

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Review Moderation</h1>
      {isLoading ? <div className="flex justify-center py-8"><Loader2 className="h-5 w-5 animate-spin" /></div> : items.length === 0 ? (
        <div className="text-center py-12 text-muted-foreground"><Star className="h-8 w-8 mx-auto mb-2" /><p>No flagged reviews</p></div>
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Reviewer</TableHead>
              <TableHead>Rating</TableHead>
              <TableHead>Comment</TableHead>
              <TableHead>Flags</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {items.map((r: { id: string; reviewer_name: string; overall_rating: number; comment: string; flags?: unknown[] }) => (
              <TableRow key={r.id}>
                <TableCell className="text-sm">{r.reviewer_name || "Anonymous"}</TableCell>
                <TableCell><Badge variant="outline">{r.overall_rating}/5</Badge></TableCell>
                <TableCell className="text-sm max-w-xs truncate">{r.comment || "-"}</TableCell>
                <TableCell><Badge variant="destructive">{r.flags?.length || 0}</Badge></TableCell>
                <TableCell>
                  <Button size="sm" variant="destructive" onClick={() => hide.mutate(r.id)} disabled={hide.isPending}>
                    <EyeOff className="h-3 w-3 mr-1" />Hide
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
    </div>
  );
}
