import type { Metadata } from "next";
import type { ReactNode } from "react";

import { AdminGate } from "@/components/admin/admin-gate";

export const metadata: Metadata = {
  title: "Registrar — EduFlow",
  description: "Review applications and record decisions.",
};

export default function AdminLayout({ children }: { children: ReactNode }) {
  return <AdminGate>{children}</AdminGate>;
}
