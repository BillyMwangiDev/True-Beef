import { useRouter } from "expo-router";
import { useState } from "react";
import { Button, Text, TextInput, View } from "react-native";

import { createAnimal } from "../lib/api";
import { cacheAnimal, initDb } from "../lib/db";

export default function NewAnimal() {
  const router = useRouter();
  const [breed, setBreed] = useState("Angus");
  const [birthDate, setBirthDate] = useState("2025-03-01");
  const [error, setError] = useState<string | null>(null);

  async function submit() {
    try {
      initDb();
      const animal = await createAnimal({
        breed,
        sex: "M",
        birth_date: birthDate,
        us_born: true,
        us_raised: true,
      });
      cacheAnimal({ id: animal.id, breed: animal.breed, birth_date: animal.birth_date });
      router.replace("/");
    } catch (e) {
      setError(String(e));
    }
  }

  return (
    <View style={{ flex: 1, padding: 16, gap: 12 }}>
      <Text style={{ fontSize: 22, fontWeight: "600" }}>Log animal</Text>
      <TextInput value={breed} onChangeText={setBreed} placeholder="Breed"
        style={{ borderWidth: 1, padding: 8 }} />
      <TextInput value={birthDate} onChangeText={setBirthDate} placeholder="Birth date (YYYY-MM-DD)"
        style={{ borderWidth: 1, padding: 8 }} />
      <Button title="Save" onPress={submit} />
      {error ? <Text style={{ color: "red" }}>{error}</Text> : null}
    </View>
  );
}
