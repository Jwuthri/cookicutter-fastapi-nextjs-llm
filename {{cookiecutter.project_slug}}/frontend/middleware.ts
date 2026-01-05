import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// Simple middleware - can be extended with Clerk auth later
export function middleware(request: NextRequest) {
  // Allow all routes for now
  // Add authentication logic here when Clerk is configured
  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!.+\\.[\\w]+$|_next).*)", "/", "/(api|trpc)(.*)"],
};
