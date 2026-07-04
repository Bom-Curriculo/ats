import { APICONNECTBACKEND } from "@/helpers/api-connect";
import type { UserType } from "@/types/user-type";


export async function getUser(): Promise<UserType> {
  const token = localStorage.getItem("token");

  const response = await fetch(`${APICONNECTBACKEND}/client/user`, {
    method: "GET",
    headers: {
      "Accept": "application/json",
      "Authorization": `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error("Not authenticated");
  }

  const json = await response.json();
  return json.data.user;
}