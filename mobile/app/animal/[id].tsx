import { useLocalSearchParams } from "expo-router";
import { useEffect, useState } from "react";
import { FlatList, Text, View } from "react-native";

import { getAnimal } from "../../lib/api";

type Event = { seq: number; event_type: string; created_at: string };

export default function AnimalDetail() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const [events, setEvents] = useState<Event[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getAnimal(id)
      .then((a) => setEvents(a.events as Event[]))
      .catch((e) => setError(String(e)));
  }, [id]);

  return (
    <View style={{ flex: 1, padding: 16 }}>
      <Text style={{ fontSize: 22, fontWeight: "600", marginBottom: 12 }}>Timeline</Text>
      {error ? <Text style={{ color: "red" }}>{error}</Text> : null}
      <FlatList
        data={events}
        keyExtractor={(e) => String(e.seq)}
        renderItem={({ item }) => (
          <Text style={{ paddingVertical: 6 }}>
            #{item.seq} {item.event_type} — {item.created_at}
          </Text>
        )}
      />
    </View>
  );
}
