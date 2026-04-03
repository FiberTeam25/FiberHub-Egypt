"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import api from "@/lib/api";
import { useTranslation } from "@/store/language";
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
  const t = useTranslation();

  const fetchShortlist = useCallback(async () => {
    try {
      const res = await api.get("/shortlist");
      setItems(res.data.items ?? res.data);
    } catch {
      setError(t("shortlist.loadFailed"));
    } finally {
      setLoading(false);
    }
  }, [t]);

  useEffect(() => {
    fetchShortlist();
  }, [fetchShortlist]);

  const handleRemove = async (id: string) => {
    try {
      await api.delete(`/shortlist/${id}`);
      setItems((prev) => prev.filter((item) => item.id !== id));
    } catch {
      setError(t("shortlist.removeFailed"));
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
      <h1 className="text-2xl font-bold">{t("shortlist.title")}</h1>

      {items.length === 0 ? (
        <Card>
          <CardContent className="pt-6 text-center">
            <p className="text-muted-foreground">
              {t("shortlist.empty")}
            </p>
            <Button className="mt-4" variant="outline" render={<Link href="/search" />}>
              {t("shortlist.searchCompanies")}
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
                      {item.company?.name ?? item.profile_name ?? t("common.unknown")}
                    </CardTitle>
                    <CardDescription className="truncate">
                      {item.company
                        ? item.company.company_type
                        : item.profile_headline ?? t("common.individual")}
                    </CardDescription>
                  </div>
                  {item.company?.verification_status === "approved" && (
                    <Badge variant="default" className="ml-2 shrink-0">
                      {t("shortlist.verified")}
                    </Badge>
                  )}
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                {item.company && (
                  <div className="text-sm text-muted-foreground">
                    {[item.company.city, item.company.governorate]
                      .filter(Boolean)
                      .join(", ") || t("shortlist.locationNotSpecified")}
                  </div>
                )}
                <p className="text-xs text-muted-foreground">
                  {t("shortlist.savedOn")}{" "}
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
                    {t("shortlist.view")}
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-destructive hover:text-destructive"
                    onClick={() => handleRemove(item.id)}
                  >
                    {t("shortlist.remove")}
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
