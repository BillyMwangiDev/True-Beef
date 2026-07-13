import * as SQLite from "expo-sqlite";

export type CachedAnimal = { id: string; breed: string; birth_date: string };

const db = SQLite.openDatabaseSync("truebeef.db");

export function initDb(): void {
  db.execSync(
    "CREATE TABLE IF NOT EXISTS animals (id TEXT PRIMARY KEY, breed TEXT, birth_date TEXT)"
  );
}

export function cacheAnimal(a: CachedAnimal): void {
  db.runSync(
    "INSERT OR REPLACE INTO animals (id, breed, birth_date) VALUES (?, ?, ?)",
    a.id,
    a.breed,
    a.birth_date
  );
}

export function getCachedAnimals(): CachedAnimal[] {
  return db.getAllSync<CachedAnimal>("SELECT id, breed, birth_date FROM animals");
}
