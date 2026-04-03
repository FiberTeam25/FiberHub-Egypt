"use client";

import Link from "next/link";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { useTranslation } from "@/store/language";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Search,
  ShieldCheck,
  FileText,
  MessageSquare,
  Building2,
  Wrench,
  Cable,
  Users,
} from "lucide-react";
import type { TranslationKey } from "@/lib/i18n";

export default function HomePage() {
  const t = useTranslation();

  const features: { icon: typeof Search; titleKey: TranslationKey; descKey: TranslationKey }[] = [
    { icon: Search, titleKey: "home.searchDiscover", descKey: "home.searchDiscoverDesc" },
    { icon: ShieldCheck, titleKey: "home.verifiedProfiles", descKey: "home.verifiedProfilesDesc" },
    { icon: FileText, titleKey: "home.rfqWorkflow", descKey: "home.rfqWorkflowDesc" },
    { icon: MessageSquare, titleKey: "home.contextualMessaging", descKey: "home.contextualMessagingDesc" },
  ];

  const userTypes: { icon: typeof Building2; labelKey: TranslationKey; descKey: TranslationKey }[] = [
    { icon: Building2, labelKey: "home.buyers", descKey: "home.buyersDesc" },
    { icon: Cable, labelKey: "home.suppliers", descKey: "home.suppliersDesc" },
    { icon: Wrench, labelKey: "home.contractors", descKey: "home.contractorsDesc" },
    { icon: Users, labelKey: "home.professionals", descKey: "home.professionalsDesc" },
  ];

  return (
    <div className="min-h-screen flex flex-col">
      <Header />

      <main className="flex-1">
        {/* Hero */}
        <section className="bg-gradient-to-b from-muted/50 to-background py-20">
          <div className="mx-auto max-w-7xl px-4 text-center">
            <Badge variant="secondary" className="mb-4">
              {t("home.badge")}
            </Badge>
            <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-4">
              {t("home.heroTitle1")}
              <br />
              <span className="text-muted-foreground">{t("home.heroTitle2")}</span>
            </h1>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto mb-8">
              {t("home.heroDescription")}
            </p>
            <div className="flex items-center justify-center gap-4">
              <Button size="lg" render={<Link href="/signup" />}>{t("home.getStarted")}</Button>
              <Button size="lg" variant="outline" render={<Link href="/search" />}>{t("home.browseCompanies")}</Button>
            </div>
          </div>
        </section>

        {/* User types */}
        <section className="py-16">
          <div className="mx-auto max-w-7xl px-4">
            <h2 className="text-2xl font-bold text-center mb-10">{t("home.whoUses")}</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {userTypes.map((type) => (
                <Card key={type.labelKey} className="text-center">
                  <CardContent className="pt-6">
                    <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                      <type.icon className="h-6 w-6 text-primary" />
                    </div>
                    <h3 className="font-semibold mb-1">{t(type.labelKey)}</h3>
                    <p className="text-sm text-muted-foreground">{t(type.descKey)}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </section>

        {/* Features */}
        <section className="bg-muted/30 py-16">
          <div className="mx-auto max-w-7xl px-4">
            <h2 className="text-2xl font-bold text-center mb-10">{t("home.features")}</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {features.map((feature) => (
                <div key={feature.titleKey} className="flex gap-4">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                    <feature.icon className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <h3 className="font-semibold mb-1">{t(feature.titleKey)}</h3>
                    <p className="text-sm text-muted-foreground">{t(feature.descKey)}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="py-16">
          <div className="mx-auto max-w-3xl px-4 text-center">
            <h2 className="text-2xl font-bold mb-4">{t("home.ctaTitle")}</h2>
            <p className="text-muted-foreground mb-8">
              {t("home.ctaDescription")}
            </p>
            <Button size="lg" render={<Link href="/signup" />}>{t("home.createAccount")}</Button>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
