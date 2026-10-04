import { makeEpisode } from "../../kit/episode";
import { vFramesFor } from "../../kit/vshort";
import type { EpisodeEntry } from "..";
import { W_, S_ } from "./data";
import { SHOTS } from "./shots";
import { PREFIX1, Short1 } from "./short1";
import { ThumbA } from "./thumbs";

// Reference episode. Every episode folder has the same files: data.ts, shots*.tsx, short1.tsx, short2.tsx, thumbs.tsx, index.tsx.
// Render with --public-dir=demo-episode.
const ep = makeEpisode({ words: W_, sections: S_, shots: SHOTS, rail: "countdown", total: 3 });

const entry: EpisodeEntry = {
  id: "Demo", Long: ep.Episode, frames: ep.frames,
  shorts: [{ id: "DemoShort1", C: Short1, frames: vFramesFor(S_, PREFIX1) }],
  thumbs: [{ id: "DemoThumbA", C: ThumbA }],
};
export default entry;
