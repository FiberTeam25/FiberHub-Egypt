"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import api from "@/lib/api";
import type { Company } from "@/types/company";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface ShortlistItem {
  id: string;
  company_id: string | null;
  profile_id: string | null;
  company?: Company;
  profile_name?: string;
  profile_headline?: string;
  created_at: string;
}

export default function ShortlistPage() {
  const [items, setItems] = useState<ShortlistItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchShortlist = useCallback(async () => {
    try {
      const res = await api.get("/shortlist");
      setItems(res.data.items ?? res.data);
    } catch {
      setError("Failed to load shortlist.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchShortlist();
  }, [fetchShortlist]);

  const handleRemove = async (id: string) => {
    try {
      await api.delete(`/shortlist/${id}`);
      setItems((prev) => prev.filter((item) => item.id !== id));
    } catch {
      setError("Failed to remove item.");
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  if (error && items.length === 0) {
    return (
      <div className="py-20 text-center">
        <p className="text-destructive">{error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Shortlist</h1>

      {items.length === 0 ? (
        <Card>
          <CardContent className="pt-6 text-center">
            <p className="text-muted-foreground">
              Your shortlist is empty. Browse companies and profiles to save
              them here.
            </p>
            <Button className="mt-4" variant="outline" render={<Link href="/search" />}>
              Search Companies
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {items.map((item) => (
            <Card key={item.id}>
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="min-w-0 flex-1">
                    <CardTitle className="text-base truncate">
                      {item.company?.name ?? item.profile_name ?? "Unknown"}
                    </CardTitle>
                    <CardDescription className="truncate">
                      {item.company
                        ? item.company.company_type
                        : item.profile_headline ?? "Individual"}
                    </CardDescription>
                  </div>
                  {item.company?.verification_status === "approved" && (
                    <Badge variant="default" className="ml-2 shrink-0">
                      Verified
                    </Badge>
                  )}
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                {item.company && (
                  <div className="text-sm text-muted-foreground">
                    {[item.company.city, item.company.governorate]
                      .filter(Boolean)
                      .join(", ") || "Location not specified"}
                  </div>
                )}
                <p className="text-xs text-muted-foreground">
                  Saved on{" "}
                  {new Date(item.created_at).toLocaleDateString()}
                </p>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    render={
                      <Link
                        href={
                          item.company
                            ? `/companies/${item.company.slug}`
                            : `/profiles/${item.profile_id}`
                        }
                      />
                    }
                  >
                    View
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-destructive hover:text-destructive"
                    onClick={() => handleRemove(item.id)}
                  >
                    Remove
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
