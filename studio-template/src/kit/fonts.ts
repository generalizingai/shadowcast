// Load a Google Font with only the weights/styles it actually has (asking for a missing weight throws in Remotion).
type Info = { fontFamily: string; fonts: Record<string, Record<string, Record<string, string>>> };
type GF = { getInfo: () => Info; loadFont: (style: string, o: { weights: string[]; subsets: string[] }) => unknown };

export const gfont = (mod: unknown, want: string[], style: "normal" | "italic" = "normal"): string => {
  const m = mod as GF;
  const info = m.getInfo();
  const st = info.fonts[style] ? style : "normal";
  const avail = Object.keys(info.fonts[st]);
  const hit = want.filter((w) => avail.includes(w));
  const weights = hit.length ? hit : [avail.includes("400") ? "400" : avail[avail.length - 1]];
  const latin = weights.every((w) => "latin" in info.fonts[st][w]);
  m.loadFont(st, { weights, subsets: [latin ? "latin" : Object.keys(info.fonts[st][weights[0]])[0]] });
  return info.fontFamily;
};
