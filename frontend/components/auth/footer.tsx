"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";

interface FooterProps {
  labels?: string[];
  hrefs?: string[];
}

export const Footer = ({ labels, hrefs }: FooterProps) => {
  const footerItems = labels!.map((label, key) => (
    <Button
      variant="link"
      key={label}
      className="text-sm w-full text-alternative"
      size="sm"
      asChild
    >
      <Link href={hrefs![key]}>{label}</Link>
    </Button>
  ));
  return (
    <div className="w-full flex gap-y-4 items-center justify-center">
      {footerItems}
    </div>
  );
};
