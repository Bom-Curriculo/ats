import { APICONNECTBACKEND } from "@/helpers/api-connect";
import type { ForgotPasswordType } from "@/types/forgot-password-type";

export async function ForgotPasswordApi(data: ForgotPasswordType) {
  const response = await fetch(`${APICONNECTBACKEND}/auth/forgot-password`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error("Não foi possível enviar o link de recuperação, tente novamente");
  }

  return response.json();
}
