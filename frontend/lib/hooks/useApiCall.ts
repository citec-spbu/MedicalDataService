import { useRouter } from "next/navigation";
import { AxiosError, AxiosResponse } from "axios";
import { useCallback } from "react";

type ApiCallFunction<T> = (...args: any[]) => Promise<AxiosResponse<T>>;

const useApiCall = <T>(apiCall: ApiCallFunction<T>) => {
  const router = useRouter();

  const apiWrapper = useCallback(
    async (...args: any[]): Promise<AxiosResponse<T>> => {
      try {
        return await apiCall(...args);
      } catch (error) {
        const errorMessage = (error as Error).message;
        if (errorMessage === "Unauthorized") {
          router.push("/auth/login");
        } else if ((error as AxiosError).status === 401) {
          localStorage.removeItem("accessToken");
          return await apiCall(...args);
        }
        throw error;
      }
    },
    [apiCall, router]
  );

  return apiWrapper;
};

export default useApiCall;
