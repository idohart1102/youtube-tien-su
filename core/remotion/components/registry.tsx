import React from 'react';
import { delayRender, continueRender } from 'remotion';
import { TRex } from '../lib/trex';
import { Mammal, Turtle, Bird, SAUROPOD, TRICERATOPS, STEGOSAURUS, Silhouette, Pterosaur, Asteroid, Earth, FishFossil, SkullFossil, Fern, Conifer, Cycad } from '../lib/creatures';

// Thư viện sinh vật vẽ tay (SVG). Thêm sinh vật mới: viết vào lib/ rồi đăng ký 1 dòng ở đây.
// Hàm nhận f (frame) và trả về <g>; toạ độ gốc tuỳ hình, SizeCompare tự đo kích thước.
export const CREATURES: Record<string, (f: number, opt?: Record<string, any>) => React.ReactNode> = {
  trex: (f, o) => <TRex phase={f / 30} jaw={o?.jaw ?? 0} />,
  mammal: (f) => <Mammal t={f / 30} />,
  turtle: (f) => <Turtle t={f / 30} />,
  bird: (f) => <Bird peck={(Math.sin(f / 8) + 1) / 2} />,
  pterosaur: (f) => <Pterosaur flap={Math.sin(f / 6)} />,
  sauropod: (_f, o) => <Silhouette d={SAUROPOD} fill={o?.fill} rim={o?.rim} flip={o?.flip} />,
  triceratops: (_f, o) => <Silhouette d={TRICERATOPS} fill={o?.fill} rim={o?.rim} flip={o?.flip} />,
  stegosaurus: (_f, o) => <Silhouette d={STEGOSAURUS} fill={o?.fill} rim={o?.rim} flip={o?.flip} />,
  asteroid: (f) => <Asteroid r={120} rot={f * 0.4} />,
  earth: (f) => <Earth R={300} spin={f * 0.3} />,
  fish_fossil: () => <FishFossil />,
  skull_fossil: () => <SkullFossil />,
  fern: (f) => <Fern sway={Math.sin(f / 30)} />,
  conifer: (f) => <Conifer sway={Math.sin(f / 40)} />,
  cycad: (f) => <Cycad sway={Math.sin(f / 35)} />,
  human: () => (
    // người cao 170 đơn vị, chân chạm y=0
    <path d="M0,-170 a14,14 0 1,1 0.1,0 Z M-16,-140 L16,-140 L22,-80 L12,-80 L10,-2 L2,-2 L0,-70 L-2,-2 L-10,-2 L-12,-80 L-22,-80 Z" fill="#1c140e" />
  ),
};

export const creature = (name: string, f: number, opt?: Record<string, any>) => {
  const fn = CREATURES[name];
  if (fn) return fn(f, opt);
  // Chưa có hình: vẽ khối tạm để không vỡ render, validate_scenes.py sẽ cảnh báo
  return <ellipse cx={0} cy={-60} rx={160} ry={60} fill="#5a4636" stroke="#1c140e" strokeWidth={4} />;
};

// Đo khung hình của sinh vật rồi dời gốc toạ độ về điểm giữa-đáy (chân chạm y=0)
export const Grounded: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const ref = React.useRef<SVGGElement>(null);
  const [off, setOff] = React.useState<[number, number] | null>(null);
  const [handle] = React.useState(() => delayRender('grounded'));
  React.useLayoutEffect(() => {
    if (ref.current) {
      const b = ref.current.getBBox();
      setOff([-(b.x + b.width / 2), -(b.y + b.height)]);
    } else continueRender(handle);
  }, [handle]);
  React.useEffect(() => {
    if (off) continueRender(handle);
  }, [off, handle]);
  return <g ref={ref} transform={off ? `translate(${off[0]},${off[1]})` : undefined}>{children}</g>;
};
