"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import api from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { CheckCircle, XCircle, Loader2 } from "lucide-react";

function VerifyEmailPageContent() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token");
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (!token) {
      setStatus("error");
      setMessage("No verification token provided.");
      return;
    }
    api
      .post("/auth/verify-email", { token })
      .then(() => {
        setStatus("success");
        setMessage("Your email has been verified successfully!");
      })
      .catch((err) => {
        setStatus("error");
        setMessage(err.response?.data?.detail || "Verification failed. Token may be expired.");
      });
  }, [token]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-muted/30 px-4">
      <Card className="w-full max-w-md text-center">
        <CardHeader>
          <CardTitle>Email Verification</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {status === "loading" && (
            <div className="flex flex-col items-center gap-2">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
              <p className="text-muted-foreground">Verifying your email...</p>
            </div>
          )}
          {status === "success" && (
            <div className="flex flex-col items-center gap-2">
              <CheckCircle className="h-8 w-8 text-green-600" />
              <p>{message}</p>
              <Button render={<Link href="/login" />} className="mt-4">Sign In</Button>
            </div>
          )}
          {status === "error" && (
            <div className="flex flex-col items-center gap-2">
              <XCircle className="h-8 w-8 text-red-600" />
              <p className="text-red-600">{message}</p>
              <Button variant="outline" render={<Link href="/login" />} className="mt-4">Go to Login</Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

export default function VerifyEmailPage() {
  return <Suspense><VerifyEmailPageContent /></Suspense>;
}
