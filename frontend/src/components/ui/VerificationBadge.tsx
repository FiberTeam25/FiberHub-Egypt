"use client";

import { ShieldCheck } from "lucide-react";
import { Badge } from "@/components/ui/badge";

export function VerificationBadge({ status }: { status: string }) {
  if (status !== "approved") return null;
  return (
    <Badge variant="secondary" className="gap-1 text-blue-700 bg-blue-50 border-blue-200">
      <ShieldCheck className="h-3 w-3" />
      Verified
    </Badge>
  );
}
