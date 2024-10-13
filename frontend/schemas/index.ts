import * as z from "zod";

export const RegisterSchema = z
  .object({
    login: z.string().min(1, { message: "Необходимо ввести логин" }),
    password: z
      .string()
      .min(6, { message: "Пароль должен содержать не менее 6 символов" }),
    confirmPassword: z.string()
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
