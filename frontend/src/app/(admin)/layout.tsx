"use client";

import { useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";
import { useCurrentUser } from "@/hooks/useAuth";
import { Header } from "@/components/layout/Header";
import { cn } from "@/lib/utils";
import { LayoutDashboard, Users, Building2, ShieldCheck, FolderTree, Star, Loader2 } from "lucide-react";

const adminNav = [
  { label: "Dashboard", href: "/admin", icon: LayoutDashboard },
  { label: "Users", href: "/admin/users", icon: Users },
  { label: "Companies", href: "/admin/companies", icon: Building2 },
  { label: "Verification", href: "/admin/verification", icon: ShieldCheck },
  { label: "Categories", href: "/admin/categories", icon: FolderTree },
  { label: "Reviews", href: "/admin/reviews", icon: Star },
];

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const { data: user, isLoading } = useCurrentUser();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!isLoading && (!user || user.account_type !== "admin")) router.push("/dashboard");
  }, [isLoading, user, router]);

  if (isLoading) return <div className="min-h-screen flex items-center justify-center"><Loader2 className="h-6 w-6 animate-spin" /></div>;
  if (!user || user.account_type !== "admin") return null;

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <div className="flex flex-1">
        <aside className="w-64 border-r bg-muted/30 min-h-[calc(100vh-4rem)] hidden lg:block">
          <div className="p-4">
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">Admin Panel</p>
            <nav className="space-y-1">
              {adminNav.map((item) => {
                const isActive = pathname === item.href || (item.href !== "/admin" && pathname.startsWith(item.href));
                return (
                  <Link key={item.href} href={item.href} className={cn("flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors", isActive ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:bg-muted hover:text-foreground")}>
                    <item.icon className="h-4 w-4" />{item.label}
                  </Link>
                );
              })}
            </nav>
          </div>
        </aside>
        <main className="flex-1 p-6">{children}</main>
      </div>
    </div>
  );
}
