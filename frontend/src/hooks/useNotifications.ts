"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";

export function useNotifications(page = 1) {
  return useQuery({
    queryKey: ["notifications", page],
    queryFn: async () => {
      const res = await api.get("/notifications", { params: { page } });
      return res.data;
    },
  });
}

export function useUnreadCount() {
  return useQuery({
    queryKey: ["unreadCount"],
    queryFn: async () => {
      const res = await api.get("/notifications/unread-count");
      return res.data.unread_count as number;
    },
    refetchInterval: 30000,
  });
}

export function useMarkNotificationRead() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await api.post(`/notifications/${id}/read`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
      queryClient.invalidateQueries({ queryKey: ["unreadCount"] });
    },
  });
}

export function useMarkAllRead() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      await api.post("/notifications/read-all");
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
      queryClient.invalidateQueries({ queryKey: ["unreadCount"] });
    },
  });
}
