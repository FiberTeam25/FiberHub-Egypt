"use client";

import Link from "next/link";
import { useAuthStore } from "@/store/auth";
import { useCurrentUser, useLogout } from "@/hooks/useAuth";
import { useUnreadCount } from "@/hooks/useNotifications";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Bell, Menu, User, LogOut, LayoutDashboard } from "lucide-react";
import { useState } from "react";
import { LanguageToggle } from "@/components/layout/LanguageToggle";

export function Header() {
  const { user } = useAuthStore();
  useCurrentUser();
  const logout = useLogout();
  const { data: unreadCount } = useUnreadCount();
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 border-b bg-white/95 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4">
        <Link href="/" className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground font-bold text-sm">
            FH
          </div>
          <span className="text-lg font-semibold hidden sm:inline">FiberHub Egypt</span>
        </Link>

        <nav className="hidden md:flex items-center gap-6 text-sm">
          <Link href="/search" className="text-muted-foreground hover:text-foreground transition-colors">
            Search
          </Link>
          <Link href="/search?type=companies" className="text-muted-foreground hover:text-foreground transition-colors">
            Companies
          </Link>
          <Link href="/search?type=professionals" className="text-muted-foreground hover:text-foreground transition-colors">
            Professionals
          </Link>
        </nav>

        <div className="flex items-center gap-2">
          <LanguageToggle />
          {user ? (
            <>
              <Link href="/notifications" className="relative p-2">
                <Bell className="h-5 w-5 text-muted-foreground" />
                {unreadCount && unreadCount > 0 && (
                  <span className="absolute -top-0.5 -right-0.5 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-[10px] text-white font-medium">
                    {unreadCount > 9 ? "9+" : unreadCount}
                  </span>
                )}
              </Link>
              <DropdownMenu>
                <DropdownMenuTrigger render={<Button variant="ghost" size="sm" className="gap-2" />}>
                    <User className="h-4 w-4" />
                    <span className="hidden sm:inline">
                      {user.first_name || user.email}
                    </span>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-48">
                  <DropdownMenuItem render={<Link href="/dashboard" className="cursor-pointer" />}>
                      <LayoutDashboard className="mr-2 h-4 w-4" />
                      Dashboard
                  </DropdownMenuItem>
                  {user.account_type === "admin" && (
                    <DropdownMenuItem render={<Link href="/admin" className="cursor-pointer" />}>
                        <LayoutDashboard className="mr-2 h-4 w-4" />
                        Admin Panel
                    </DropdownMenuItem>
                  )}
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={logout} className="cursor-pointer text-red-600">
                    <LogOut className="mr-2 h-4 w-4" />
                    Logout
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </>
          ) : (
            <div className="flex items-center gap-2">
              <Button variant="ghost" size="sm" render={<Link href="/login" />}>Login</Button>
              <Button size="sm" render={<Link href="/signup" />}>Sign Up</Button>
            </div>
          )}
          <Button
            variant="ghost"
            size="icon"
            className="md:hidden"
            onClick={() => setMobileOpen(!mobileOpen)}
          >
            <Menu className="h-5 w-5" />
          </Button>
        </div>
      </div>

      {mobileOpen && (
        <nav className="border-t md:hidden px-4 py-3 space-y-2">
          <Link href="/search" className="block text-sm text-muted-foreground" onClick={() => setMobileOpen(false)}>Search</Link>
          <Link href="/search?type=companies" className="block text-sm text-muted-foreground" onClick={() => setMobileOpen(false)}>Companies</Link>
          <Link href="/search?type=professionals" className="block text-sm text-muted-foreground" onClick={() => setMobileOpen(false)}>Professionals</Link>
        </nav>
      )}
    </header>
  );
}
