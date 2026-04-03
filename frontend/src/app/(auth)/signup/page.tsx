"use client";

import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useRegister } from "@/hooks/useAuth";
import { useTranslation } from "@/store/language";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import type { TranslationKey } from "@/lib/i18n";

const accountTypes: { value: string; labelKey: TranslationKey }[] = [
  { value: "buyer", labelKey: "accountTypeDesc.buyer" },
  { value: "supplier", labelKey: "accountTypeDesc.supplier" },
  { value: "distributor", labelKey: "accountTypeDesc.distributor" },
  { value: "manufacturer", labelKey: "accountTypeDesc.manufacturer" },
  { value: "contractor", labelKey: "accountTypeDesc.contractor" },
  { value: "subcontractor", labelKey: "accountTypeDesc.subcontractor" },
  { value: "individual", labelKey: "accountTypeDesc.individual" },
];

const schema = z.object({
  first_name: z.string().min(1, "First name is required"),
  last_name: z.string().min(1, "Last name is required"),
  email: z.string().email("Invalid email"),
  password: z.string().min(8, "Password must be at least 8 characters"),
  phone: z.string().optional(),
  account_type: z.string().min(1, "Select an account type"),
});

type FormData = z.infer<typeof schema>;

export default function SignupPage() {
  const { mutate: signup, isPending, error } = useRegister();
  const t = useTranslation();

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors },
  } = useForm<FormData>({ resolver: zodResolver(schema) });

  const onSubmit = (data: FormData) => signup(data);

  return (
    <div className="min-h-screen flex items-center justify-center bg-muted/30 px-4 py-8">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <Link href="/" className="inline-flex items-center justify-center gap-2 mb-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground font-bold text-sm">
              FH
            </div>
          </Link>
          <CardTitle>{t("auth.createYourAccount")}</CardTitle>
          <CardDescription>{t("auth.joinNetwork")}</CardDescription>
        </CardHeader>
        <form onSubmit={handleSubmit(onSubmit)}>
          <CardContent className="space-y-4">
            {error && (
              <div className="rounded-lg bg-red-50 border border-red-200 p-3 text-sm text-red-800">
                {(error as { response?: { data?: { detail?: string } } })?.response?.data?.detail || t("auth.registrationFailed")}
              </div>
            )}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="first_name">{t("auth.firstName")}</Label>
                <Input id="first_name" {...register("first_name")} />
                {errors.first_name && <p className="text-xs text-red-500">{errors.first_name.message}</p>}
              </div>
              <div className="space-y-2">
                <Label htmlFor="last_name">{t("auth.lastName")}</Label>
                <Input id="last_name" {...register("last_name")} />
                {errors.last_name && <p className="text-xs text-red-500">{errors.last_name.message}</p>}
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">{t("auth.email")}</Label>
              <Input id="email" type="email" placeholder="you@company.eg" {...register("email")} />
              {errors.email && <p className="text-xs text-red-500">{errors.email.message}</p>}
            </div>
            <div className="space-y-2">
              <Label htmlFor="phone">{t("auth.phoneOptional")}</Label>
              <Input id="phone" placeholder="+20..." {...register("phone")} />
            </div>
            <div className="space-y-2">
              <Label>{t("auth.accountType")}</Label>
              <Select onValueChange={(v) => setValue("account_type", v as string)}>
                <SelectTrigger>
                  <SelectValue placeholder={t("auth.selectRole")} />
                </SelectTrigger>
                <SelectContent>
                  {accountTypes.map((at) => (
                    <SelectItem key={at.value} value={at.value}>
                      {t(at.labelKey)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {errors.account_type && <p className="text-xs text-red-500">{errors.account_type.message}</p>}
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">{t("auth.password")}</Label>
              <Input id="password" type="password" {...register("password")} />
              {errors.password && <p className="text-xs text-red-500">{errors.password.message}</p>}
            </div>
          </CardContent>
          <CardFooter className="flex flex-col gap-4">
            <Button type="submit" className="w-full" disabled={isPending}>
              {isPending ? t("auth.creatingAccount") : t("auth.createAccount")}
            </Button>
            <p className="text-sm text-muted-foreground text-center">
              {t("auth.haveAccount")}{" "}
              <Link href="/login" className="text-foreground font-medium hover:underline">
                {t("auth.signIn")}
              </Link>
            </p>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
