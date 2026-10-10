export const APPLICATION_STATUSES = [
  "NEW",
  "PENDING_REVIEW",
  "CONTRACT_GENERATED",
  "ACCEPTED",
  "REJECTED",
] as const;

export type ApplicationStatus = (typeof APPLICATION_STATUSES)[number];

export type Application = {
  id: string;
  applicant_name: string;
  birth_date: string;
  phone: string;
  email: string;
  course_name: string;
  status: ApplicationStatus;
  admin_notes: string | null;
  created_at: string;
  updated_at: string;
};

export type ApplicationDocument = {
  id: string;
  application_id: string;
  doc_type: "QUESTIONNAIRE" | "CONTRACT";
  file_path: string;
  created_at: string;
  updated_at: string;
};

export type ApplicationDetail = Application & {
  documents: ApplicationDocument[];
};

export type ApplicationListResponse = {
  items: Application[];
  total: number;
  limit: number;
  offset: number;
};

export const CONTRACT_ELIGIBLE_STATUSES: readonly ApplicationStatus[] = [
  "NEW",
  "PENDING_REVIEW",
];

export function canGenerateContract(status: ApplicationStatus): boolean {
  return CONTRACT_ELIGIBLE_STATUSES.includes(status);
}
