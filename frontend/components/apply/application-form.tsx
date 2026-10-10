"use client";

import { ChevronDown, Loader2 } from "lucide-react";
import { useState } from "react";
import { useForm } from "react-hook-form";

import { controlClass, Field } from "@/components/apply/field";
import { ApiError, submitApplication } from "@/lib/api";
import { COURSE_OPTIONS } from "@/lib/courses";
import {
  applicationSchema,
  type ApplicationFormValues,
} from "@/lib/validations/application";
import { zodResolver } from "@/lib/zod-resolver";

type ApplicationFormProps = {
  onSuccess: () => void;
};

function todayIsoDate(): string {
  return new Date().toISOString().slice(0, 10);
}

export function ApplicationForm({ onSuccess }: ApplicationFormProps) {
  const [submitError, setSubmitError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ApplicationFormValues>({
    resolver: zodResolver(applicationSchema),
    mode: "onSubmit",
    defaultValues: {
      applicant_name: "",
      phone: "",
      email: "",
      birth_date: "",
      course_name: "",
    },
  });

  const onSubmit = async (values: ApplicationFormValues): Promise<void> => {
    setSubmitError(null);
    try {
      await submitApplication(values);
      onSuccess();
    } catch (error) {
      if (error instanceof ApiError) {
        setSubmitError(error.message);
        return;
      }
      setSubmitError(
        "We could not reach EduFlow right now. Check your connection and try again.",
      );
    }
  };

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="rounded-2xl border border-slate-200 bg-white p-6 shadow-card sm:p-8"
      noValidate
      aria-busy={isSubmitting}
    >
      <div className="mb-6 border-b border-slate-100 pb-5">
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-teal-700">
          Application
        </p>
        <h2 className="mt-1.5 text-xl font-semibold tracking-tight text-slate-900">
          Start your enrolment
        </h2>
        <p className="mt-1 text-sm text-slate-500">
          Tell us who you are. An administrator will generate your contract.
        </p>
      </div>

      {submitError ? (
        <div
          role="alert"
          className="mb-5 rounded-lg border border-red-200 bg-red-50 px-3.5 py-3 text-sm text-red-700"
        >
          {submitError}
        </div>
      ) : null}

      <div className="space-y-4">
        <Field
          id="applicant_name"
          label="Full name"
          error={errors.applicant_name?.message}
        >
          <input
            id="applicant_name"
            type="text"
            autoComplete="name"
            placeholder="Ada Lovelace"
            disabled={isSubmitting}
            aria-invalid={Boolean(errors.applicant_name)}
            className={controlClass(Boolean(errors.applicant_name))}
            {...register("applicant_name")}
          />
        </Field>

        <div className="grid gap-4 sm:grid-cols-2">
          <Field
            id="email"
            label="Email"
            error={errors.email?.message}
          >
            <input
              id="email"
              type="email"
              autoComplete="email"
              placeholder="ada@company.com"
              disabled={isSubmitting}
              aria-invalid={Boolean(errors.email)}
              className={controlClass(Boolean(errors.email))}
              {...register("email")}
            />
          </Field>

          <Field
            id="phone"
            label="Phone"
            hint="E.164 format, starting with +"
            error={errors.phone?.message}
          >
            <input
              id="phone"
              type="tel"
              autoComplete="tel"
              placeholder="+77011234567"
              disabled={isSubmitting}
              aria-invalid={Boolean(errors.phone)}
              className={controlClass(Boolean(errors.phone))}
              {...register("phone")}
            />
          </Field>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <Field
            id="birth_date"
            label="Birth date"
            error={errors.birth_date?.message}
          >
            <input
              id="birth_date"
              type="date"
              max={todayIsoDate()}
              disabled={isSubmitting}
              aria-invalid={Boolean(errors.birth_date)}
              className={controlClass(Boolean(errors.birth_date))}
              {...register("birth_date")}
            />
          </Field>

          <Field
            id="course_name"
            label="Course name"
            error={errors.course_name?.message}
          >
            <div className="relative">
              <select
                id="course_name"
                disabled={isSubmitting}
                aria-invalid={Boolean(errors.course_name)}
                className={`${controlClass(Boolean(errors.course_name))} appearance-none pr-10`}
                {...register("course_name")}
              >
                <option value="">Select a programme</option>
                {COURSE_OPTIONS.map((course) => (
                  <option key={course} value={course}>
                    {course}
                  </option>
                ))}
              </select>
              <ChevronDown
                className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400"
                aria-hidden
              />
            </div>
          </Field>
        </div>
      </div>

      <button
        type="submit"
        disabled={isSubmitting}
        className="mt-7 inline-flex w-full items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-sky-600 to-teal-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:from-sky-700 hover:to-teal-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-500/40 disabled:cursor-not-allowed disabled:opacity-70"
      >
        {isSubmitting ? (
          <>
            <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
            Submitting application…
          </>
        ) : (
          "Submit application"
        )}
      </button>
    </form>
  );
}
