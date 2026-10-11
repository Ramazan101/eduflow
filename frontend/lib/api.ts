import { clearAdminToken, getAdminToken } from "@/lib/session";
import type { ApplicationDetailsValues } from "@/lib/validations/application";
import type {
  ApplicationCreatedResponse,
  ApplicationDetail,
  ApplicationListResponse,
  ApplicationStatus,
  DocumentMetadata,
  Institution,
  Program,
  RequirementProfile,
  TokenResponse,
} from "@/lib/types/application";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type ApiErrorBody = {
  detail?: unknown;
};

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

function extractDetail(detail: unknown): string | null {
  if (typeof detail === "string") {
    return detail;
  }
  if (Array.isArray(detail) && detail.length > 0) {
    const first = detail[0] as { msg?: string };
    if (typeof first?.msg === "string") {
      return first.msg;
    }
  }
  return null;
}

function handleUnauthorized(): void {
  clearAdminToken();
  if (typeof window === "undefined") {
    return;
  }
  const path = window.location.pathname;
  if (path.startsWith("/admin") && path !== "/admin/login") {
    window.location.assign("/admin/login?expired=1");
  }
}

async function requestJson<T>(
  path: string,
  init: RequestInit,
  fallbackMessage: string,
  authenticated = false,
): Promise<T> {
  const headers = new Headers(init.headers);
  if (authenticated) {
    const token = getAdminToken();
    if (!token) {
      handleUnauthorized();
      throw new ApiError("Please sign in to continue.", 401);
    }
    headers.set("Authorization", `Bearer ${token}`);
  }

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, { ...init, headers });
  } catch {
    throw new ApiError(
      "Could not reach the EduFlow API. Confirm the backend is running.",
      0,
    );
  }

  if (response.status === 401 && authenticated) {
    handleUnauthorized();
  }

    if (!response.ok) {
    let message = fallbackMessage;
    if (response.status === 401 && authenticated) {
      message = "Please sign in to continue.";
    } else if (response.status === 403) {
      message = "You are not allowed to perform this action.";
    }
    try {
      const body = (await response.json()) as ApiErrorBody;
      const detail = extractDetail(body.detail);
      if (detail) {
        message = detail;
      }
    } catch {
      // Keep the fallback message when the error payload is not JSON.
    }
    throw new ApiError(message, response.status);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export async function listInstitutions(): Promise<Institution[]> {
  return requestJson(
    "/api/v1/institutions",
    { method: "GET" },
    "We could not load institutions.",
  );
}

export async function listPrograms(institutionId?: string): Promise<Program[]> {
  const search = new URLSearchParams();
  if (institutionId) {
    search.set("institution_id", institutionId);
  }
  const suffix = search.size ? `?${search.toString()}` : "";
  return requestJson(
    `/api/v1/programs${suffix}`,
    { method: "GET" },
    "We could not load programmes.",
  );
}

export async function listRequirementProfiles(
  institutionId?: string,
): Promise<RequirementProfile[]> {
  const search = new URLSearchParams();
  if (institutionId) {
    search.set("institution_id", institutionId);
  }
  const suffix = search.size ? `?${search.toString()}` : "";
  return requestJson(
    `/api/v1/requirement-profiles${suffix}`,
    { method: "GET" },
    "We could not load admission requirements.",
  );
}

export async function submitApplication(payload: {
  program_id: string;
  requirement_profile_id: string;
  applicant_name: string;
  birth_date: string;
  phone: string;
  email: string;
}): Promise<ApplicationCreatedResponse> {
  return requestJson(
    "/api/v1/applications/",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    },
    "We could not submit your application. Please try again.",
  );
}

export async function loginAdmin(
  email: string,
  password: string,
): Promise<TokenResponse> {
  return requestJson(
    "/api/v1/auth/login",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    },
    "Could not sign in.",
  );
}

export async function listApplications(params?: {
  status?: ApplicationStatus;
  program_id?: string;
  limit?: number;
  offset?: number;
}): Promise<ApplicationListResponse> {
  const search = new URLSearchParams();
  if (params?.status) {
    search.set("status", params.status);
  }
  if (params?.program_id) {
    search.set("program_id", params.program_id);
  }
  search.set("limit", String(params?.limit ?? 20));
  search.set("offset", String(params?.offset ?? 0));
  return requestJson(
    `/api/v1/applications/?${search.toString()}`,
    { method: "GET" },
    "We could not load applications.",
    true,
  );
}

export async function getApplication(
  applicationId: string,
): Promise<ApplicationDetail> {
  return requestJson(
    `/api/v1/applications/${applicationId}`,
    { method: "GET" },
    "We could not load this application.",
    true,
  );
}

export async function changeApplicationStatus(
  applicationId: string,
  status: ApplicationStatus,
  note?: string,
): Promise<ApplicationDetail> {
  return requestJson(
    `/api/v1/applications/${applicationId}/status`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status, note: note || null }),
    },
    "The server rejected this status change.",
    true,
  );
}

export async function listDocuments(
  applicationId: string,
): Promise<DocumentMetadata[]> {
  return requestJson(
    `/api/v1/applications/${applicationId}/documents`,
    { method: "GET" },
    "We could not load documents.",
    true,
  );
}

export async function generateDocument(
  applicationId: string,
): Promise<DocumentMetadata> {
  return requestJson(
    `/api/v1/applications/${applicationId}/documents`,
    { method: "POST" },
    "We could not generate the document.",
    true,
  );
}

export async function downloadDocument(
  applicationId: string,
  documentId: string,
): Promise<void> {
  const token = getAdminToken();
  if (!token) {
    handleUnauthorized();
    throw new ApiError("Please sign in to continue.", 401);
  }
  let response: Response;
  try {
    response = await fetch(
      `${API_BASE_URL}/api/v1/applications/${applicationId}/documents/${documentId}/download`,
      { headers: { Authorization: `Bearer ${token}` } },
    );
  } catch {
    throw new ApiError(
      "Could not reach the EduFlow API. Confirm the backend is running.",
      0,
    );
  }
  if (response.status === 401) {
    handleUnauthorized();
    throw new ApiError("Please sign in to continue.", 401);
  }
  if (!response.ok) {
    throw new ApiError("We could not download this document.", response.status);
  }
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `eduflow-demo-${documentId}.pdf`;
  link.click();
  URL.revokeObjectURL(url);
}

export type { ApplicationDetailsValues };
