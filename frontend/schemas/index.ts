import * as z from "zod";

export const RegisterSchema = z
  .object({
    login: z
      .string()
      .min(3, { message: "Логин должен содержать не менее 3 символов" })
      .max(40, { message: "Логин должен содержать не более 40 символов" })
      .regex(/^[A-Za-z][A-Za-z0-9]*$/, {
        message: "Логин содержит недопустимые символы"
      })
      .trim(),
    password: z
      .string()
      .min(8, { message: "Пароль должен содержать не менее 8 символов" })
      .max(72, { message: "Пароль должен содержать не более 72 символов" })
      .regex(/^[A-Za-z][A-Za-z0-9@$!%*#?&]*$/, {
        message: "Пароль содержит недопустимые символы"
      })
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

export const LoginSchemas = z.object({
  login: z
    .string()
    .min(3, { message: "Логин должен содержать не менее 3 символов" })
    .max(40, { message: "Логин должен содержать не более 40 символов" })
    .regex(/^[A-Za-z][A-Za-z0-9]*$/, {
      message: "Логин содержит недопустимые символы"
    })
    .trim(),
  password: z
    .string()
    .min(8, { message: "Пароль должен содержать не менее 8 символов" })
    .max(72, { message: "Пароль должен содержать не более 72 символов" })
    .regex(/^[A-Za-z][A-Za-z0-9@$!%*#?&]*$/, {
      message: "Пароль содержит недопустимые символы"
    })
    .trim()
});
