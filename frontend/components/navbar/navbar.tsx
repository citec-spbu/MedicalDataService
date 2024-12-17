"use client";

import Link from "next/link";
import { HomeIcon } from "lucide-react";
import { usePathname } from "next/navigation";
import { ModeToggle } from "@/components/themes/theme-button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import { Cart } from "./cart";
import { useEffect, useState } from "react";
import { useUserContext } from "@/providers/user-provider";

export const Navbar = () => {
  const pathname = usePathname();
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
        <CustomLink href="/browser">Проводник</CustomLink>
        <CustomLink href={`/viewer${viewerQueryParams ?? ""}`}>
          Просмотр файлов
        </CustomLink>
        <DropdownMenu>
          <DropdownMenuTrigger>{user.name}</DropdownMenuTrigger>
          <DropdownMenuContent>
            <DropdownMenuItem asChild>
              <Button>Выйти из аккунта</Button>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
        <ModeToggle />
        <Cart />
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
