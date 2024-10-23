"use client";

import * as z from "zod";

import { RegisterSchema } from "@/schemas";

import axios from "axios";

export const register = async (values: z.infer<typeof RegisterSchema>) => {
  try {
    const response = await axios.postForm(
      "http://localhost:8000/user/register/",
      {
        nickname: values.login,
        password: values.password
      }
    );
    if (response.status === 200) {
      return { success: "Вы успешно зарегестрированы!" };
    }
    throw new Error(response.statusText);
  } catch (error) {
    if (error instanceof Error) {
      return { error: error.message };
    }
    console.log(error);
    throw error;
  }
};
