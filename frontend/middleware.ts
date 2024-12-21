import { jwtDecode, JwtPayload } from "jwt-decode";
import { cookies } from "next/headers";
import { NextResponse, NextRequest } from "next/server";
import { UserRole } from "./providers/user-provider";

const protectedRoutes = ["/browser", "/viewer", "/"];
const publicRoutes = ["/auth/login", "/auth/register"];

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const isProtectedRoute = protectedRoutes.includes(pathname);
  const isPublicRoute = publicRoutes.includes(pathname);

  const token = (await cookies()).get("refresh_token")?.value;
  let decodedToken = null;
  if (token) {
    decodedToken = jwtDecode<JwtPayload & { role: UserRole }>(token);
  }
  if (pathname == "/viewer") {
    if (!request.nextUrl.search) {
      return NextResponse.redirect(new URL("/browser", request.nextUrl));
    }
    if (
      decodedToken?.role === "TECHNICAL" ||
      decodedToken?.role === "UPLOADER"
    ) {
      return NextResponse.redirect(new URL("/", request.nextUrl));
    }
  }
  if (pathname == "/browser" && decodedToken?.role === "UPLOADER") {
    return NextResponse.redirect(new URL("/", request.nextUrl));
  }
  if (isProtectedRoute && !token) {
    return NextResponse.redirect(new URL("/auth/login", request.nextUrl));
  }

  if (isPublicRoute && token) {
    return NextResponse.redirect(new URL("/", request.nextUrl));
  }
  return NextResponse.next();
}

export const config = {
  matcher: ["/auth/:path*", "/viewer/:path*", "/browser/:path*", "/:path*"]
};
