import React from "react";
import { Word } from "./timing";
import { LFF } from "./theme";

// Word-synced captions for vertical Shorts: groups of up to 3 words, the spoken word highlighted, numbers shown as digits.
const INTER = LFF.sans;

// Merge spoken numbers into digits for captions: "nine hundred and seventy-nine" -> 979, "two-one" -> 2–1, "twenty-sixteen" -> 2016.
const UNITS: Record<string, number> = { zero: 0, one: 1, two: 2, three: 3, four: 4, five: 5, six: 6, seven: 7, eight: 8, nine: 9, ten: 10, eleven: 11, twelve: 12, thirteen: 13, fourteen: 14, fifteen: 15, sixteen: 16, seventeen: 17, eighteen: 18, nineteen: 19 };
const TENS: Record<string, number> = { twenty: 20, thirty: 30, forty: 40, fifty: 50, sixty: 60, seventy: 70, eighty: 80, ninety: 90 };
const clean = (w: string) => w.toLowerCase().replace(/[^a-z-]/g, "");
const isNumPart = (p: string) => p in UNITS || p in TENS || p === "hundred" || p === "thousand";
const isNumWord = (w: string) => { const c = clean(w); return c !== "" && c.split("-").every(isNumPart); };
const valueOf = (ws: string[]): string => {
  const parts = ws.map(clean).filter((p) => p && p !== "and" && p !== "a").flatMap((p) => p.split("-"));
  const pt = parts.indexOf("point"); // "one point four" -> 1.4
  if (pt > 0) return `${valueOf(parts.slice(0, pt))}.${parts.slice(pt + 1).map((p) => UNITS[p] ?? "").join("")}`;
  if (parts.length === 2 && parts[0] in TENS && parts[1] in UNITS && UNITS[parts[1]] >= 10) return String(TENS[parts[0]] * 100 + UNITS[parts[1]]);
  if (parts.length === 2 && parts.every((p) => p in UNITS && UNITS[p] < 10) && ws.length === 1) return `${UNITS[parts[0]]}–${UNITS[parts[1]]}`;
  const big = parts.includes("hundred") || parts.includes("thousand");
  // "twenty thirty" -> 2030, "twenty twenty-seven" -> 2027
  if (!big && ws.length === 2 && parts[0] in TENS && parts[1] in TENS) return String(TENS[parts[0]] * 100 + Number(valueOf(parts.slice(1))));
  // "one thirty-eight" -> 138
  if (!big && ws.length === 2 && parts[0] in UNITS && UNITS[parts[0]] < 10 && parts[1] in TENS) return String(UNITS[parts[0]] * 100 + Number(valueOf(parts.slice(1))));
  let total = 0, cur = 0;
  for (const p of parts) { if (p in UNITS) cur += UNITS[p]; else if (p in TENS) cur += TENS[p]; else if (p === "hundred") cur = (cur || 1) * 100; else if (p === "thousand") { total += (cur || 1) * 1000; cur = 0; } }
  return (total + cur).toLocaleString("en-US");
};
const mergeNumbers = (words: Word[]): Word[] => {
  const out: Word[] = [];
  for (let i = 0; i < words.length; i++) {
    const w = words[i];
    if (clean(w.w) === "one-nil") { out.push({ ...w, w: "1–0" + w.w.replace(/[A-Za-z-]/g, "") }); continue; }
    const startsA = clean(w.w) === "a" && words[i + 1] && clean(words[i + 1].w) === "hundred";
    if (!isNumWord(w.w) && !startsA) { out.push(w); continue; }
    let j = i; const run = [w.w];
    while (j + 1 < words.length && !/[.?!,:]$/.test(words[j].w) && (isNumWord(words[j + 1].w) || (clean(words[j + 1].w) === "and" && !!words[j + 2] && isNumWord(words[j + 2].w) && /hundred|thousand/.test(clean(words[j].w))) || (clean(words[j + 1].w) === "point" && !!words[j + 2] && isNumWord(words[j + 2].w)))) { j++; run.push(words[j].w); }
    const punct = (words[j].w.match(/[.?!,:]+$/) || [""])[0];
    let v = valueOf(run);
    const next = clean(words[j + 1]?.w ?? "");
    if (/^2,0\d\d$/.test(v) && clean(run[0]) === "two" && !punct.includes(",") && !/^(dollars?|people|units|copies|shares|fans|tickets|miles|times|pounds|euros)$/.test(next)) v = v.replace(",", "");
    out.push({ w: v + punct, s: w.s, e: words[j].e }); i = j;
  }
  return out;
};

