"use client";

import { Loader2 } from "lucide-react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";
import { useForm } from "react-hook-form";

import { controlClass, Field } from "@/components/apply/field";
import { LogoMark } from "@/components/brand/logo-mark";
import { ApiError, loginAdmin } from "@/lib/api";
import { setAdminToken } from "@/lib/session";
import { loginSchema, type LoginValues } from "@/lib/validations/application";
import { zodResolver } from "@/lib/zod-resolver";

function LoginForm() {
  const router = useRouter();
  const params = useSearchParams();
  const expired = params.get("expired") === "1";
  const [error, setError] = useState<string | null>(
    expired ? "Your session ended. Sign in again." : null,
  );
  const form = useForm<LoginValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: "", password: "" },
  });

  const onSubmit = form.handleSubmit(async (values) => {
    setError(null);
    try {
      const token = await loginAdmin(values.email, values.password);
      setAdminToken(token.access_token);
      router.replace("/admin");
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Could not sign in right now.",
      );
    }
  });

  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-12">
      <div className="w-full max-w-md rounded-xl border border-[var(--line)] bg-[#fffcf7] p-8 shadow-sm">
        <Link href="/" className="flex items-center gap-2.5">
          <LogoMark />
          <span className="text-sm font-semibold">EduFlow</span>
        </Link>
        <h1 className="mt-6 text-2xl font-semibold tracking-tight">
          Registrar sign in
        </h1>
        <p className="mt-2 text-sm text-[var(--muted)]">
          Use the administrator account created with the bootstrap command.
        </p>
        {error ? (
          <p role="alert" className="mt-4 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800">
            {error}
          </p>
        ) : null}
        <form onSubmit={onSubmit} className="mt-6 space-y-4" noValidate>
          <Field id="email" label="Work email" error={form.formState.errors.email?.message}>
            <input
              id="email"
              type="email"
              autoComplete="username"
              className={controlClass(Boolean(form.formState.errors.email))}
              {...form.register("email")}
            />
          </Field>
          <Field
            id="password"
            label="Password"
            error={form.formState.errors.password?.message}
          >
            <input
              id="password"
              type="password"
              autoComplete="current-password"
              className={controlClass(Boolean(form.formState.errors.password))}
              {...form.register("password")}
            />
          </Field>
          <button
            type="submit"
            disabled={form.formState.isSubmitting}
            className="inline-flex w-full items-center justify-center gap-2 rounded-md bg-[var(--accent)] px-4 py-2.5 text-sm font-semibold text-[#f7f4ee] disabled:opacity-70"
          >
            {form.formState.isSubmitting ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
                Signing in…
              </>
            ) : (
              "Sign in"
            )}
          </button>
        </form>
      </div>
    </div>
  );
}

export default function AdminLoginPage() {
  return (
    <Suspense fallback={<p className="p-8 text-sm text-[var(--muted)]">Loading…</p>}>
      <LoginForm />
    </Suspense>
  );
}
