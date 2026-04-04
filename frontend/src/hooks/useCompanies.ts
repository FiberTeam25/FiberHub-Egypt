"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";
import type { Company } from "@/types/company";
import type { PaginatedResponse } from "@/types/api";

export function useCompanies(params?: Record<string, string | number | boolean>) {
  return useQuery({
    queryKey: ["companies", params],
    queryFn: async () => {
      const res = await api.get<PaginatedResponse<Company>>("/companies", { params });
      return res.data;
    },
  });
}

export function useMyCompany() {
  return useQuery({
    queryKey: ["myCompany"],
    queryFn: async () => {
      const res = await api.get<Company | null>("/companies/mine");
      return res.data;
    },
  });
}

export function useCompany(slug: string) {
  return useQuery({
    queryKey: ["company", slug],
    queryFn: async () => {
      const res = await api.get<Company>(`/companies/${slug}`);
      return res.data;
    },
    enabled: !!slug,
  });
}

export function useCreateCompany() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: Record<string, unknown>) => {
      const res = await api.post("/companies", data);
      return res.data;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["companies"] }),
  });
}

export function useUpdateCompany() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Record<string, unknown> }) => {
      const res = await api.patch(`/companies/${id}`, data);
      return res.data;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["companies"] }),
  });
}
