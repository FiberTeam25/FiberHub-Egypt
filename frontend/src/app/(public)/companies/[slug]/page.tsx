"use client";

import { useParams } from "next/navigation";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { useCompany } from "@/hooks/useCompanies";
import { VerificationBadge } from "@/components/ui/VerificationBadge";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import { Building2, MapPin, Globe, Mail, Phone, Calendar, Loader2 } from "lucide-react";

export default function CompanyProfilePage() {
  const params = useParams();
  const slug = params.slug as string;
  const { data: company, isLoading, error } = useCompany(slug);

  if (isLoading) return (<div className="min-h-screen flex flex-col"><Header /><div className="flex-1 flex items-center justify-center"><Loader2 className="h-6 w-6 animate-spin" /></div></div>);
  if (error || !company) return (<div className="min-h-screen flex flex-col"><Header /><div className="flex-1 flex items-center justify-center text-muted-foreground">Company not found</div><Footer /></div>);

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1">
        <div className="bg-muted/30 py-8">
          <div className="mx-auto max-w-7xl px-4">
            <div className="flex items-start gap-4">
              <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-xl bg-muted"><Building2 className="h-8 w-8 text-muted-foreground" /></div>
              <div>
                <div className="flex items-center gap-3 flex-wrap">
                  <h1 className="text-2xl font-bold">{company.name}</h1>
                  <Badge variant="outline" className="capitalize">{company.company_type}</Badge>
                  <VerificationBadge status={company.verification_status} />
                </div>
                <div className="flex items-center gap-4 mt-2 text-sm text-muted-foreground flex-wrap">
                  {company.governorate && <span className="flex items-center gap-1"><MapPin className="h-3 w-3" />{company.governorate}</span>}
                  {company.year_established && <span className="flex items-center gap-1"><Calendar className="h-3 w-3" />Est. {company.year_established}</span>}
                  {company.company_size && <span>Size: {company.company_size}</span>}
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className="mx-auto max-w-7xl px-4 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2">
              <Tabs defaultValue="overview">
                <TabsList>
                  <TabsTrigger value="overview">Overview</TabsTrigger>
                  <TabsTrigger value="services">Services</TabsTrigger>
                  <TabsTrigger value="products">Products</TabsTrigger>
                  <TabsTrigger value="certs">Certifications</TabsTrigger>
                  <TabsTrigger value="refs">References</TabsTrigger>
                </TabsList>
                <TabsContent value="overview" className="mt-4"><Card><CardContent className="pt-6"><p className="text-sm text-muted-foreground whitespace-pre-wrap">{company.description || "No description provided."}</p></CardContent></Card></TabsContent>
                <TabsContent value="services" className="mt-4"><Card><CardContent className="pt-6">{company.services?.length ? company.services.map((s: { id: string; category_name?: string }) => (<div key={s.id} className="border-b pb-3 mb-3 last:border-0"><p className="font-medium text-sm">{s.category_name || "Service"}</p></div>)) : <p className="text-sm text-muted-foreground">No services listed.</p>}</CardContent></Card></TabsContent>
                <TabsContent value="products" className="mt-4"><Card><CardContent className="pt-6">{company.products?.length ? company.products.map((p: { id: string; category_name?: string }) => (<div key={p.id} className="border-b pb-3 mb-3 last:border-0"><p className="font-medium text-sm">{p.category_name || "Product"}</p></div>)) : <p className="text-sm text-muted-foreground">No products listed.</p>}</CardContent></Card></TabsContent>
                <TabsContent value="certs" className="mt-4"><Card><CardContent className="pt-6">{company.certifications?.length ? company.certifications.map((c: { id: string; name: string }) => (<div key={c.id} className="border-b pb-3 mb-3 last:border-0"><p className="font-medium text-sm">{c.name}</p></div>)) : <p className="text-sm text-muted-foreground">No certifications.</p>}</CardContent></Card></TabsContent>
                <TabsContent value="refs" className="mt-4"><Card><CardContent className="pt-6">{company.references?.length ? company.references.map((r: { id: string; project_name: string }) => (<div key={r.id} className="border-b pb-3 mb-3 last:border-0"><p className="font-medium text-sm">{r.project_name}</p></div>)) : <p className="text-sm text-muted-foreground">No references.</p>}</CardContent></Card></TabsContent>
              </Tabs>
            </div>
            <div>
              <Card>
                <CardHeader><CardTitle className="text-base">Contact Info</CardTitle></CardHeader>
                <CardContent className="space-y-3 text-sm">
                  {company.email && <div className="flex items-center gap-2"><Mail className="h-4 w-4 text-muted-foreground" />{company.email}</div>}
                  {company.phone && <div className="flex items-center gap-2"><Phone className="h-4 w-4 text-muted-foreground" />{company.phone}</div>}
                  {company.website && <div className="flex items-center gap-2"><Globe className="h-4 w-4 text-muted-foreground" />{company.website}</div>}
                  <Separator />
                  <div>
                    <p className="text-xs text-muted-foreground mb-1">Profile Completion</p>
                    <div className="w-full bg-muted rounded-full h-2"><div className="bg-primary h-2 rounded-full" style={{ width: company.profile_completion + "%" }} /></div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}
