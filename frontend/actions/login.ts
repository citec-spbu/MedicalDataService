"use server";

import { LoginSchemas } from "@/schemas";
import axios, { AxiosError } from "axios";
import { cookies } from "next/headers";

type ResponseData = {
  detail: string;
};

type FormState = {
  message: string;
  fields?: Record<string, string>;
};

const API = "http://app:8000"

export const login = async (
  prevState: FormState,
  data: FormData
): Promise<FormState> => {
  const formData = Object.fromEntries(data);
  const parsed = LoginSchemas.safeParse(formData);

  try {
    const response = await axios.postForm(`${API}/user/login/`, {
      nickname: formData.login,
      password: formData.password
    });
    (await cookies()).set(
      "refresh_token",
      response.headers["set-cookie"]![0].slice(
        response.headers["set-cookie"]![0].indexOf("=") + 1,
        response.headers["set-cookie"]![0].indexOf(";")
      ),
      { httpOnly: true, maxAge: 2592000, path: "/", sameSite: "lax" }
    );
    return {
      message: "success",
      fields: {
        accessToken: response.data["access_token"]
      }
    };
  } catch (error) {
    const response = { message: "", fields: parsed.data };
    if (error instanceof AxiosError) {
      if (error.response) {
        response.message = (error.response.data as ResponseData).detail;
      } else if (error.request) {
        response.message = "Пожалуйста повторите попытку позже";
      }
    } else {
      response.message = "Неизвестная ошибка";
    }
    return response;
  }
};
