"use client";

import api from "@/lib/api";
import {
  createContext,
  ReactNode,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState
} from "react";

interface User {
  name: string;
  role: string;
}

export const UserContext = createContext<User | null>(null);

export const UserProvider = ({
  children
}: Readonly<{ children: ReactNode }>) => {
  const [user, setUser] = useState<User | null>(null);
  const obj = useMemo(() => user, [user]);
  useEffect(() => {
    const fetchUser = async () => {
      const response = (await api.get("/user/me")).data;
      setUser({ name: response.nickname, role: response.role });
    };

    fetchUser();

    const handleStorageChange = (event: StorageEvent) => {
      if (event.key === "accessToken") {
        fetchUser();
      }
    };

    window.addEventListener("storage", handleStorageChange);

    return () => {
      window.removeEventListener("storage", handleStorageChange);
    };
  }, []);
  return <UserContext.Provider value={obj}>{children}</UserContext.Provider>;
};

export const useUserContext = (): User | null => {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error("useUserContext must be used within a UserProvider");
  }
  return context;
};
