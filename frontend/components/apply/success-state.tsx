import { STATUS_LABELS, applicantNextStep } from "@/lib/status";
import type { ApplicationCreatedResponse } from "@/lib/types/application";

type SuccessStateProps = {
  result: ApplicationCreatedResponse;
  onReset: () => void;
};

export function SuccessState({ result, onReset }: SuccessStateProps) {
  return (
    <div
      className="rounded-xl border border-[var(--line)] bg-[#fffcf7] p-8 shadow-sm sm:p-10"
      role="status"
      aria-live="polite"
    >
      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--accent)]">
        Submitted
      </p>
      <h2 className="mt-2 text-2xl font-semibold tracking-tight">
        Application received
      </h2>
      <p className="mt-3 text-sm leading-6 text-[var(--muted)]">
        The registrar has your file. A PDF is not generated at this step, and
        this confirmation is not an offer of admission.
      </p>

      <dl className="mt-6 grid gap-3 rounded-lg border border-[var(--line)] bg-white px-4 py-4 text-sm">
        <div className="flex justify-between gap-4">
          <dt className="text-[var(--muted)]">Reference</dt>
          <dd className="font-mono text-xs text-[var(--ink)]">{result.id}</dd>
        </div>
        <div className="flex justify-between gap-4">
          <dt className="text-[var(--muted)]">Status</dt>
          <dd className="font-medium">{STATUS_LABELS[result.status]}</dd>
        </div>
      </dl>

      <p className="mt-5 text-sm leading-6 text-[var(--ink)]">
        {applicantNextStep(result.status)}
      </p>

      <button
        type="button"
        onClick={onReset}
        className="mt-8 inline-flex text-sm font-medium text-[var(--accent)] underline-offset-4 hover:underline"
      >
        Start another application
      </button>
    </div>
  );
}
