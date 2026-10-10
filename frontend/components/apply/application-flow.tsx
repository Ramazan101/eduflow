"use client";

import { useState } from "react";

import { ApplicationForm } from "@/components/apply/application-form";
import { SuccessState } from "@/components/apply/success-state";

export function ApplicationFlow() {
  const [submitted, setSubmitted] = useState(false);

  if (submitted) {
    return <SuccessState />;
  }

  return <ApplicationForm onSuccess={() => setSubmitted(true)} />;
}
