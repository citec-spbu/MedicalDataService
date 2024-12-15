"use client";

import ReduxProvider from "@/providers/redux-provider";
import { Navbar } from "@/components/navbar/navbar";

const NavLayout = ({ children }: { children: React.ReactNode }) => {
  return (
    <ReduxProvider>
      <Navbar />
      {children}
    </ReduxProvider>
  );
};

export default NavLayout;
