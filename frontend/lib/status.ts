import type { ApplicationStatus } from "@/lib/types/application";

export const STATUS_LABELS: Record<ApplicationStatus, string> = {
  NEW: "Received",
  PENDING_REVIEW: "In review",
  ACCEPTED: "Accepted",
  REJECTED: "Not accepted",
};

export type StatusAction = {
  status: ApplicationStatus;
  label: string;
  tone: "neutral" | "danger" | "positive";
  confirm: string;
};

const NEXT_ACTIONS: Record<ApplicationStatus, StatusAction[]> = {
  NEW: [
    {
      status: "PENDING_REVIEW",
      label: "Send to review",
      tone: "neutral",
      confirm: "Move this application into registrar review?",
    },
    {
      status: "REJECTED",
      label: "Decline",
      tone: "danger",
      confirm: "Decline this application? This cannot be undone from the workspace.",
    },
  ],
  PENDING_REVIEW: [
    {
      status: "ACCEPTED",
      label: "Accept",
      tone: "positive",
      confirm: "Accept this applicant? The server records the decision; a PDF is not a signature.",
    },
    {
      status: "REJECTED",
      label: "Decline",
      tone: "danger",
      confirm: "Decline this application? This cannot be undone from the workspace.",
    },
  ],
  ACCEPTED: [],
  REJECTED: [],
};

export function nextStatusActions(status: ApplicationStatus): StatusAction[] {
  return NEXT_ACTIONS[status] ?? [];
}

export function applicantNextStep(status: ApplicationStatus): string {
  switch (status) {
    case "NEW":
      return "The registrar will review your file. You do not need to resubmit unless they contact you.";
    case "PENDING_REVIEW":
      return "Your application is with the registrar. A decision will be recorded as Accepted or Not accepted.";
    case "ACCEPTED":
      return "The registrar has accepted this application. Follow any instructions they send separately.";
    case "REJECTED":
      return "This application was not accepted. Contact the institution if you need clarification.";
    default:
      return "The registrar will update this application in EduFlow.";
  }
}
