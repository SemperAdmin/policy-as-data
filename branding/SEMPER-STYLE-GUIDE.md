# Semper Admin Portal - Portable Style Guide

Drop these tokens into any app to inherit the Semper Admin Portal visual system. Source of truth is `src/app/globals.css` in the SemperAdminPortal repo. This file mirrors the v1.2 token set shipped 2026-05-04.

Two companion files sit next to this one:

- `semper-tokens.css` - paste-ready CSS variables for any framework.
- `semper-tokens.json` - flat token export for Tailwind configs, Style Dictionary, Figma plugins.

## 1. Design Principles

- Default theme is dark navy. Light parchment is the secondary toggle.
- One display surface per fold. Bebas Neue stays rare and load-bearing.
- One claim, one citation. Authority sits next to the claim it backs.
- Tokens drive everything. No hardcoded hex outside test fixtures.
- Motion gates behind `prefers-reduced-motion`. Animations stay under 240ms.

## 2. Color Tokens

### 2.1 Brand Palette

Source: USMC logo extraction. Use these as the primary brand surfaces.

| Token | Hex | Use |
|-------|-----|-----|
| `--color-usmc-scarlet` | `#B82230` | Primary CTA, marine role accent, link hover |
| `--color-usmc-scarlet-700` | `#971826` | Active state, pressed buttons |
| `--color-usmc-scarlet-300` | `#D14150` | Dark-mode primary, gradient origin |
| `--color-marine-blue` | `#0F1F3D` | Deep navy chrome, commander role accent |
| `--color-marine-blue-700` | `#0A1424` | Charcoal navy, dark background |
| `--color-marine-blue-300` | `#2A3D60` | Secondary surface in dark mode |
| `--color-marine-blue-100` | `#6B9BD2` | Commander accent in dark mode |
| `--color-parchment` | `#F2E5BE` | Light surface base, dark-mode text |
| `--color-parchment-700` | `#D9C994` | Aged paper accent |
| `--color-parchment-300` | `#FAF1D8` | Lightest surface elevation |
| `--color-brass` | `#B89042` | Leader role accent, antique brass details |
| `--color-brass-700` | `#8E6E2E` | Brass pressed state |
| `--color-brass-300` | `#D4AF67` | Brass highlight, dark-mode accent |

### 2.2 Neutral Ramps

Warm parchment-tinted ramp for light mode. Cool navy ramp for dark mode.

| Token | Hex | Token | Hex |
|-------|-----|-------|-----|
| `--color-neutral-50` | `#F8F4E8` | `--color-ink-50` | `#F2E5BE` |
| `--color-neutral-100` | `#F2EBD4` | `--color-ink-100` | `#B5A988` |
| `--color-neutral-200` | `#E7DFC2` | `--color-ink-200` | `#8A7F66` |
| `--color-neutral-300` | `#C9BD96` | `--color-ink-300` | `#34507A` |
| `--color-neutral-400` | `#A89A72` | `--color-ink-400` | `#233A5C` |
| `--color-neutral-500` | `#8A7E63` | `--color-ink-500` | `#1F345C` |
| `--color-neutral-600` | `#5C5340` | `--color-ink-600` | `#182A4D` |
| `--color-neutral-700` | `#3A3328` | `--color-ink-700` | `#11203F` |
| `--color-neutral-800` | `#26221A` | `--color-ink-800` | `#0A1424` |
| `--color-neutral-900` | `#181410` | `--color-ink-900` | `#060E1A` |
| `--color-neutral-950` | `#0F0C09` | | |

### 2.3 Role Accents

Four roles, four colors. Match the accent to the audience.

| Token | Hex | Role |
|-------|-----|------|
| `--color-role-marine` | `#B82230` | Junior enlisted |
| `--color-role-leader` | `#B89042` | NCO and SNCO |
| `--color-role-commander` | `#0F1F3D` | Officer (light) or `#6B9BD2` (dark) |
| `--color-role-admin` | `#2F8F5C` | S-1 and admin specialist |

### 2.4 Status

Drives staleness banners, validation messages, info callouts.

| Token | Hex | Meaning |
|-------|-----|---------|
| `--color-status-fresh` | `#2F8F5C` | Verified within window |
| `--color-status-aging` | `#C97D1F` | Approaching review date |
| `--color-status-stale` | `#B83232` | Past review date, audit required |
| `--color-status-info` | `#2F5FA8` | Informational context |

### 2.5 Semantic Tokens

Components reference semantic tokens, not raw hex. Light defaults shown. Dark overrides below.

