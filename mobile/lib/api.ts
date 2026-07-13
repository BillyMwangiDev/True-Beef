import type { paths } from "./generated/api-types";

const BASE_URL = process.env.EXPO_PUBLIC_API_URL ?? "http://localhost:8000";

type Animal =
  paths["/animals/{animal_id}"]["get"]["responses"]["200"]["content"]["application/json"];
type AnimalCreate =
  paths["/animals"]["post"]["requestBody"]["content"]["application/json"];

export async function listAnimals(): Promise<Animal[]> {
  // No list endpoint in the scaffold; the herd list reads from the local cache (db.ts).
  throw new Error("use db.getCachedAnimals()");
}

export async function createAnimal(body: AnimalCreate): Promise<Animal> {
  const res = await fetch(`${BASE_URL}/animals`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`createAnimal failed: ${res.status}`);
  return res.json();
}

export async function getAnimal(id: string): Promise<Animal> {
  const res = await fetch(`${BASE_URL}/animals/${id}`);
  if (!res.ok) throw new Error(`getAnimal failed: ${res.status}`);
  return res.json();
}
