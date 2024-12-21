"use client";

import Link from "next/link";
import { HomeIcon } from "lucide-react";
import { usePathname, useRouter } from "next/navigation";
import { ModeToggle } from "@/components/themes/theme-button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger
} from "@/components/ui/dropdown-menu";
import { Download } from "./download";
import { useEffect, useState } from "react";
import { Upload } from "./upload";
import { logout } from "@/actions/logout";
import { useUserContext } from "@/providers/user-provider";

export const Navbar = () => {
  const pathname = usePathname();
  const router = useRouter();
  const [viewerQueryParams, setViewerQueryParams] = useState<string | null>(
    null
  );

  const user = useUserContext();

  useEffect(() => {
    if (window !== undefined) {
      setViewerQueryParams(localStorage.getItem("viewerQueryParams"));
    }
  }, [pathname]);
  return (
    <nav className="flex justify-center w-full h-16 overflow-hidden sticky top-0 bg-background">
      <ul className="w-full h-full flex justify-around items-center max-w-[1000px] text-xl">
        <CustomLink href="/">
          <HomeIcon />
        </CustomLink>
        {user && user.role !== "UPLOADER" && (
          <CustomLink href="/browser">Проводник</CustomLink>
        )}
        {((user && user.role === "ADMIN") || user?.role === "MODERATOR") && (
          <CustomLink href={`/viewer${viewerQueryParams ?? ""}`}>
            Просмотр файлов
          </CustomLink>
        )}
        <DropdownMenu>
          <DropdownMenuTrigger>{user?.name}</DropdownMenuTrigger>
          <DropdownMenuContent>
            <DropdownMenuItem
              onClick={async () => {
                localStorage.removeItem("accessToken");
                await logout();
                router.push("/auth/login");
              }}
            >
              Выйти из аккунта
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
        <ModeToggle />
        {user && user.role !== "TECHNICAL" && <Upload />}
        {user && user.role !== "UPLOADER" && <Download />}
      </ul>
    </nav>
  );
};

function CustomLink({
  href,
  children,
  ...props
}: Readonly<{
  href: string;
  children: React.ReactNode;
}>) {
  const path = usePathname();
  return (
    <li
      className={
        path ===
        href.substring(
          0,
          href.indexOf("?") > 0 ? href.indexOf("?") : href.length
        )
          ? "text-blue-500 font-bold"
          : ""
      }
    >
      <Link href={href} {...props}>
        {children}
      </Link>
    </li>
  );
}
