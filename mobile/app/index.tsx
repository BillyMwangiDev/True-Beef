import { Link } from "expo-router";
import { useEffect, useState } from "react";
import { FlatList, Text, View } from "react-native";

import { getCachedAnimals, initDb, type CachedAnimal } from "../lib/db";

export default function HerdList() {
  const [animals, setAnimals] = useState<CachedAnimal[]>([]);

  useEffect(() => {
    initDb();
    setAnimals(getCachedAnimals());
  }, []);

  return (
    <View style={{ flex: 1, padding: 16 }}>
      <Text style={{ fontSize: 22, fontWeight: "600", marginBottom: 12 }}>Herd</Text>
      <Link href="/new">+ Log animal</Link>
      <FlatList
        data={animals}
        keyExtractor={(a) => a.id}
        renderItem={({ item }) => (
          <Link href={`/animal/${item.id}`}>
            <Text style={{ paddingVertical: 8 }}>
              {item.breed} — {item.birth_date}
            </Text>
          </Link>
        )}
        ListEmptyComponent={<Text style={{ marginTop: 16 }}>No animals yet.</Text>}
      />
    </View>
  );
}
