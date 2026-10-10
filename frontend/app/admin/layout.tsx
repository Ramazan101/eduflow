import type { Metadata } from "next";
import type { ReactNode } from "react";

import { AdminShell } from "@/components/admin/admin-shell";

export const metadata: Metadata = {
  title: "Applications — EduFlow Admin",
  description: "Review student applications and generate training contracts.",
};

export default function AdminLayout({ children }: { children: ReactNode }) {
  return <AdminShell>{children}</AdminShell>;
}
