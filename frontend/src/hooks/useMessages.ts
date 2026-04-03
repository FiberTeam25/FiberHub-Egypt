"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";

export function useThreads() {
  return useQuery({
    queryKey: ["threads"],
    queryFn: async () => {
      const res = await api.get("/messages/threads");
      return res.data;
    },
    refetchInterval: 30000,
  });
}

export function useThread(threadId: string) {
  return useQuery({
    queryKey: ["thread", threadId],
    queryFn: async () => {
      const res = await api.get(`/messages/threads/${threadId}`);
      return res.data;
    },
    enabled: !!threadId,
    refetchInterval: 10000,
  });
}

export function useCreateThread() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: {
      context_type: string;
      context_id?: string;
      subject?: string;
      participant_user_ids: string[];
      initial_message: string;
    }) => {
      const res = await api.post("/messages/threads", data);
      return res.data;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["threads"] }),
  });
}

export function useSendMessage() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ threadId, content }: { threadId: string; content: string }) => {
      const res = await api.post(`/messages/threads/${threadId}/messages`, { content });
      return res.data;
    },
    onSuccess: (_, vars) => {
      queryClient.invalidateQueries({ queryKey: ["thread", vars.threadId] });
      queryClient.invalidateQueries({ queryKey: ["threads"] });
    },
  });
}

export function useMarkRead() {
  return useMutation({
    mutationFn: async (threadId: string) => {
      await api.post(`/messages/threads/${threadId}/read`);
    },
  });
}
