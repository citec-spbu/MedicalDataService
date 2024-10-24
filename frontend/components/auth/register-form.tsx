"use client";

import * as z from "zod";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import { RegisterSchema } from "@/schemas";

import {
  Form,
  FormControl,
  FormItem,
  FormField,
  FormMessage
} from "@/components/ui/form";
import { CardWrapper } from "@/components/auth/card-wrapper";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { FormError } from "@/components/form-error";
import { FormSuccess } from "@/components/form-success";

import { register } from "@/actions/register";

export const RegisterForm = () => {
  const [error, setError] = useState<string | undefined>("");
  const [success, setSuccess] = useState<string | undefined>("");
  const [isPending, setIsPending] = useState(false);

  const form = useForm<z.infer<typeof RegisterSchema>>({
    resolver: zodResolver(RegisterSchema),
    defaultValues: {
      login: "",
      password: "",
      confirmPassword: ""
    }
  });

  const onSubmit = (values: z.infer<typeof RegisterSchema>) => {
    setError("");
    setSuccess("");
    setIsPending(true);

    register(values)
      .then((data) => {
        if (data.success) setSuccess(data.message);
        else setError(data.message);
      })
      .finally(() => setIsPending(false));
  };
  return (
    <CardWrapper
      headerLabel="Регистрация аккаунта"
      showFooter
      footerLabels={["Войти в существующий аккаунт"]}
      footerHrefs={["/auth/login"]}
    >
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="w-[300px]">
          <div className="space-y-4">
            <FormField
              control={form.control}
              name="login"
              render={({ field }) => (
                <FormItem>
                  <FormControl>
                    <Input
                      {...field}
                      disabled={isPending}
                      placeholder="Логин"
                      type="text"
                      className="text-base"
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            ></FormField>
            <FormField
              control={form.control}
              name="password"
              render={({ field }) => (
                <FormItem>
                  <FormControl>
                    <Input
                      {...field}
                      disabled={isPending}
                      placeholder="Пароль"
                      type="password"
                      className="text-base"
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            ></FormField>
            <FormField
              control={form.control}
              name="confirmPassword"
              render={({ field }) => (
                <FormItem>
                  <FormControl>
                    <Input
                      {...field}
                      disabled={isPending}
                      placeholder="Повторите пароль"
                      type="password"
                      className="text-base"
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            ></FormField>
            <FormError message={error} />
            <FormSuccess message={success} />
            <Button
              disabled={isPending}
              variant="default"
              type="submit"
              className="w-full text-white bg-ring"
            >
              Зарегестрироваться
            </Button>
          </div>
        </form>
      </Form>
    </CardWrapper>
  );
};