// Display fixes: spelled acronyms "I-M-F" -> IMF, plus per-episode phrase merges like [["S","and","P"], "S&P"].
export type Fix = [string[], string];

// Spoken years -> digits (1900-2099, every common reading), applied before the generic number merger.
const U = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"];
const T = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"];
const two = (n: number): string[] => (n < 20 ? [U[n]] : n % 10 ? [T[Math.floor(n / 10)], U[n % 10]] : [T[n / 10]]);
const YEARS: Fix[] = [];
for (let y = 1900; y <= 2099; y++) {
  const hi = Math.floor(y / 100), lo = y % 100;
  const head = hi === 19 ? ["nineteen"] : ["twenty"];
  if (lo === 0) { if (hi === 19) YEARS.push([["nineteen", "hundred"], String(y)]); }
  else if (lo < 10) {
    YEARS.push([[...head, "oh", U[lo]], String(y)]);
  } else {
    YEARS.push([[...head, ...two(lo)], String(y)]);
  }
}
YEARS.sort((a, b) => b[0].length - a[0].length);
const applyFixes = (words: Word[], fixes: Fix[]): Word[] => {
  const out: Word[] = [];
  for (let i = 0; i < words.length; i++) {
    const hit = fixes.find(([ph]) => ph.every((p, k) => words[i + k] && words[i + k].w.replace(/[^A-Za-z0-9'-]/g, "").toLowerCase() === p.toLowerCase()));
    if (hit) { const last = words[i + hit[0].length - 1]; out.push({ w: hit[1] + (last.w.match(/[.?!,:]+$/) || [""])[0], s: words[i].s, e: last.e }); i += hit[0].length - 1; continue; }
    const w = words[i]; out.push(/^"?([A-Z]-)+[A-Z]\b/.test(w.w) ? { ...w, w: w.w.replace(/([A-Z])-(?=[A-Z])/g, "$1") } : w);
  }
  return out;
};

export const Captions: React.FC<{ words: Word[]; t: number; lead: number; accent: string; fixes: Fix[]; size?: number }> = ({ words: raw, t, lead, accent, fixes, size = 92 }) => {
  const words = React.useMemo(() => mergeNumbers(applyFixes(applyFixes(raw, fixes), YEARS)), [raw, fixes]);
  // group into chunks of up to 3 words, breaking on sentence ends
  const chunks: Word[][] = []; let cur: Word[] = [];
  words.forEach((w) => { cur.push(w); if (cur.length === 3 || /[.?!,:]$/.test(w.w)) { chunks.push(cur); cur = []; } });
  if (cur.length) chunks.push(cur);
  const tt = t - lead;
  const ch = chunks.find((c) => tt >= c[0].s - 0.05 && tt <= c[c.length - 1].e + 0.15);
  if (!ch) return null;
  return (
    <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "center", gap: `0 ${Math.round(size * 0.24)}px`, padding: "0 60px" }}>
      {ch.map((w, i) => { const on = tt >= w.s - 0.03 && tt <= w.e + 0.05;
        return <span key={i} style={{ fontFamily: INTER, fontWeight: 900, fontSize: size, color: on ? accent : "#fff", WebkitTextStroke: `${Math.round(size * 0.15)}px #000`, paintOrder: "stroke fill",
          textTransform: "uppercase", display: "inline-block", lineHeight: 1.15 }}>{w.w.replace(/[",]/g, "").replace(/([a-z])-([a-z])/gi, "$1 $2")}</span>; })}
    </div>
  );
};

