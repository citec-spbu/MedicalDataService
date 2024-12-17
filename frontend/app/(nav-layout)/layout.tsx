"use client";

import ReduxProvider from "@/providers/redux-provider";
import { Navbar } from "@/components/navbar/navbar";
import { Suspense } from "react";

const NavLayout = ({ children }: { children: React.ReactNode }) => {
  return (
    <Suspense>
      <ReduxProvider>
        <Navbar />
        {children}
      </ReduxProvider>
    </Suspense>
  );
};

export default NavLayout;
