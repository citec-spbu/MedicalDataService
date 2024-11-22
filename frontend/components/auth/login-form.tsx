"use client";

import * as z from "zod";

import { startTransition, useActionState, useRef } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import { LoginSchemas } from "@/schemas";

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

import { login } from "@/actions/login";

export const LoginForm = () => {
  const [state, loginAction, isPending] = useActionState(login, {
    message: "",
    fields: {}
  });

  const form = useForm<z.infer<typeof LoginSchemas>>({
    resolver: zodResolver(LoginSchemas),
    defaultValues: {
      login: "",
      password: "",
      ...(state?.fields ?? {})
    }
  });

  const formRef = useRef<HTMLFormElement>(null);

  return (
    <CardWrapper
      headerLabel="Войти в аккаунт"
      showFooter
      footerLabels={["Регистрация аккаунта"]}
      footerHrefs={["/auth/register"]}
    >
      <Form {...form}>
        <form
          ref={formRef}
          onSubmit={(e) => {
            e.preventDefault();
            form.handleSubmit(() => {
              startTransition(() => {
                loginAction(new FormData(formRef.current!));
              });
            })(e);
          }}
          action={loginAction}
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
            
            <FormError message={state?.message} />
            <Button
              disabled={isPending}
              variant="default"
              type="submit"
              className="w-full text-white bg-ring"
            >
              Войти
            </Button>
          </div>
        </form>
      </Form>
    </CardWrapper>
  );
};
