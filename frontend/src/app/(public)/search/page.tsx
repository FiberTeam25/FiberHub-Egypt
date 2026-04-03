"use client";

import { useState } from "react";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { CompanyCard } from "@/components/company/CompanyCard";
import type { Company } from "@/types/company";
import { FilterPanel } from "@/components/search/FilterPanel";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useSearchCompanies, useCategories } from "@/hooks/useSearch";
import { Search, Loader2 } from "lucide-react";

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [filters, setFilters] = useState<Record<string, string | boolean | undefined>>({});
  const [page, setPage] = useState(1);

  const params: Record<string, string | number | boolean> = { page, page_size: 12 };
  if (query) params.search = query;
  if (filters.company_type) params.company_type = filters.company_type as string;
  if (filters.governorate) params.governorate = filters.governorate as string;
  if (filters.verified_only) params.verified_only = true;

  const { data, isLoading } = useSearchCompanies(params);
  const { data: categories } = useCategories();

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1">
        <div className="mx-auto max-w-7xl px-4 py-8">
          <div className="mb-8">
            <h1 className="text-2xl font-bold mb-4">Search Companies</h1>
            <div className="flex gap-2 max-w-xl">
              <Input
                placeholder="Search by name, service, or product..."
                value={query}
                onChange={(e) => { setQuery(e.target.value); setPage(1); }}
              />
              <Button><Search className="h-4 w-4" /></Button>
            </div>
          </div>

          <div className="flex gap-8">
            <aside className="w-64 shrink-0 hidden md:block">
              <FilterPanel
                filters={filters}
                governorates={categories?.governorates || []}
                onFilterChange={(f) => { setFilters(f); setPage(1); }}
              />
            </aside>

            <div className="flex-1">
              {isLoading ? (
                <div className="flex justify-center py-12">
                  <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
                </div>
              ) : data?.items?.length ? (
                <>
                  <p className="text-sm text-muted-foreground mb-4">{data.total} results found</p>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {data.items.map((company: Company) => (
                      <CompanyCard key={company.id} company={company} />
                    ))}
                  </div>
                  {data.total > 12 && (
                    <div className="flex justify-center gap-2 mt-8">
                      <Button variant="outline" size="sm" disabled={page === 1} onClick={() => setPage(page - 1)}>Previous</Button>
                      <span className="flex items-center text-sm text-muted-foreground px-3">Page {page} of {Math.ceil(data.total / 12)}</span>
                      <Button variant="outline" size="sm" disabled={page * 12 >= data.total} onClick={() => setPage(page + 1)}>Next</Button>
                    </div>
                  )}
                </>
              ) : (
                <div className="text-center py-12 text-muted-foreground">
                  <p>No companies found. Try adjusting your filters.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}
