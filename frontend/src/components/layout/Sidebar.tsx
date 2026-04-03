"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuthStore } from "@/store/auth";
import { useTranslation } from "@/store/language";
import { cn } from "@/lib/utils";
import type { TranslationKey } from "@/lib/i18n";
import {
  LayoutDashboard,
  Building2,
  FileText,
  MessageSquare,
  Bell,
  Star,
  ShieldCheck,
  Settings,
  Users,
  Bookmark,
  UserCircle,
} from "lucide-react";

interface NavItem {
  labelKey: TranslationKey;
  href: string;
  icon: React.ElementType;
}

function getBuyerNav(): NavItem[] {
  return [
    { labelKey: "nav.dashboard", href: "/dashboard", icon: LayoutDashboard },
    { labelKey: "nav.companyProfile", href: "/company/profile", icon: Building2 },
    { labelKey: "nav.team", href: "/company/team", icon: Users },
    { labelKey: "nav.rfqs", href: "/rfqs", icon: FileText },
    { labelKey: "nav.shortlist", href: "/shortlist", icon: Bookmark },
    { labelKey: "nav.messages", href: "/messages", icon: MessageSquare },
    { labelKey: "nav.notifications", href: "/notifications", icon: Bell },
    { labelKey: "nav.verification", href: "/company/verification", icon: ShieldCheck },
    { labelKey: "nav.settings", href: "/company/settings", icon: Settings },
  ];
}

function getSupplierNav(): NavItem[] {
  return [
    { labelKey: "nav.dashboard", href: "/dashboard", icon: LayoutDashboard },
    { labelKey: "nav.companyProfile", href: "/company/profile", icon: Building2 },
    { labelKey: "nav.team", href: "/company/team", icon: Users },
    { labelKey: "nav.incomingRfqs", href: "/rfqs", icon: FileText },
    { labelKey: "nav.messages", href: "/messages", icon: MessageSquare },
    { labelKey: "nav.reviews", href: "/reviews", icon: Star },
    { labelKey: "nav.notifications", href: "/notifications", icon: Bell },
    { labelKey: "nav.verification", href: "/company/verification", icon: ShieldCheck },
    { labelKey: "nav.settings", href: "/company/settings", icon: Settings },
  ];
}

function getIndividualNav(): NavItem[] {
  return [
    { labelKey: "nav.dashboard", href: "/dashboard", icon: LayoutDashboard },
    { labelKey: "nav.profile", href: "/profile", icon: UserCircle },
    { labelKey: "nav.messages", href: "/messages", icon: MessageSquare },
    { labelKey: "nav.reviews", href: "/reviews", icon: Star },
    { labelKey: "nav.notifications", href: "/notifications", icon: Bell },
    { labelKey: "nav.verification", href: "/company/verification", icon: ShieldCheck },
  ];
}

export function Sidebar() {
  const pathname = usePathname();
  const { user } = useAuthStore();
  const t = useTranslation();

  const accountType = user?.account_type || "buyer";
  let navItems: NavItem[];

  if (accountType === "individual") {
    navItems = getIndividualNav();
  } else if (accountType === "buyer") {
    navItems = getBuyerNav();
  } else {
    navItems = getSupplierNav();
  }

  return (
    <aside className="w-64 border-r bg-muted/30 min-h-[calc(100vh-4rem)] hidden lg:block">
      <nav className="p-4 space-y-1">
        {navItems.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors",
                isActive
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
              )}
            >
              <item.icon className="h-4 w-4" />
              {t(item.labelKey)}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
