import type { ApplicationFormValues } from "@/lib/validations/application";
import type {
  ApplicationDetail,
  ApplicationListResponse,
  ApplicationStatus,
} from "@/lib/types/application";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type ApplicationCreatedResponse = {
  id: string;
};

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

async function requestJson<T>(
  path: string,
  init: RequestInit,
  fallbackMessage: string,
): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, init);
  } catch {
    throw new ApiError(
      "Could not reach the EduFlow API. Confirm the backend is running on port 8000.",
      0,
    );
  }

  if (!response.ok) {
    let message = fallbackMessage;
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

export async function submitApplication(
  values: ApplicationFormValues,
): Promise<ApplicationCreatedResponse> {
  return requestJson<ApplicationCreatedResponse>(
    "/api/v1/applications/",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(values),
    },
    "We could not submit your application. Please try again.",
  );
}

export async function listApplications(params?: {
  status?: ApplicationStatus;
  course_name?: string;
  limit?: number;
  offset?: number;
}): Promise<ApplicationListResponse> {
  const search = new URLSearchParams();
  if (params?.status) {
    search.set("status", params.status);
  }
  if (params?.course_name) {
    search.set("course_name", params.course_name);
  }
  search.set("limit", String(params?.limit ?? 20));
  search.set("offset", String(params?.offset ?? 0));

  return requestJson<ApplicationListResponse>(
    `/api/v1/applications/?${search.toString()}`,
    { method: "GET" },
    "We could not load applications.",
  );
}

export async function getApplication(
  applicationId: string,
): Promise<ApplicationDetail> {
  return requestJson<ApplicationDetail>(
    `/api/v1/applications/${applicationId}`,
    { method: "GET" },
    "We could not load this application.",
  );
}

export async function generateContract(
  applicationId: string,
): Promise<ApplicationDetail> {
  return requestJson<ApplicationDetail>(
    `/api/v1/applications/${applicationId}/generate-contract`,
    { method: "POST" },
    "We could not generate the contract.",
  );
}
