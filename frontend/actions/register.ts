"use server";

import { RegisterSchema } from "@/schemas";
import axios, { AxiosError } from "axios";
import { redirect } from "next/navigation";

type ResponseData = {
  detail: string;
};

type FormState = {
  message: string;
  fields?: Record<string, string>;
};

export const register = async (
  prevState: FormState,
  data: FormData
): Promise<FormState> => {
  const formData = Object.fromEntries(data);
  const parsed = RegisterSchema.safeParse(formData);

  try {
    await axios.postForm("http://localhost:8000/user/register/", {
      nickname: formData.login,
      password: formData.password
    });
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

  redirect("/auth/login");
};
