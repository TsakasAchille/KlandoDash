import { auth } from "@/lib/auth";
import { NextResponse } from "next/server";

export default auth((req) => {
  const isLoggedIn = !!req.auth;
  const isLoginPage = req.nextUrl.pathname === "/login";
  const pathname = req.nextUrl.pathname;

  // Utilisateur connecté sur /login -> rediriger vers /
  if (isLoggedIn && isLoginPage) {
    return NextResponse.redirect(new URL("/", req.url));
  }

  // Utilisateur non connecté sur page protégée -> rediriger vers /login
  if (!isLoggedIn && !isLoginPage) {
    const loginUrl = new URL("/login", req.url);
    loginUrl.searchParams.set("callbackUrl", pathname);
    return NextResponse.redirect(loginUrl);
  }

  // Logique de contrôle d'accès par rôle
  if (isLoggedIn) {
    const userRole = req.auth?.user?.role;

    // Seuls les admins peuvent accéder à /admin
    if (pathname.startsWith("/admin") && userRole !== "admin") {
      return NextResponse.redirect(new URL("/", req.url));
    }

    // Marketing role access
    if (pathname.startsWith("/marketing") && userRole !== "admin" && userRole !== "marketing") {
      return NextResponse.redirect(new URL("/", req.url));
    }

    // Le rôle 'support' et 'marketing' ne peuvent pas accéder à /stats
    if (pathname.startsWith("/stats") && userRole !== "admin") {
      return NextResponse.redirect(new URL("/", req.url));
    }

    // 'marketing' can access support, users, map
    const canAccessSupport = userRole === "admin" || userRole === "support" || userRole === "marketing";
    if (pathname.startsWith("/support") && !canAccessSupport) {
      return NextResponse.redirect(new URL("/", req.url));
    }
  }

  return NextResponse.next();
});

export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - api/auth (NextAuth endpoints)
     * - api/webhooks (webhook endpoints)
     * - api/health (health checks)
     */
    "/((?!_next|api/auth|api/webhooks|api/health|favicon.ico).*)",
  ],
};
