"use client";

import * as z from "zod";

import { RegisterSchema } from "@/schemas";

import axios, { AxiosError } from "axios";

type ResponseData = {
  detail: string;
};

export const register = async (values: z.infer<typeof RegisterSchema>) => {
  const result = { success: true, message: "Вы успешно зарегестрировались!" };
  await axios
    .postForm("http://localhost:8000/user/register/", {
      nickname: values.login,
      password: values.password
    })
    .catch(function (error: AxiosError) {
      result.success = false;
      if (error.response) {
        result.message = (error.response.data as ResponseData).detail;
      } else if (error.request) {
        result.message = "Пожалуйста повторите попытку позже";
      } else {
        result.message = "Неизвестная ошибка";
      }
    });
  return result;
};
