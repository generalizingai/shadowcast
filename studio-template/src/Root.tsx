import React from "react";
import { Composition } from "remotion";
import { FPS, H, W } from "./kit/theme";
import { EPISODES } from "./episodes";

export const Root: React.FC = () => (
  <>
    {EPISODES.map((e) => (
      <React.Fragment key={e.id}>
        <Composition id={e.id} component={e.Long} durationInFrames={e.frames} fps={FPS} width={W} height={H} />
        {e.shorts.map((s) => <Composition key={s.id} id={s.id} component={s.C} durationInFrames={s.frames} fps={FPS} width={1080} height={1920} />)}
        {e.thumbs.map((t) => <Composition key={t.id} id={t.id} component={t.C} durationInFrames={1} fps={FPS} width={1280} height={720} />)}
      </React.Fragment>
    ))}
  </>
);
