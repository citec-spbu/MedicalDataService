import * as z from "zod";

export const RegisterSchema = z
  .object({
    login: z
      .string()
      .min(3, { message: "Логин должен содержать не менее 3 символов" })
      .trim(),
    password: z
      .string()
      .min(8, { message: "Пароль должен содержать не менее 8 символов" })
      .trim(),
    confirmPassword: z.string().trim()
  })
  .superRefine(({ confirmPassword, password }, ctx) => {
    if (confirmPassword !== password) {
      ctx.addIssue({
        code: "custom",
        message: "Пароли не совпадают",
        path: ["confirmPassword"]
      });
    }
  });


  export const LoginSchemas = z
  .object({
    login: z
      .string()
      .min(3, { message: "Логин должен содержать не менее 3 символов" })
      .trim(),
    password: z
      .string()
      .min(8, { message: "Пароль должен содержать не менее 8 символов" })
      .trim(),
  });