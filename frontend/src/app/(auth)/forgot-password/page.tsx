"use client";

import { Suspense, useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import api from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";

const requestSchema = z.object({
  email: z.string().email("Invalid email"),
});

const resetSchema = z.object({
  new_password: z.string().min(8, "Password must be at least 8 characters"),
  confirm_password: z.string(),
}).refine((d) => d.new_password === d.confirm_password, {
  message: "Passwords do not match",
  path: ["confirm_password"],
});

function ForgotPasswordPageContent() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token");

  if (token) {
    return <ResetForm token={token} />;
  }
  return <RequestForm />;
}

function RequestForm() {
  const [sent, setSent] = useState(false);
  const [loading, setLoading] = useState(false);
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(requestSchema),
  });

  const onSubmit = async (data: { email: string }) => {
    setLoading(true);
    try {
      await api.post("/auth/forgot-password", data);
      setSent(true);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-muted/30 px-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle>Forgot Password</CardTitle>
          <CardDescription>Enter your email to receive a reset link</CardDescription>
        </CardHeader>
        {sent ? (
          <CardContent>
            <div className="rounded-lg bg-green-50 border border-green-200 p-4 text-sm text-green-800 text-center">
              If an account exists with that email, a reset link has been sent.
            </div>
          </CardContent>
        ) : (
          <form onSubmit={handleSubmit(onSubmit)}>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input id="email" type="email" {...register("email")} />
                {errors.email && <p className="text-xs text-red-500">{errors.email.message as string}</p>}
              </div>
            </CardContent>
            <CardFooter className="flex flex-col gap-4">
              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? "Sending..." : "Send Reset Link"}
              </Button>
              <Link href="/login" className="text-sm text-muted-foreground hover:text-foreground">
                Back to login
              </Link>
            </CardFooter>
          </form>
        )}
      </Card>
    </div>
  );
}

function ResetForm({ token }: { token: string }) {
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(resetSchema),
  });

  const onSubmit = async (data: { new_password: string }) => {
    setLoading(true);
    setError("");
    try {
      await api.post("/auth/reset-password", { token, new_password: data.new_password });
      setSuccess(true);
    } catch (err: unknown) {
      setError((err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || "Reset failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-muted/30 px-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle>Reset Password</CardTitle>
          <CardDescription>Enter your new password</CardDescription>
        </CardHeader>
        {success ? (
          <CardContent className="text-center space-y-4">
            <div className="rounded-lg bg-green-50 border border-green-200 p-4 text-sm text-green-800">
              Password reset successfully!
            </div>
            <Button render={<Link href="/login" />}>Sign In</Button>
          </CardContent>
        ) : (
          <form onSubmit={handleSubmit(onSubmit)}>
            <CardContent className="space-y-4">
              {error && (
                <div className="rounded-lg bg-red-50 border border-red-200 p-3 text-sm text-red-800">{error}</div>
              )}
              <div className="space-y-2">
                <Label htmlFor="new_password">New Password</Label>
                <Input id="new_password" type="password" {...register("new_password")} />
                {errors.new_password && <p className="text-xs text-red-500">{errors.new_password.message as string}</p>}
              </div>
              <div className="space-y-2">
                <Label htmlFor="confirm_password">Confirm Password</Label>
                <Input id="confirm_password" type="password" {...register("confirm_password")} />
                {errors.confirm_password && <p className="text-xs text-red-500">{errors.confirm_password.message as string}</p>}
              </div>
            </CardContent>
            <CardFooter>
              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? "Resetting..." : "Reset Password"}
              </Button>
            </CardFooter>
          </form>
        )}
      </Card>
    </div>
  );
}

export default function ForgotPasswordPage() { return <Suspense><ForgotPasswordPageContent /></Suspense>; }
