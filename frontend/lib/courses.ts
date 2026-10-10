export const COURSE_OPTIONS = [
  "Applied Data Engineering",
  "Product Leadership Intensive",
  "Cloud Architecture for Teams",
  "AI Operations Bootcamp",
  "Revenue Operations Foundations",
] as const;

export type CourseName = (typeof COURSE_OPTIONS)[number];
