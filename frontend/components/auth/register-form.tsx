"use client";

import * as z from "zod";

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

import { CardWrapper } from "./card-wrapper";
import { Input } from "@/components/ui/input";
import { Button } from "../ui/button";

export const RegisterForm = () => {
  const form = useForm<z.infer<typeof RegisterSchema>>({
    resolver: zodResolver(RegisterSchema),
    defaultValues: {
      login: "",
      password: "",
      confirmPassword: ""
    }
  });

  const onSubmit = (values: z.infer<typeof RegisterSchema>) => {
    // TODO: send to server
    console.log(values);
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
                      placeholder="Повторите пароль"
                      type="password"
                      className="text-base"
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            ></FormField>
            <Button
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
