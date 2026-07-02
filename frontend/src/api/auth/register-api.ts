import { APICONNECTBACKEND } from "@/helpers/api-connect";
import type { RegisterType } from "@/types/register-type";


export async function RegisterApi(dataRegister: RegisterType) {
  const response = await fetch(`${APICONNECTBACKEND}/auth/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include",
    body: JSON.stringify(dataRegister),
  });

  if (!response.ok) {
    throw new Error("Error to register try again");
  }
  return response.json();
}