| Token | Light | Dark |
|-------|-------|------|
| `--color-background` | `#F8F4E8` | `#0A1424` |
| `--color-bg-elev` | `#FFFCF4` | `#11203F` |
| `--color-bg-sunken` | `#EFE9D6` | `#060E1A` |
| `--color-foreground` | `#1A1610` | `#F2E5BE` |
| `--color-card` | `#FFFCF4` | `#11203F` |
| `--color-popover` | `#FFFCF4` | `#11203F` |
| `--color-primary` | `#B82230` | `#D14150` |
| `--color-primary-foreground` | `#FFFCF4` | `#060E1A` |
| `--color-secondary` | `#0F1F3D` | `#2A3D60` |
| `--color-secondary-foreground` | `#F2E5BE` | `#F2E5BE` |
| `--color-muted` | `#F2EBD4` | `#182A4D` |
| `--color-muted-foreground` | `#5C5340` | `#B5A988` |
| `--color-subtle-foreground` | `#8A7E63` | `#8A7F66` |
| `--color-accent` | `#B89042` | `#D4AF67` |
| `--color-accent-foreground` | `#1A1610` | `#060E1A` |
| `--color-destructive` | `#B83232` | `#B83232` |
| `--color-border` | `#DDD3B5` | `#233A5C` |
| `--color-border-strong` | `#C9BD96` | `#34507A` |
| `--color-ring` | `#B82230` | `#B82230` |
| `--color-surface` | `#FFFCF4` | `#11203F` |
| `--color-surface-2` | `#F2EBD4` | `#182A4D` |
| `--color-surface-3` | `#E7DFC2` | `#1F345C` |

## 3. Typography

### 3.1 Font Stack

Self-hosted variable fonts. No Google Fonts request at runtime.

```css
--font-display: "Bebas Neue", "Oswald", system-ui, sans-serif;
--font-body:    "Inter Variable", "Inter", system-ui, sans-serif;
--font-mono:    "JetBrains Mono Variable", "JetBrains Mono", "Cascadia Code", Menlo, monospace;
```

Install with:

```bash
npm i @fontsource-variable/inter @fontsource-variable/jetbrains-mono @fontsource/bebas-neue
```

Then import once in your root stylesheet:

```css
@import "@fontsource-variable/inter";
@import "@fontsource-variable/jetbrains-mono";
@import "@fontsource/bebas-neue";
```

### 3.2 Type Scale

| Token | Size | rem | Role |
|-------|------|-----|------|
| `--text-xs` | 12 | 0.75 | Eyebrow, fine print |
| `--text-sm` | 13 | 0.8125 | UI controls, mono citations |
| `--text-base` | 15 | 0.9375 | Body default |
| `--text-md` | 16 | 1 | Long-form policy prose |
| `--text-lg` | 17 | 1.0625 | h3 |
| `--text-xl` | 20 | 1.25 | Subhead |
| `--text-2xl` | 22 | 1.375 | h2 |
| `--text-3xl` | 28 | 1.75 | h1 in body |
| `--text-4xl` | 36 | 2.25 | Page header |
| `--text-5xl` | 48 | 3 | Hero secondary |
| `--text-6xl` | 56 | 3.5 | Hero display |

### 3.3 Heading Rules

- Hero h1, page header h1, role card h3, stat tile number: `font-display` (Bebas Neue).
- All other headings: `font-body` (Inter) with weight 700 for h2, 600 for h3.
- Line height 1.2 for headings, 1.6 for body, 1.7 for long-form prose.
- Letter spacing -0.005em on headings.
- Maximum one Bebas Neue surface per fold.

### 3.4 Text Treatments

```css
/* Eyebrow */
font: 700 11px/1 var(--font-body);
text-transform: uppercase;
letter-spacing: 0.08em;
color: var(--color-muted-foreground);

/* Mono citation */
font: 500 13px var(--font-mono);
color: var(--color-subtle-foreground);
```

## 4. Spacing Scale

Strict scale. No off-scale values.

`4 / 8 / 12 / 16 / 24 / 32 / 48 / 64`

| Use | Spacing |
|-----|---------|
| Card padding desktop (role and home cards) | 24 |
| Card padding dense content | 20 |
| Card padding mobile minimum | 16 |
| Grid gaps default | 18 |
| Section spacing within | 32 |
| Section spacing between | 40 |
| Section spacing between major blocks | 56 |

## 5. Radii

```css
--radius-xs:     3px;  /* Tags */
--radius-sm:     6px;  /* Buttons */
--radius-md:     8px;  /* Cards */
--radius-lg:    12px;  /* Hero, floating chrome */
--radius-card:   8px;
--radius-button: 6px;
--radius-banner: 0px;
--radius-chip:   9999px;
--radius:        0.5rem;
```

## 6. Shadows

Two tiers, with dark-mode overrides for deeper occlusion.

Light:

```css
--shadow-sm:          0 1px 2px rgba(26,22,16,.05), 0 0 0 1px rgba(26,22,16,.04);
--shadow-card:        0 1px 2px rgba(26,22,16,.05), 0 0 0 1px rgba(26,22,16,.04);
--shadow-md:          0 2px 4px rgba(26,22,16,.06), 0 10px 28px rgba(26,22,16,.08);
--shadow-card-strong: 0 2px 4px rgba(26,22,16,.06), 0 10px 28px rgba(26,22,16,.08);
--shadow-lg:          0 18px 52px rgba(26,22,16,.20);
```

