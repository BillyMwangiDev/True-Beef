// STUB. Real offline-first bidirectional sync is Phase-1 farm-app work, not scaffold work.
// This interface exists so the architecture has a clear seam to fill later.

export interface SyncEngine {
  /** Push locally-queued writes to the API when connectivity returns. */
  push(): Promise<void>;
  /** Pull server changes into the local cache. */
  pull(): Promise<void>;
}

export const sync: SyncEngine = {
  async push() {
    throw new Error("not implemented: offline sync is a Phase-1 deliverable");
  },
  async pull() {
    throw new Error("not implemented: offline sync is a Phase-1 deliverable");
  },
};
