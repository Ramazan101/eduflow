import { z } from "zod";

export const PHONE_PATTERN = /^\+[1-9]\d{7,14}$/;

export const applicationDetailsSchema = z.object({
  applicant_name: z
    .string()
    .trim()
    .min(1, "Full name is required")
    .max(255, "Full name is too long"),
  phone: z
    .string()
    .trim()
    .regex(
      PHONE_PATTERN,
      "Enter a valid international phone number, e.g. +77011234567",
    ),
  email: z.string().trim().email("Enter a valid email address"),
  birth_date: z
    .string()
    .min(1, "Birth date is required")
    .refine((value) => !Number.isNaN(Date.parse(value)), "Enter a valid date")
    .refine((value) => {
      const selected = new Date(`${value}T00:00:00`);
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      return selected <= today;
    }, "Birth date cannot be in the future"),
});

export type ApplicationDetailsValues = z.infer<typeof applicationDetailsSchema>;

export const loginSchema = z.object({
  email: z.string().trim().email("Enter a valid work email"),
  password: z.string().min(1, "Password is required"),
});

export type LoginValues = z.infer<typeof loginSchema>;
