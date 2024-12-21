"use client";

import * as z from "zod";

import { startTransition, useActionState, useEffect, useRef } from "react";
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
import { useRouter } from "next/navigation";

export const LoginForm = () => {
  const router = useRouter();
  const [state, loginAction, isPending] = useActionState(login, {
    message: "",
    fields: {}
  });

  useEffect(() => {
    if (state.message === "success") {
      localStorage.setItem("accessToken", state.fields!.accessToken);

      router.push("/");
    }
  }, [state, router]);

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
              startTransition(async () => {
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

            {state?.message !== "success" && (
              <FormError message={state?.message} />
            )}
            <Button
              disabled={isPending}
              variant="default"
              type="submit"
              className="w-full bg-ring"
            >
              Войти
            </Button>
          </div>
        </form>
      </Form>
    </CardWrapper>
  );
};
