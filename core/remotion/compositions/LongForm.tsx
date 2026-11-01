import React from 'react';
import { AbsoluteFill, Audio, Sequence, staticFile, useCurrentFrame } from 'remotion';
import '@fontsource/noto-serif-jp/400.css';
import '@fontsource/noto-serif-jp/700.css';
// Be Vietnam Pro: font tiếng Việt cho kênh vi (gói fontsource đã gồm bộ ký tự tiếng Việt)
import '@fontsource/be-vietnam-pro/400.css';
import '@fontsource/be-vietnam-pro/600.css';
import '@fontsource/be-vietnam-pro/800.css';
import { clamp } from '../lib/lib';
import { EpisodeProps, DEFAULT_THEME } from '../types';
import { ThemeCtx, SceneProps } from '../components/common';
import { KenBurns } from '../components/KenBurns';
import { TitleCard } from '../components/TitleCard';
import { Creature } from '../components/Creature';
import { SizeCompare } from '../components/SizeCompare';
import { GeoClock } from '../components/GeoClock';
import { MapDrift } from '../components/MapDrift';
import { Overlay, Caption, Subtitles, Badges, Cards, AiNotice } from '../components/Overlay';
import { PhotoCard } from '../components/PhotoCard';
import { Parallax } from '../components/Parallax';
import { Collage } from '../components/Collage';
import { GeoMap } from '../components/GeoMap';
import { Annotate } from '../components/Annotate';
import { SceneFx } from '../components/SceneFx';
import { Stage } from '../components/Stage';
import { FossilReveal } from '../components/FossilReveal';
import { StrataWipe } from '../components/StrataWipe';

// Tên component trong scenes.json → component React. Thêm component mới: đăng ký ở đây + enum trong scenes.schema.json
export const COMPONENTS: Record<string, React.FC<SceneProps>> = { KenBurns, TitleCard, Creature, SizeCompare, GeoClock, MapDrift, PhotoCard, Parallax, Collage, GeoMap, Stage, FossilReveal };

const FADE = 12;

// Chuyển cảnh theo scene.transition: "fade" (mặc định, hòa tan 12 khung), "dip" (nháy tối, dùng khi sang chặng), "cut"
const Fader: React.FC<{ children: React.ReactNode; first: boolean; kind?: string }> = ({ children, first, kind }) => {
  const f = useCurrentFrame();
  if (first || kind === 'cut') return <AbsoluteFill>{children}</AbsoluteFill>;
  if (kind === 'dip') return <AbsoluteFill style={{ opacity: f < FADE ? 0 : clamp((f - FADE) / 9) }}>{children}</AbsoluteFill>;
  return <AbsoluteFill style={{ opacity: clamp(f / FADE) }}>{children}</AbsoluteFill>;
};

export const LongForm: React.FC<EpisodeProps> = ({ fps, scenes, theme, audio, music, grainAsset, subs }) => {
  const th = { ...DEFAULT_THEME, ...theme, palette: { ...DEFAULT_THEME.palette, ...(theme?.palette || {}) } };
  let start = 0;
  const total = Math.round(scenes.reduce((a, x) => a + x.duration_s, 0) * fps);
  return (
    <ThemeCtx.Provider value={th}>
      <AbsoluteFill style={{ background: th.palette.bg }}>
        {audio ? <Audio src={staticFile(audio)} /> : null}
        {music ? <Audio src={staticFile(music.src)} loop volume={(fr) => music.volume * Math.min(1, fr / (2 * fps), (total - fr) / (2 * fps))} /> : null}
        {scenes.map((s, i) => {
          const from = Math.round(start * fps);
          start += s.duration_s;
          const dur = Math.round(start * fps) - from;
          const C = COMPONENTS[s.component] || KenBurns;
          const lead = i && s.transition !== 'cut' ? FADE : 0; // cut: không chồng cảnh trước, đúng mốc thời gian
          return (
            <Sequence key={s.id} from={from - lead} durationInFrames={dur + lead}>
              <Fader first={i === 0} kind={s.transition}>
                <SceneFx p={s.props || {}} lead={lead} fps={fps}>
                  <C dur={dur + lead} asset={s.asset} props={s.props || {}} lead={lead} />
                </SceneFx>
                {s.props?.strata_in ? <StrataWipe s={s.props.strata_in} fps={fps} lead={lead} /> : null}
                <Sequence from={lead}>
                  <Annotate items={s.props?.annotate} fps={fps} />
                  <Cards items={s.props?.cards} fps={fps} />
                  <Badges items={s.props?.badges} fps={fps} />
                </Sequence>
                {subs ? null : <Caption text={s.narration} dur={dur + lead} />}
              </Fader>
            </Sequence>
          );
        })}
        <Overlay grainAsset={grainAsset} />
        <AiNotice total={total} fps={fps} />
        {subs && th.subtitles !== false ? <Subtitles cues={subs} fps={fps} /> : null}
      </AbsoluteFill>
    </ThemeCtx.Provider>
  );
};
