# CEO Brain Strategy page — design reference

Design tokens are inspired by the Humanoid-style strategy deck. The CEO Strategy page
reuses the palette, spacing and interaction patterns listed below.

## Palette

| Token | Value | Usage |
|-------|-------|-------|
| `--hmnd-navy` | `#06091c` | Primary text, deep surfaces |
| `--hmnd-blue` | `#4953d8` | Primary accent, CTAs, active state |
| `--hmnd-blue-dark` | `#3b44b5` | Hover state for CTAs |
| `--hmnd-bg-blue` | `rgba(73, 83, 216, 0.05)` | Subtle surfaces |
| `--hmnd-gray` | `#dfe1e2` | Dividers, soft borders |
| `--hmnd-text-dim` | `#64748b` | Secondary text |
| `--surface` | `#ffffff` | Cards, panels |
| `--bg` | `#ffffff` | Page background |
| `--border` | `#e2e8f0` | Default borders |

## Typography

- Primary font: `Outfit`, fallback to `system-ui`, `sans-serif`.
- Weights: 200, 300, 400, 500, 600.
- Hero headline: light / 400, large.
- Uppercase label: 12–14px, `--hmnd-blue`, letter-spacing 0.08em.

## Components

- **Pill button** — radius `9999px`, blue fill, white text, hover darkens.
- **Glass card** — white surface, `--border` 1px, radius 16px, subtle shadow, translate-Y on hover.
- **Right drawer** — fixed right panel, 600px desktop / full-width mobile, slides in from the right with backdrop.

## Navigation pattern

Left sidebar with:
- Logo (mint-style dot + wordmark).
- Primary "Overview" nav item.
- Group label + module nav items (one per TO-BE module).
- Mobile: sidebar becomes a toggleable overlay drawer.

## Page sections

1. **Header** — title, subtitle, top-right actions ("Roadmap 2026", "Open Strategy" external link).
2. **Module grid** — 10 tiles; clicking a tile opens the right drawer with module detail.
3. **Roadmap section** — ordered timeline of modules with deadlines; cards open the same drawer.
4. **AI Platform block** — infra/data/services/AI services/clients, one card per row.
5. **Drawer** — module detail: description, effect tag, user stories (numbered list), deadline, link to strategy.
