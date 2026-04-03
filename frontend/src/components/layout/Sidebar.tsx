"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuthStore } from "@/store/auth";
import { cn } from "@/lib/utils";
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
  label: string;
  href: string;
  icon: React.ElementType;
}

function getBuyerNav(): NavItem[] {
  return [
    { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { label: "Company Profile", href: "/company/profile", icon: Building2 },
    { label: "Team", href: "/company/team", icon: Users },
    { label: "RFQs", href: "/rfqs", icon: FileText },
    { label: "Shortlist", href: "/shortlist", icon: Bookmark },
    { label: "Messages", href: "/messages", icon: MessageSquare },
    { label: "Notifications", href: "/notifications", icon: Bell },
    { label: "Verification", href: "/company/verification", icon: ShieldCheck },
    { label: "Settings", href: "/company/settings", icon: Settings },
  ];
}

function getSupplierNav(): NavItem[] {
  return [
    { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { label: "Company Profile", href: "/company/profile", icon: Building2 },
    { label: "Team", href: "/company/team", icon: Users },
    { label: "Incoming RFQs", href: "/rfqs", icon: FileText },
    { label: "Messages", href: "/messages", icon: MessageSquare },
    { label: "Reviews", href: "/reviews", icon: Star },
    { label: "Notifications", href: "/notifications", icon: Bell },
    { label: "Verification", href: "/company/verification", icon: ShieldCheck },
    { label: "Settings", href: "/company/settings", icon: Settings },
  ];
}

function getIndividualNav(): NavItem[] {
  return [
    { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { label: "My Profile", href: "/profile", icon: UserCircle },
    { label: "Messages", href: "/messages", icon: MessageSquare },
    { label: "Reviews", href: "/reviews", icon: Star },
    { label: "Notifications", href: "/notifications", icon: Bell },
    { label: "Verification", href: "/company/verification", icon: ShieldCheck },
  ];
}

export function Sidebar() {
  const pathname = usePathname();
  const { user } = useAuthStore();

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
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
