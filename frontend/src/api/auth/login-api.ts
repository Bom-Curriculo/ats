import { APICONNECTBACKEND } from "@/helpers/api-connect";
import type { LoginType } from "@/types/login-type";

export async function LoginApi(dataLogin: LoginType) {
  const response = await fetch(`${APICONNECTBACKEND}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify(dataLogin),
  });

  if (!response.ok) {
    throw new Error("Error to login try again");
  }

  const res = await response.json();

  localStorage.setItem("token", res.data.token);

  return res;
}