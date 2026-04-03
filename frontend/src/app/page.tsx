import Link from "next/link";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
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

const features = [
  {
    icon: Search,
    title: "Search & Discover",
    description: "Find verified suppliers, contractors, and professionals across Egypt's fiber sector.",
  },
  {
    icon: ShieldCheck,
    title: "Verified Profiles",
    description: "Trust badges and verification ensure you're working with legitimate businesses.",
  },
  {
    icon: FileText,
    title: "RFQ Workflow",
    description: "Create and manage Requests for Quotation, invite vendors, and compare responses.",
  },
  {
    icon: MessageSquare,
    title: "Contextual Messaging",
    description: "Communicate directly with vendors, linked to RFQs and business context.",
  },
];

const userTypes = [
  { icon: Building2, label: "Buyers & Operators", description: "Telecom operators, ISPs, developers" },
  { icon: Cable, label: "Suppliers & Distributors", description: "Fiber cables, passive materials, equipment" },
  { icon: Wrench, label: "Contractors", description: "FTTH, OSP, splicing, testing, civil works" },
  { icon: Users, label: "Professionals", description: "Technicians, splicers, OTDR engineers" },
];

export default function HomePage() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />

      <main className="flex-1">
        {/* Hero */}
        <section className="bg-gradient-to-b from-muted/50 to-background py-20">
          <div className="mx-auto max-w-7xl px-4 text-center">
            <Badge variant="secondary" className="mb-4">
              Egypt&apos;s Fiber Optic B2B Network
            </Badge>
            <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-4">
              Connect, Source & Build Trust
              <br />
              <span className="text-muted-foreground">in Egypt&apos;s Fiber Sector</span>
            </h1>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto mb-8">
              The trusted platform where buyers, suppliers, contractors, and professionals
              find each other, issue RFQs, and build verified business relationships.
            </p>
            <div className="flex items-center justify-center gap-4">
              <Button size="lg" render={<Link href="/signup" />}>Get Started Free</Button>
              <Button size="lg" variant="outline" render={<Link href="/search" />}>Browse Companies</Button>
            </div>
          </div>
        </section>

        {/* User types */}
        <section className="py-16">
          <div className="mx-auto max-w-7xl px-4">
            <h2 className="text-2xl font-bold text-center mb-10">Who Uses FiberHub?</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {userTypes.map((type) => (
                <Card key={type.label} className="text-center">
                  <CardContent className="pt-6">
                    <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                      <type.icon className="h-6 w-6 text-primary" />
                    </div>
                    <h3 className="font-semibold mb-1">{type.label}</h3>
                    <p className="text-sm text-muted-foreground">{type.description}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </section>

        {/* Features */}
        <section className="bg-muted/30 py-16">
          <div className="mx-auto max-w-7xl px-4">
            <h2 className="text-2xl font-bold text-center mb-10">Platform Features</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {features.map((feature) => (
                <div key={feature.title} className="flex gap-4">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                    <feature.icon className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <h3 className="font-semibold mb-1">{feature.title}</h3>
                    <p className="text-sm text-muted-foreground">{feature.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="py-16">
          <div className="mx-auto max-w-3xl px-4 text-center">
            <h2 className="text-2xl font-bold mb-4">Ready to join Egypt&apos;s fiber network?</h2>
            <p className="text-muted-foreground mb-8">
              Create your company profile, get verified, and start connecting with the right partners.
            </p>
            <Button size="lg" render={<Link href="/signup" />}>Create Your Account</Button>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
