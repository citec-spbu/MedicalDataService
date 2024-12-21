"use client";

import ReduxProvider from "@/providers/redux-provider";
import { Navbar } from "@/components/navbar/navbar";
import { Suspense } from "react";
import { UserProvider } from "@/providers/user-provider";

const NavLayout = ({ children }: { children: React.ReactNode }) => {
  return (
    <Suspense>
      <ReduxProvider>
        <UserProvider>
          <Navbar />
          {children}
        </UserProvider>
      </ReduxProvider>
    </Suspense>
  );
};

export default NavLayout;
