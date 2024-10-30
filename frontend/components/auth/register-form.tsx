"use client";

import * as z from "zod";

import { startTransition, useActionState, useRef } from "react";
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

import { register } from "@/actions/register";

export const RegisterForm = () => {
  const [state, registerAction, isPending] = useActionState(register, {
    message: "",
    fields: {}
  });

  const form = useForm<z.infer<typeof RegisterSchema>>({
    resolver: zodResolver(RegisterSchema),
    defaultValues: {
      login: "",
      password: "",
      confirmPassword: "",
      ...(state?.fields ?? {})
    }
  });

  const formRef = useRef<HTMLFormElement>(null);

  return (
    <CardWrapper
      headerLabel="Регистрация аккаунта"
      showFooter
      footerLabels={["Войти в существующий аккаунт"]}
      footerHrefs={["/auth/login"]}
    >
      <Form {...form}>
        <form
          ref={formRef}
          onSubmit={(e) => {
            e.preventDefault();
            form.handleSubmit(() => {
              startTransition(() => {
                registerAction(new FormData(formRef.current!));
              });
            })(e);
          }}
          action={registerAction}
          className="w-[300px]"
        >
          <div className="space-y-4 text-base">
            <FormField
              control={form.control}
              name="login"
              render={({ field }) => (
                <FormItem>
                  <FormControl>
                    <Input {...field} placeholder="Логин" type="text" />
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
                    <Input {...field} placeholder="Пароль" type="password" />
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
                      placeholder="Повторите пароль"
                      type="password"
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            ></FormField>
            <FormError message={state?.message} />
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
