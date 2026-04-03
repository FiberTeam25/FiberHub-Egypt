"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { VerificationBadge } from "@/components/ui/VerificationBadge";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { UserCircle, MapPin, Clock, Loader2 } from "lucide-react";
import api from "@/lib/api";

export default function ProfessionalProfilePage() {
  const params = useParams();
  const slug = params.slug as string;
  const { data: profile, isLoading } = useQuery({
    queryKey: ["profile", slug],
    queryFn: async () => { const res = await api.get("/profiles/" + slug); return res.data; },
    enabled: !!slug,
  });

  if (isLoading) return (<div className="min-h-screen flex flex-col"><Header /><div className="flex-1 flex items-center justify-center"><Loader2 className="h-6 w-6 animate-spin" /></div></div>);
  if (!profile) return (<div className="min-h-screen flex flex-col"><Header /><div className="flex-1 flex items-center justify-center text-muted-foreground">Profile not found</div><Footer /></div>);

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1">
        <div className="mx-auto max-w-3xl px-4 py-8">
          <Card><CardContent className="pt-6">
            <div className="flex items-start gap-4 mb-6">
              <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-full bg-muted"><UserCircle className="h-8 w-8 text-muted-foreground" /></div>
              <div>
                <div className="flex items-center gap-2 flex-wrap">
                  <h1 className="text-xl font-bold">{profile.first_name} {profile.last_name}</h1>
                  <VerificationBadge status={profile.verification_status} />
                </div>
                {profile.headline && <p className="text-muted-foreground mt-1">{profile.headline}</p>}
                <div className="flex items-center gap-4 mt-2 text-sm text-muted-foreground flex-wrap">
                  {profile.governorate && <span className="flex items-center gap-1"><MapPin className="h-3 w-3" />{profile.governorate}</span>}
                  {profile.experience_years && <span>{profile.experience_years} years experience</span>}
                  {profile.availability && <span className="flex items-center gap-1"><Clock className="h-3 w-3" />{profile.availability}</span>}
                </div>
              </div>
            </div>
            {profile.bio && (<div className="mb-6"><h2 className="font-semibold mb-2">About</h2><p className="text-sm text-muted-foreground whitespace-pre-wrap">{profile.bio}</p></div>)}
            {profile.specializations?.length > 0 && (<div className="mb-6"><h2 className="font-semibold mb-2">Specializations</h2><div className="flex flex-wrap gap-2">{profile.specializations.map((s: string) => (<Badge key={s} variant="secondary">{s}</Badge>))}</div></div>)}
            {profile.hourly_rate_egp && (<div><h2 className="font-semibold mb-1">Rate</h2><p className="text-sm text-muted-foreground">{profile.hourly_rate_egp} EGP/hour</p></div>)}
          </CardContent></Card>
        </div>
      </main>
      <Footer />
    </div>
  );
}