Dark:

```css
--shadow-sm: 0 1px 2px rgba(0,0,0,.4),  0 0 0 1px rgba(242,229,190,.04);
--shadow-md: 0 2px 4px rgba(0,0,0,.4),  0 10px 28px rgba(0,0,0,.45);
--shadow-lg: 0 18px 52px rgba(0,0,0,.55);
```

## 7. Layout Constants

```css
--topbar-h: 56px;   /* Floating pill height */
--tree-w:  272px;   /* Sidebar tree width */
--toc-w:   232px;   /* Right TOC width */
```

Mobile topbar collapses to 48px. Bottom tab bar holds 5 tabs.

## 8. Motion

| Duration | Token | Use |
|----------|-------|-----|
| 120ms | fast | Hover, focus rings |
| 180ms | default | Drawers, popovers |
| 240ms | slow | Route fades |

Easing curves: ease-out for entry, ease-in for exit. Every transition gates behind:

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

No scroll-driven reveals. No page-transition theater.

## 9. Premium Polish Layer

Six craft moves preserve the UUPM benchmark aesthetic across new surfaces.

1. Default to dark theme.
2. Floating pill topbar with backdrop blur.
3. Ambient bloom radial gradient at section tops in dark mode.
4. Stat tiles: 32px brass icon, 44px Bebas Neue numeric, eyebrow label, meta line, hover lift.
5. Gradient text accent on a single hero keyword per page.
6. Card breathing room: 24px padding, 18px grid gaps, per-role tinted radial bloom on dark role cards.

### 9.1 Gradient Text Accent

```css
.gradient-accent {
  background: linear-gradient(95deg,
    var(--color-usmc-scarlet) 0%,
    var(--color-usmc-scarlet-300) 35%,
    var(--color-brass-300) 75%,
    var(--color-brass) 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  color: transparent;
}
```

### 9.2 Ambient Bloom

```css
.ambient-bloom { position: relative; isolation: isolate; }
.ambient-bloom::before {
  content: "";
  position: absolute;
  top: -40px; left: 50%;
  transform: translateX(-50%);
  width: 70%; max-width: 720px; height: 320px;
  background: radial-gradient(ellipse at center,
    color-mix(in srgb, var(--color-usmc-scarlet) 10%, transparent) 0%,
    color-mix(in srgb, var(--color-marine-blue-300) 8%, transparent) 40%,
    transparent 75%);
  pointer-events: none;
  z-index: -1;
  filter: blur(20px);
  opacity: 0;
  transition: opacity .3s ease;
}
.dark .ambient-bloom::before { opacity: 1; }
```

### 9.3 Floating Pill Chrome

```css
.chrome-floating {
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  background: color-mix(in srgb, var(--color-bg-elev) 92%, transparent);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  box-shadow: var(--shadow-md);
}
```

## 10. Selection and Focus

```css
:focus-visible {
  outline: 3px solid var(--color-ring);
  outline-offset: 2px;
  border-radius: 2px;
}

::selection {
  background: var(--color-brass);
  color: var(--color-neutral-950);
}
```

## 11. How to Adopt in Another App

Three integration paths, from light to heavy.

### 11.1 Raw CSS (any framework)

1. Copy `semper-tokens.css` into your project.
2. Import it once in your root stylesheet or HTML head.
3. Reference variables in your existing components: `color: var(--color-primary)`.
4. Toggle dark mode by adding the `dark` class to `html` or `body`.

### 11.2 Tailwind v4

1. Copy `semper-tokens.css` into `src/app/globals.css`.
2. Wrap the brand variables in an `@theme` block (already structured for this).
3. Tailwind generates utilities automatically: `bg-usmc-scarlet`, `text-parchment`, `rounded-lg`, etc.
4. Install the fonts from the type stack section.

### 11.3 Build pipeline (Style Dictionary, Figma Tokens)

1. Consume `semper-tokens.json`.
2. Map your platform transforms onto the flat token tree.
3. Emit native variables for iOS, Android, or other targets.

## 12. Pitfalls to Avoid

- Hardcoding hex values in components breaks the dark-mode swap. Reference tokens.
- Using Bebas Neue on every heading flattens the hierarchy. Inter owns h2 and h3.
- Off-scale spacing (10px, 18px outside the grid gap) degrades visual rhythm. Stick to the 4/8/12/16/24/32/48/64 ladder.
- Skipping `prefers-reduced-motion` violates accessibility floors.
- Inline gradient text on long copy fails contrast. Hero only, single keyword.
- Floating chrome without backdrop blur looks flat. Keep the blur and the shadow together.

End of guide.
