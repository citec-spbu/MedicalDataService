"use client";

import { createContext, ReactNode, useContext, useMemo, useState } from "react";

interface User {
  name: string;
  role: string;
}

interface UserContextType {
  user: User | null;
  setUser: (user: User | null) => void;
}

export const UserContext = createContext<UserContextType | null>(null);

export const UserProvider = ({
  children
}: Readonly<{ children: ReactNode }>) => {
  const [user, setUser] = useState<User | null>(null);
  const obj = useMemo(() => ({ user: user, setUser: setUser }), [user]);

  return <UserContext.Provider value={obj}>{children}</UserContext.Provider>;
};

export const useUserContext = (): UserContextType => {
  const context = useContext(UserContext);
  if (context === null) {
    throw new Error("useUserContext must be used within a UserProvider");
  }
  return context;
};
