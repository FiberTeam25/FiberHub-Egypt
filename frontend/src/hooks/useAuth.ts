"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import api from "@/lib/api";
import { useAuthStore } from "@/store/auth";
import { login as loginFn, register as registerFn, logout as logoutFn } from "@/lib/auth";

export function useCurrentUser() {
  const { setUser } = useAuthStore();

  return useQuery({
    queryKey: ["currentUser"],
    queryFn: async () => {
      const res = await api.get("/auth/me");
      setUser(res.data);
      return res.data;
    },
    retry: false,
    staleTime: 5 * 60 * 1000,
  });
}

export function useLogin() {
  const queryClient = useQueryClient();
  const router = useRouter();

  return useMutation({
    mutationFn: ({ email, password }: { email: string; password: string }) =>
      loginFn(email, password),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["currentUser"] });
      router.push("/dashboard");
    },
  });
}

export function useRegister() {
  const router = useRouter();

  return useMutation({
    mutationFn: (data: {
      email: string;
      password: string;
      first_name: string;
      last_name: string;
      phone?: string;
      account_type: string;
    }) => registerFn(data),
    onSuccess: () => {
      router.push("/login?registered=true");
    },
  });
}

export function useLogout() {
  const queryClient = useQueryClient();
  const { setUser } = useAuthStore();

  return () => {
    setUser(null);
    queryClient.clear();
    logoutFn();
  };
}
