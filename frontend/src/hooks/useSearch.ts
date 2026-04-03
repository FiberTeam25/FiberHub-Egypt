"use client";

import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";

export function useSearch(params: Record<string, string | number | boolean>) {
  return useQuery({
    queryKey: ["search", params],
    queryFn: async () => {
      const res = await api.get("/search", { params });
      return res.data;
    },
    enabled: !!params.q || !!params.company_type,
  });
}

export function useSearchCompanies(params: Record<string, string | number | boolean>) {
  return useQuery({
    queryKey: ["searchCompanies", params],
    queryFn: async () => {
      const res = await api.get("/search/companies", { params });
      return res.data;
    },
    enabled: Object.keys(params).length > 0,
  });
}

export function useCategories() {
  return useQuery({
    queryKey: ["categories"],
    queryFn: async () => {
      const [products, services, governorates] = await Promise.all([
        api.get("/categories/products"),
        api.get("/categories/services"),
        api.get("/categories/governorates"),
      ]);
      return {
        products: products.data,
        services: services.data,
        governorates: governorates.data,
      };
    },
    staleTime: 10 * 60 * 1000,
  });
}
