import z from "zod";

export const forgotPasswordSchema = z.object({
  email: z.email("Email inválido"),
});
export type ForgotPasswordFormData = z.infer<typeof forgotPasswordSchema>;
