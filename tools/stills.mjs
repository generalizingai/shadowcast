// Render labelled stills at chosen frames (review / layout audit). Run with node from anywhere:
//   node stills.mjs <studioDir> <compositionId> <publicDir> <outDir> "<frame frame ...>"
import { createRequire } from "node:module";
import path from "node:path";
import { pathToFileURL } from "node:url";
const [, , studio, comp, publicDir, outDir, ...raw] = process.argv;
const req = createRequire(path.resolve(studio, "package.json"));
const { bundle } = await import(pathToFileURL(req.resolve("@remotion/bundler")).href);
const { renderStill, selectComposition } = await import(pathToFileURL(req.resolve("@remotion/renderer")).href);
const frames = raw.flatMap((s) => s.split(/\s+/)).filter(Boolean).map(Number);
const serveUrl = await bundle({ entryPoint: path.resolve(studio, "src/index.ts"), publicDir: path.resolve(publicDir) });
const composition = await selectComposition({ serveUrl, id: comp });
console.log("duration", composition.durationInFrames);
for (const f of frames.filter((x) => x < composition.durationInFrames)) {
  await renderStill({ composition, serveUrl, frame: f, output: path.join(outDir, `f${String(f).padStart(5, "0")}.jpg`), imageFormat: "jpeg", scale: composition.width > 1300 ? 0.5 : 1 });
}
console.log("done", frames.length);
