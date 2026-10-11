"use client";

import { ChevronDown, Loader2 } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useForm } from "react-hook-form";

import { controlClass, Field } from "@/components/apply/field";
import { SuccessState } from "@/components/apply/success-state";
import {
  ApiError,
  listInstitutions,
  listPrograms,
  listRequirementProfiles,
  submitApplication,
} from "@/lib/api";
import type {
  ApplicationCreatedResponse,
  Institution,
  Program,
  RequirementProfile,
} from "@/lib/types/application";
import {
  applicationDetailsSchema,
  type ApplicationDetailsValues,
} from "@/lib/validations/application";
import { zodResolver } from "@/lib/zod-resolver";

type Step = "select" | "details" | "review";

function todayIsoDate(): string {
  return new Date().toISOString().slice(0, 10);
}

export function ApplicationFlow() {
  const [step, setStep] = useState<Step>("select");
  const [catalogError, setCatalogError] = useState<string | null>(null);
  const [catalogLoading, setCatalogLoading] = useState(true);
  const [selectionLoading, setSelectionLoading] = useState(false);
  const [institutions, setInstitutions] = useState<Institution[]>([]);
  const [programs, setPrograms] = useState<Program[]>([]);
  const [profiles, setProfiles] = useState<RequirementProfile[]>([]);
  const [institutionId, setInstitutionId] = useState("");
  const [programId, setProgramId] = useState("");
  const [profileId, setProfileId] = useState("");
  const [selectionError, setSelectionError] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<ApplicationCreatedResponse | null>(null);

  const form = useForm<ApplicationDetailsValues>({
    resolver: zodResolver(applicationDetailsSchema),
    mode: "onSubmit",
    defaultValues: {
      applicant_name: "",
      phone: "",
      email: "",
      birth_date: "",
    },
  });

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      setCatalogLoading(true);
      setCatalogError(null);
      try {
        const data = await listInstitutions();
        if (!cancelled) {
          setInstitutions(data);
        }
      } catch (error) {
        if (!cancelled) {
          setCatalogError(
            error instanceof ApiError
              ? error.message
              : "We could not load institutions.",
          );
        }
      } finally {
        if (!cancelled) {
          setCatalogLoading(false);
        }
      }
    };
    void load();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!institutionId) {
      setPrograms([]);
      setProfiles([]);
      setProgramId("");
      setProfileId("");
      return;
    }
    let cancelled = false;
    const load = async () => {
      setSelectionLoading(true);
      setPrograms([]);
      setProfiles([]);
      try {
        const [nextPrograms, nextProfiles] = await Promise.all([
          listPrograms(institutionId),
          listRequirementProfiles(institutionId),
        ]);
        if (cancelled) {
          return;
        }
        setPrograms(nextPrograms);
        setProfiles(nextProfiles);
        setProgramId((current) =>
          nextPrograms.some((item) => item.id === current) ? current : "",
        );
        setProfileId((current) => {
          if (nextProfiles.length === 1) {
            return nextProfiles[0].id;
          }
          return nextProfiles.some((item) => item.id === current) ? current : "";
        });
      } catch (error) {
        if (!cancelled) {
          setCatalogError(
            error instanceof ApiError
              ? error.message
              : "We could not load programmes.",
          );
        }
      } finally {
        if (!cancelled) {
          setSelectionLoading(false);
        }
      }
    };
    void load();
    return () => {
      cancelled = true;
    };
  }, [institutionId]);

  const institution = institutions.find((item) => item.id === institutionId);
  const program = programs.find((item) => item.id === programId);
  const profile = profiles.find((item) => item.id === profileId);
  const details = form.watch();

  const steps = useMemo(
    () => [
      { id: "select", label: "Programme" },
      { id: "details", label: "Your details" },
      { id: "review", label: "Review" },
    ],
    [],
  );

  const continueFromSelect = () => {
    setSelectionError(null);
    if (!institution || !program || !profile) {
      setSelectionError(
        "Choose an institution, programme, and verified requirement profile.",
      );
      return;
    }
    setStep("details");
  };

  const onDetails = form.handleSubmit(() => {
    setSubmitError(null);
    setStep("review");
  });

  const onSubmit = async () => {
    if (!program || !profile) {
      return;
    }
    const values = form.getValues();
    setSubmitError(null);
    setSubmitting(true);
    try {
      const created = await submitApplication({
        program_id: program.id,
        requirement_profile_id: profile.id,
        applicant_name: values.applicant_name,
        birth_date: values.birth_date,
        phone: values.phone,
        email: values.email,
      });
      setResult(created);
    } catch (error) {
      setSubmitError(
        error instanceof ApiError
          ? error.message
          : "We could not reach EduFlow right now.",
      );
    } finally {
      setSubmitting(false);
    }
  };

  if (result) {
    return (
      <SuccessState
        result={result}
        onReset={() => {
          setResult(null);
          setStep("select");
          form.reset();
        }}
      />
    );
  }

  return (
    <div className="rounded-xl border border-[var(--line)] bg-[#fffcf7] p-6 shadow-sm sm:p-8">
      <ol className="mb-6 flex gap-2 text-[11px] font-medium uppercase tracking-[0.14em] text-[var(--muted)]">
        {steps.map((item, index) => (
          <li
            key={item.id}
            className={
              item.id === step ? "text-[var(--accent)]" : "text-[var(--muted)]"
            }
          >
            {index + 1}. {item.label}
            {index < steps.length - 1 ? (
              <span className="mx-2 text-[var(--line)]" aria-hidden>
                /
              </span>
            ) : null}
          </li>
        ))}
      </ol>

      {catalogError ? (
        <p role="alert" className="mb-4 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800">
          {catalogError}
        </p>
      ) : null}

      {step === "select" ? (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold tracking-tight">Choose where you are applying</h2>
          <p className="text-sm leading-6 text-[var(--muted)]">
            Requirements come from the institution’s verified admissions profile.
            EduFlow only asks for the contact fields that profile uses.
          </p>
          {catalogLoading ? (
            <p className="text-sm text-[var(--muted)]">Loading institutions…</p>
          ) : institutions.length === 0 ? (
            <p className="rounded-md border border-dashed border-[var(--line)] px-4 py-6 text-sm text-[var(--muted)]">
              No institutions are published yet. Ask the registrar to seed the catalog.
            </p>
          ) : (
            <>
              <Field id="institution" label="Institution" error={undefined}>
                <div className="relative">
                  <select
                    id="institution"
                    value={institutionId}
                    onChange={(event) => setInstitutionId(event.target.value)}
                    className={`${controlClass(false)} appearance-none pr-10`}
                  >
                    <option value="">Select an institution</option>
                    {institutions.map((item) => (
                      <option key={item.id} value={item.id}>
                        {item.name}
                      </option>
                    ))}
                  </select>
                  <ChevronDown className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--muted)]" aria-hidden />
                </div>
              </Field>
              <Field id="program" label="Programme">
                <div className="relative">
                  <select
                    id="program"
                    value={programId}
                    disabled={!institutionId}
                    onChange={(event) => setProgramId(event.target.value)}
                    className={`${controlClass(false)} appearance-none pr-10`}
                  >
                    <option value="">Select a programme</option>
                    {programs.map((item) => (
                      <option key={item.id} value={item.id}>
                        {item.name}
                      </option>
                    ))}
                  </select>
                  <ChevronDown className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--muted)]" aria-hidden />
                </div>
              </Field>
              {institutionId && selectionLoading ? (
                <p className="text-sm text-[var(--muted)]">Loading programmes…</p>
              ) : null}
              {institutionId && !selectionLoading && programs.length === 0 ? (
                <p className="text-sm text-[var(--muted)]">
                  This institution has no published programmes yet.
                </p>
              ) : null}
              {institutionId && !selectionLoading && programs.length > 0 && profiles.length === 0 ? (
                <p className="text-sm text-[var(--muted)]">
                  No verified requirement profile is available for this institution.
                </p>
              ) : null}
              {profiles.length > 1 ? (
                <Field id="profile" label="Requirement profile">
                  <div className="relative">
                    <select
                      id="profile"
                      value={profileId}
                      onChange={(event) => setProfileId(event.target.value)}
                      className={`${controlClass(false)} appearance-none pr-10`}
                    >
                      <option value="">Select a profile</option>
                      {profiles.map((item) => (
                        <option key={item.id} value={item.id}>
                          {item.name}
                        </option>
                      ))}
                    </select>
                    <ChevronDown className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--muted)]" aria-hidden />
                  </div>
                </Field>
              ) : null}
            </>
          )}

          {profile ? (
            <section className="rounded-lg border border-[var(--line)] bg-white px-4 py-4">
              <h3 className="text-sm font-semibold">Admission requirements</h3>
              <p className="mt-1 text-sm text-[var(--ink)]">{profile.name}</p>
              <p className="mt-2 text-xs leading-5 text-[var(--muted)]">
                Official source:{" "}
                <a
                  href={profile.source_reference}
                  className="underline underline-offset-2"
                  target="_blank"
                  rel="noreferrer"
                >
                  {profile.source_reference}
                </a>
              </p>
              <ul className="mt-3 list-disc space-y-1 pl-5 text-sm text-[var(--muted)]">
                <li>Full legal name</li>
                <li>Date of birth</li>
                <li>International phone number</li>
                <li>Email address</li>
              </ul>
              <p className="mt-3 text-xs text-[var(--muted)]">
                Identity documents, parent details, and other records are not
                collected in this application.
              </p>
            </section>
          ) : null}

          {selectionError ? (
            <p role="alert" className="text-sm text-[var(--danger)]">
              {selectionError}
            </p>
          ) : null}

          {institutions.length > 0 ? (
            <button
              type="button"
              onClick={continueFromSelect}
              className="mt-2 inline-flex w-full items-center justify-center rounded-md bg-[var(--accent)] px-4 py-2.5 text-sm font-semibold text-[#f7f4ee] transition hover:bg-[#17473b]"
            >
              Continue
            </button>
          ) : null}
        </div>
      ) : null}

      {step === "details" ? (
        <form onSubmit={onDetails} className="space-y-4" noValidate>
          <h2 className="text-xl font-semibold tracking-tight">Your details</h2>
          <p className="text-sm text-[var(--muted)]">
            Applying to {program?.name} at {institution?.name}.
          </p>
          <Field
            id="applicant_name"
            label="Full name"
            error={form.formState.errors.applicant_name?.message}
          >
            <input
              id="applicant_name"
              type="text"
              autoComplete="name"
              className={controlClass(Boolean(form.formState.errors.applicant_name))}
              aria-invalid={Boolean(form.formState.errors.applicant_name)}
              {...form.register("applicant_name")}
            />
          </Field>
          <div className="grid gap-4 sm:grid-cols-2">
            <Field id="email" label="Email" error={form.formState.errors.email?.message}>
              <input
                id="email"
                type="email"
                autoComplete="email"
                className={controlClass(Boolean(form.formState.errors.email))}
                aria-invalid={Boolean(form.formState.errors.email)}
                {...form.register("email")}
              />
            </Field>
            <Field
              id="phone"
              label="Phone"
              hint="E.164 format, starting with +"
              error={form.formState.errors.phone?.message}
            >
              <input
                id="phone"
                type="tel"
                autoComplete="tel"
                placeholder="+77011234567"
                className={controlClass(Boolean(form.formState.errors.phone))}
                aria-invalid={Boolean(form.formState.errors.phone)}
                {...form.register("phone")}
              />
            </Field>
          </div>
          <Field
            id="birth_date"
            label="Date of birth"
            error={form.formState.errors.birth_date?.message}
          >
            <input
              id="birth_date"
              type="date"
              max={todayIsoDate()}
              className={controlClass(Boolean(form.formState.errors.birth_date))}
              aria-invalid={Boolean(form.formState.errors.birth_date)}
              {...form.register("birth_date")}
            />
          </Field>
          <div className="flex gap-3 pt-2">
            <button
              type="button"
              onClick={() => setStep("select")}
              className="rounded-md border border-[var(--line)] px-4 py-2.5 text-sm font-medium"
            >
              Back
            </button>
            <button
              type="submit"
              className="flex-1 rounded-md bg-[var(--accent)] px-4 py-2.5 text-sm font-semibold text-[#f7f4ee] hover:bg-[#17473b]"
            >
              Review
            </button>
          </div>
        </form>
      ) : null}

      {step === "review" ? (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold tracking-tight">Review and submit</h2>
          <dl className="space-y-2 rounded-lg border border-[var(--line)] bg-white px-4 py-4 text-sm">
            <ReviewRow label="Institution" value={institution?.name ?? "—"} />
            <ReviewRow label="Programme" value={program?.name ?? "—"} />
            <ReviewRow label="Requirements" value={profile?.name ?? "—"} />
            <ReviewRow label="Name" value={details.applicant_name} />
            <ReviewRow label="Email" value={details.email} />
            <ReviewRow label="Phone" value={details.phone} />
            <ReviewRow label="Date of birth" value={details.birth_date} />
          </dl>
          {submitError ? (
            <p role="alert" className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800">
              {submitError}
            </p>
          ) : null}
          <div className="flex gap-3">
            <button
              type="button"
              onClick={() => setStep("details")}
              disabled={submitting}
              className="rounded-md border border-[var(--line)] px-4 py-2.5 text-sm font-medium disabled:opacity-60"
            >
              Back
            </button>
            <button
              type="button"
              onClick={() => void onSubmit()}
              disabled={submitting}
              className="inline-flex flex-1 items-center justify-center gap-2 rounded-md bg-[var(--accent)] px-4 py-2.5 text-sm font-semibold text-[#f7f4ee] hover:bg-[#17473b] disabled:opacity-70"
            >
              {submitting ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
                  Submitting…
                </>
              ) : (
                "Submit application"
              )}
            </button>
          </div>
        </div>
      ) : null}
    </div>
  );
}

function ReviewRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between gap-4">
      <dt className="text-[var(--muted)]">{label}</dt>
      <dd className="text-right font-medium">{value}</dd>
    </div>
  );
}
