import words from "../../../demo-episode/audio/words_tight.json";
import sections from "../../../demo-episode/audio/sections_tight.json";
import type { Word } from "../../kit/timing";
import type { Section } from "../../kit/episode";

// The episode's timed VO. In a channel workspace these paths point at ../../../../episodes/<NN-slug>/audio/.
export const W_ = words as Word[];
export const S_ = sections as Section[];
