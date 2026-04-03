"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Loader2, Plus } from "lucide-react";

function CategoryTable({ type }: { type: "products" | "services" }) {
  const queryClient = useQueryClient();
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ name: "", description: "" });

  const { data, isLoading } = useQuery({
    queryKey: ["categories", type],
    queryFn: async () => { const res = await api.get("/categories/" + type); return res.data; },
  });

  const create = useMutation({
    mutationFn: async (data: { name: string; description: string }) => api.post("/categories/" + type, data),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["categories", type] }); setOpen(false); setForm({ name: "", description: "" }); },
  });

  const items = Array.isArray(data) ? data : data?.items || [];

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <p className="text-sm text-muted-foreground">{items.length} categories</p>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger render={<Button size="sm" />}><Plus className="h-4 w-4 mr-2" />Add Category</DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Add {type === "products" ? "Product" : "Service"} Category</DialogTitle></DialogHeader>
            <div className="space-y-4">
              <div><Label>Name</Label><Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></div>
              <div><Label>Description</Label><Textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} /></div>
              <Button onClick={() => create.mutate(form)} disabled={create.isPending || !form.name}>{create.isPending ? "Creating..." : "Create"}</Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>
      {isLoading ? <div className="flex justify-center py-8"><Loader2 className="h-5 w-5 animate-spin" /></div> : (
        <Table>
          <TableHeader><TableRow><TableHead>Name</TableHead><TableHead>Slug</TableHead><TableHead>Active</TableHead></TableRow></TableHeader>
          <TableBody>
            {items.map((c: { id: string; name: string; slug: string; is_active: boolean }) => (
              <TableRow key={c.id}>
                <TableCell className="font-medium text-sm">{c.name}</TableCell>
                <TableCell className="text-sm text-muted-foreground">{c.slug}</TableCell>
                <TableCell className="text-sm">{c.is_active ? "Yes" : "No"}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
    </div>
  );
}

export default function AdminCategoriesPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Category Management</h1>
      <Tabs defaultValue="products">
        <TabsList><TabsTrigger value="products">Product Categories</TabsTrigger><TabsTrigger value="services">Service Categories</TabsTrigger></TabsList>
        <TabsContent value="products" className="mt-4"><CategoryTable type="products" /></TabsContent>
        <TabsContent value="services" className="mt-4"><CategoryTable type="services" /></TabsContent>
      </Tabs>
    </div>
  );
}
