"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";

export function useRfqs(params?: Record<string, string | number>) {
  return useQuery({
    queryKey: ["rfqs", params],
    queryFn: async () => {
      const res = await api.get("/rfqs", { params });
      return res.data;
    },
    enabled: params !== undefined,
  });
}

export function useRfq(id: string) {
  return useQuery({
    queryKey: ["rfq", id],
    queryFn: async () => {
      const res = await api.get(`/rfqs/${id}`);
      return res.data;
    },
    enabled: !!id,
  });
}

export function useCreateRfq() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: Record<string, unknown>) => {
      const res = await api.post("/rfqs", data);
      return res.data;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["rfqs"] }),
  });
}

export function usePublishRfq() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const res = await api.post(`/rfqs/${id}/publish`);
      return res.data;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["rfqs"] }),
  });
}

export function useInviteCompanies() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ rfqId, companyIds }: { rfqId: string; companyIds: string[] }) => {
      const res = await api.post(`/rfqs/${rfqId}/invite`, { company_ids: companyIds });
      return res.data;
    },
    onSuccess: (_, vars) => queryClient.invalidateQueries({ queryKey: ["rfq", vars.rfqId] }),
  });
}

export function useSubmitResponse() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ rfqId, data }: { rfqId: string; data: Record<string, unknown> }) => {
      const res = await api.post(`/rfqs/${rfqId}/responses`, data);
      return res.data;
    },
    onSuccess: (_, vars) => queryClient.invalidateQueries({ queryKey: ["rfq", vars.rfqId] }),
  });
}

export function useRfqResponses(rfqId: string) {
  return useQuery({
    queryKey: ["rfqResponses", rfqId],
    queryFn: async () => {
      const res = await api.get(`/rfqs/${rfqId}/responses`);
      return res.data;
    },
    enabled: !!rfqId,
  });
}
