import type React from "react";

// Registry of every episode in this channel. The episode skill appends one import + one entry per episode.
// Composition ids: <ID> (16:9 long), <ID>Short1 / <ID>Short2 (9:16), <ID>ThumbA/B/C (1280x720).
export type EpisodeEntry = {
  id: string;
  Long: React.FC; frames: number;
  shorts: { id: string; C: React.FC; frames: number }[];
  thumbs: { id: string; C: React.FC }[];
};

import demo from "./_demo";

export const EPISODES: EpisodeEntry[] = [demo];
