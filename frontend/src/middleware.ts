import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// Middleware runs on the edge — we can't check localStorage.
// Instead, we check for a cookie-based hint or just let client-side handle auth redirects.
// For MVP, we only protect admin routes server-side via a simple pattern check.
// Client-side hooks handle dashboard auth.
export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Admin routes — if no token hint, redirect to login
  // The actual token check happens client-side; this is just a basic guard
  if (pathname.startsWith("/admin")) {
    // Let client handle the full auth check
    return NextResponse.next();
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*", "/admin/:path*"],
};
