"use client";

import Link from "next/link";
import { HomeIcon } from "lucide-react";
import { usePathname } from "next/navigation";
import { ModeToggle } from "@/components/themes/theme-button";

export const Navbar = () => {
  return (
    <nav className="flex justify-center w-full h-16 overflow-hidden sticky top-0 bg-background">
      <ul className="w-full h-full flex justify-around items-center max-w-[1000px] text-xl">
        <CustomLink href="/">
          <HomeIcon />
        </CustomLink>
        <CustomLink href="/browser">Проводник</CustomLink>
        <CustomLink href="/viewer">Просмотр файлов</CustomLink>
        <CustomLink href="/">Фамилия И. О.</CustomLink>
        <ModeToggle />
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
    <li className={path === href ? "text-blue-500 font-bold" : ""}>
      <Link href={href} {...props}>
        {children}
      </Link>
    </li>
  );
}
