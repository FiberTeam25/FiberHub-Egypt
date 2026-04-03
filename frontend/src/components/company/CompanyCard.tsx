"use client";

import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { VerificationBadge } from "@/components/ui/VerificationBadge";
import { Building2, MapPin } from "lucide-react";
import type { Company } from "@/types/company";

export function CompanyCard({ company }: { company: Company }) {
  return (
    <Link href={`/companies/${company.slug}`}>
      <Card className="hover:shadow-md transition-shadow h-full">
        <CardContent className="pt-6">
          <div className="flex items-start gap-3 mb-3">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-muted">
              <Building2 className="h-5 w-5 text-muted-foreground" />
            </div>
            <div className="min-w-0 flex-1">
              <h3 className="font-semibold truncate">{company.name}</h3>
              <div className="flex items-center gap-2 mt-1 flex-wrap">
                <Badge variant="outline" className="text-xs capitalize">{company.company_type}</Badge>
                <VerificationBadge status={company.verification_status} />
              </div>
            </div>
          </div>
          {company.description && (
            <p className="text-sm text-muted-foreground line-clamp-2 mb-3">{company.description}</p>
          )}
          {company.governorate && (
            <div className="flex items-center gap-1 text-xs text-muted-foreground">
              <MapPin className="h-3 w-3" />
              {company.governorate}{company.city && `, ${company.city}`}
            </div>
          )}
        </CardContent>
      </Card>
    </Link>
  );
}
