export const APPLICATION_STATUSES = [
  "NEW",
  "PENDING_REVIEW",
  "ACCEPTED",
  "REJECTED",
] as const;

export type ApplicationStatus = (typeof APPLICATION_STATUSES)[number];

export type Institution = {
  id: string;
  name: string;
  slug: string;
  created_at: string;
  updated_at: string;
};

export type Program = {
  id: string;
  institution_id: string;
  name: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

export type RequirementProfile = {
  id: string;
  institution_id: string;
  name: string;
  source_reference: string;
  verification_status: "UNVERIFIED" | "VERIFIED" | "RETIRED";
  created_at: string;
  updated_at: string;
};

export type StatusHistoryEntry = {
  id: string;
  application_id: string;
  from_status: ApplicationStatus | null;
  to_status: ApplicationStatus;
  note: string | null;
  changed_by_id: string | null;
  created_at: string;
  updated_at: string;
};

export type Application = {
  id: string;
  program_id: string;
  requirement_profile_id: string;
  applicant_name: string;
  birth_date: string;
  phone: string;
  email: string;
  status: ApplicationStatus;
  created_at: string;
  updated_at: string;
};

export type ApplicationDetail = Application & {
  admin_notes: string | null;
  status_history: StatusHistoryEntry[];
};

export type ApplicationListResponse = {
  items: Application[];
  total: number;
  limit: number;
  offset: number;
};

export type ApplicationCreatedResponse = {
  id: string;
  status: ApplicationStatus;
};

export type DocumentMetadata = {
  id: string;
  application_id: string;
  template_key: string;
  template_version: string;
  generation_status: "SUCCESS" | "FAILED";
  error_code: string | null;
  created_at: string;
  updated_at: string;
};

export type TokenResponse = {
  access_token: string;
  token_type: string;
  expires_in: number;
};
