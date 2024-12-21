"use client";

import { jwtDecode, JwtPayload } from "jwt-decode";
import {
  createContext,
  ReactNode,
  useContext,
  useEffect,
  useState
} from "react";

export type UserRole = "ADMIN" | "MODERATOR" | "UPLOADER" | "TECHNICAL";

export interface User {
  name: string;
  role: UserRole;
}

export const UserContext = createContext<User | null>(null);

export const UserProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    const tokenFromLocalStorage = localStorage.getItem("accessToken");
    if (tokenFromLocalStorage) {
      const decodedToken = jwtDecode<JwtPayload & { role: UserRole }>(
        tokenFromLocalStorage
      );
      setUser({ name: decodedToken.sub!, role: decodedToken.role });
    }
  }, []);

  useEffect(() => {
    const handleStorageEvent = (e: StorageEvent) => {
      console.log(e.key);
      if (e.key == "accessToken") {
        const token = localStorage.getItem("accessToken");
        if (token) {
          const decodedToken = jwtDecode<JwtPayload & { role: UserRole }>(
            token
          );
          setUser({ name: decodedToken.sub!, role: decodedToken.role });
        } else {
          setUser(null);
        }
      }
    };

    window.addEventListener("storage", handleStorageEvent);
    return () => {
      window.removeEventListener("storage", handleStorageEvent);
    };
  }, []);

  return <UserContext.Provider value={user}>{children}</UserContext.Provider>;
};

export const useUserContext = (): User | null => {
  return useContext(UserContext);
};
