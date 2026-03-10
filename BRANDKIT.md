# FundPilot Brand Kit -- "Data Bureau"

> The confidence of Bloomberg Terminal's information density, filtered through modern editorial design. Data is content worthy of magazine-quality presentation.

## Design Philosophy

Dense when needed, never cluttered. Borrows from newsroom typography and financial terminal aesthetics to create something serious and visually striking. The existing gold/bronze logo anchors the identity, bridged to the UI through the electric saffron accent.

---

## Core Palette

| Role | Name | Hex | RGB | Usage |
|------|------|-----|-----|-------|
| Primary | Bureau Black | `#141218` | 20, 18, 24 | Headers, navigation, strong UI chrome |
| Secondary | Graphite Violet | `#45405A` | 69, 64, 90 | Secondary text, metadata, inactive states |
| Accent | Electric Saffron | `#F0A500` | 240, 165, 0 | CTAs, data highlights, interactive elements |
| Background | Warm Chalk | `#F5F3EF` | 245, 243, 239 | Page background, base layer |
| Surface | Clean White | `#FFFFFF` | 255, 255, 255 | Cards, panels, elevated containers |
| Text | Deep Ink | `#1E1B26` | 30, 27, 38 | Body copy, data values, primary content |

## Extended Palette

| Role | Name | Hex | Usage |
|------|------|-----|-------|
| Success | Terminal Green | `#00C853` | Positive indicators, confirmations, upward trends |
| Warning | Signal Amber | `#FFB300` | Caution states, pending items, neutral trends |
| Error | Alert Crimson | `#D32F2F` | Errors, destructive actions, downward trends |
| Accent Hover | Deep Saffron | `#D4920A` | Hover/pressed state for accent elements |
| Accent Subtle | Saffron Wash | `#F0A50014` | 8% opacity backgrounds for highlighted rows/areas |
| Border | Chalk Edge | `#E2DFD8` | Card borders, dividers, table rules |
| Border Dark | Stone | `#C8C3B8` | Stronger borders, input outlines on focus |
| Muted Text | Faded Violet | `#7A7590` | Placeholders, disabled text, timestamps |
| Code Background | Terminal Wash | `#F8F6F2` | Background for code blocks, SQL displays |

## Dark Mode Palette

| Role | Light | Dark | Notes |
|------|-------|------|-------|
| Primary | `#141218` | `#F5F3EF` | Inverts: dark text becomes light |
| Secondary | `#45405A` | `#9690A8` | Lightened for readability |
| Accent | `#F0A500` | `#F0A500` | Unchanged -- gains power on dark ground |
| Background | `#F5F3EF` | `#141218` | Full inversion |
| Surface | `#FFFFFF` | `#1E1B26` | Cards float on dark base |
| Text | `#1E1B26` | `#E8E4DC` | Warm off-white, not pure white |
| Border | `#E2DFD8` | `#2A2636` | Subtle separation |
| Code BG | `#F8F6F2` | `#1A1724` | Slightly lighter than surface |
| Success | `#00C853` | `#00E676` | Slightly brighter for contrast |
| Warning | `#FFB300` | `#FFCA28` | Slightly brighter for contrast |
| Error | `#D32F2F` | `#EF5350` | Slightly brighter for contrast |

Dark mode feel: Bloomberg Terminal that went to design school. Warm undertones preserved.

---

## Typography

### Font Stack

| Role | Font | Weights | Google Fonts Import |
|------|------|---------|---------------------|
| Display | Fraunces | 600, 700, 800 | `Fraunces:wght@600;700;800` |
| Body | Outfit | 300, 400, 500, 600 | `Outfit:wght@300;400;500;600` |
| Data/Code | Fira Code | 400, 500 | `Fira+Code:wght@400;500` |

### Type Scale

| Level | Font | Size | Weight | Line Height | Letter Spacing | Color |
|-------|------|------|--------|-------------|----------------|-------|
| Display (h1) | Fraunces | 32px | 700 | 1.2 | -0.02em | `#141218` |
| Title (h2) | Fraunces | 24px | 600 | 1.3 | -0.01em | `#141218` |
| Section (h3) | Outfit | 18px | 600 | 1.4 | 0 | `#141218` |
| Subtitle (h4) | Outfit | 15px | 600 | 1.4 | 0 | `#45405A` |
| Body | Outfit | 15px | 400 | 1.6 | 0 | `#1E1B26` |
| Body Small | Outfit | 13px | 400 | 1.5 | 0 | `#1E1B26` |
| Caption | Outfit | 12px | 500 | 1.4 | +0.02em | `#7A7590` |
| Overline | Outfit | 11px | 600 | 1.3 | +0.06em | `#45405A` |
| Code | Fira Code | 14px | 400 | 1.6 | 0 | `#1E1B26` |
| Code Small | Fira Code | 12px | 400 | 1.5 | 0 | `#1E1B26` |
| Data Table | Fira Code | 13px | 400 | 1.4 | 0 | `#1E1B26` |

### Rules

- Fraunces is reserved for h1 and h2 ONLY. It is the "editorial" register.
- Everything h3 and below uses Outfit.
- Numeric data in tables always uses Fira Code with `font-feature-settings: "tnum"` (tabular figures).
- Overline style (11px uppercase) used for section labels above cards.
- Never set Fraunces below 20px.

---

## Spacing System

Base unit: 4px

| Token | Value | Usage |
|-------|-------|-------|
| `space-1` | 4px | Tight gaps, icon padding |
| `space-2` | 8px | Between related elements |
| `space-3` | 12px | Between form elements, list items |
| `space-4` | 16px | Card internal padding (compact), section gaps |
| `space-5` | 20px | Standard card padding |
| `space-6` | 24px | Between content blocks |
| `space-8` | 32px | Between major sections |
| `space-10` | 40px | Page margins |
| `space-12` | 48px | Large section separation |
| `space-16` | 64px | Hero/header vertical padding |

The density is intentional. This is an information tool. Tight-to-moderate spacing (16-20px card padding) keeps data accessible without cramping.

---

## Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| `radius-sm` | 2px | Buttons, inputs, small elements |
| `radius-md` | 4px | Cards, dropdowns, modals |
| `radius-lg` | 6px | Large containers, dialogs |
| `radius-full` | 9999px | Tags, badges, pills, avatars |

Sharp. The sharpness signals precision and editorial rigor. No soft, rounded "friendly" corners.

---

## Shadows

| Token | Value | Usage |
|-------|-------|-------|
| `shadow-sm` | `0 1px 2px rgba(20, 18, 24, 0.05)` | Subtle lift for inputs |
| `shadow-md` | `0 2px 8px rgba(20, 18, 24, 0.06), 0 12px 32px rgba(20, 18, 24, 0.04)` | Cards, panels |
| `shadow-lg` | `0 4px 16px rgba(20, 18, 24, 0.08), 0 24px 48px rgba(20, 18, 24, 0.06)` | Modals, popovers |
| `shadow-focus` | `0 0 0 3px rgba(240, 165, 0, 0.2)` | Focus rings on interactive elements |

Double-shadow technique on md and lg creates realistic depth. Hover states intensify shadow (move from `shadow-md` to `shadow-lg`) rather than changing color.

---

## Component Specifications

### Buttons

**Primary:**
- Background: `#141218`
- Text: `#FFFFFF`, Outfit 14px weight 500
- Height: 44px, padding: 0 20px
- Radius: 2px
- Left border: 3px solid `#F0A500` (the signature detail)
- Hover: background `#2A2636`
- Active: scale(0.97) for 120ms ("stamp" feel)
- Disabled: background `#45405A`, no left border

**Secondary:**
- Background: transparent
- Border: 1.5px solid `#141218`
- Text: `#141218`, Outfit 14px weight 500
- Height: 44px
- Hover: border-color transitions to `#F0A500`
- Active: background `#F5F3EF`

**Ghost:**
- Background: transparent, no border
- Text: `#45405A`, Outfit 14px weight 500
- Hover: text `#141218`, underline
- Used for: tertiary actions, inline links

### Cards

- Background: `#FFFFFF`
- Border: 1px solid `#E2DFD8`
- Radius: 4px
- Shadow: `shadow-md`
- Padding: 20px
- Card title: Fraunces 18px weight 600, followed by a 1px `#E2DFD8` horizontal rule with 16px bottom margin
- Data-heavy cards: alternating rows `#FFFFFF` / `#F5F3EF`
- Hover (if clickable): shadow transitions to `shadow-lg`

### Inputs

- Background: `#FFFFFF`
- Border: 1.5px solid `#D0CCC4`
- Radius: 2px
- Height: 44px
- Padding: 0 12px
- Font: Outfit 15px weight 400
- Placeholder: `#7A7590`
- Focus: border `#141218`, then a 2px `#F0A500` bottom-border slides in from left (signature micro-interaction, 200ms ease-out)
- Focus ring: `shadow-focus`
- Label: Outfit 12px weight 600, `#45405A`, letter-spacing +0.02em, 6px below label

### Navigation (Top Bar)

- Background: `#141218`
- Height: 56px
- Logo: left-aligned, 24px from edge
- Nav items: `#FFFFFF`, Outfit 13px weight 500, letter-spacing +0.04em, uppercase
- Active state: `#F0A500` text color
- Loading indicator: 2px `#F0A500` progress bar at very top of viewport
- User menu: right-aligned, avatar circle (32px) + name in `#FFFFFF`

### Data Tables

- Full-width, no outer border
- Header row: `#141218` background, white text, Outfit 11px weight 600 uppercase, letter-spacing +0.04em
- Data rows: Fira Code 13px weight 400, alternating `#FFFFFF` / `#F5F3EF`
- Row borders: 1px `#E2DFD8` horizontal rules only (no vertical)
- Totals row: Outfit 14px weight 600, `#141218` background, white text
- Hover row: background `#F0A50014` (saffron at 8%)
- Numeric alignment: right-aligned, tabular figures

### Charts

Primary chart palette (in order of usage):
1. `#F0A500` Electric Saffron
2. `#141218` Bureau Black
3. `#45405A` Graphite Violet
4. `#D32F2F` Alert Crimson
5. `#00C853` Terminal Green
6. `#7A7590` Faded Violet
7. `#FFB300` Signal Amber
8. `#C8C3B8` Stone

Chart styling:
- Gridlines: `#E2DFD8` at 0.5px
- Axis labels: Outfit 11px `#7A7590`
- Chart titles: Outfit 15px weight 600 `#141218`
- Animation: 400ms ease-out-cubic on load
- Tooltip: `#141218` background, white text, 2px radius, `shadow-lg`

### Chat Messages

- User message: right-aligned, `#141218` background, white text, 4px radius
- AI message: left-aligned, `#FFFFFF` background, 1px `#E2DFD8` border, `#1E1B26` text
- AI message header: "FundPilot" in Outfit 12px weight 600 `#F0A500`
- SQL code blocks: `#F8F6F2` background, 1px `#E2DFD8` border, Fira Code 13px
- Typing indicator: three `#F0A500` dots with sequential fade animation

### Tags / Badges

- Background: `#F0A50014` (saffron 8%)
- Text: `#D4920A` (deep saffron)
- Font: Outfit 11px weight 600
- Radius: 9999px (pill)
- Padding: 2px 10px
- Variants: success (green bg/text), error (red bg/text), neutral (violet bg/text)

### Empty States

- Centered layout
- Illustration (see `ASSET_GENERATION_GUIDE.md`)
- Title: Fraunces 24px weight 600
- Description: Outfit 15px weight 400 `#45405A`
- CTA: Primary button

---

## Voice and Tone

**Brand personality:** Expert editorial voice. FundPilot speaks like a senior analyst writing for a financial publication -- precise, confident, direct. Never vague, never hedging.

**Writing principles:**
- Lead with the number, then explain it
- Use active voice
- Short sentences for data, longer sentences for insight
- No filler words ("eigenlijk", "een beetje", "misschien")
- Technical terms are fine when standard in fundraising

**UI copy tone:**
- Button labels: direct verbs ("Analyseer", "Exporteer", "Filter")
- Error messages: state the problem, then the fix
- Empty states: suggest a clear next action
- Confirmations: brief and specific

---

## Logo Usage

- Primary placement: top-left of navigation bar against `#141218` background
- Minimum clear space: 16px on all sides
- Minimum size: 24px height
- The gold gradient logo works natively against both `#141218` (dark nav) and `#F5F3EF` (light background)
- Never place the logo on `#F0A500` or other mid-tone colored backgrounds
- Favicon: simplified logo mark (the chart/arrow icon only) at 32x32 and 16x16

---

## Asset Generation

See `ASSET_GENERATION_GUIDE.md` for the complete checklist of visual assets to create, including exact prompts, tools, dimensions, file names, and storage locations.

---

## Implementation Files

| File | Purpose |
|------|---------|
| `frontends/webcomponent/src/styles/vanna-design-tokens.ts` | Primary CSS custom properties |
| `src/vanna/servers/base/templates.py` | Google Fonts imports, Tailwind config |
| `frontends/webcomponent/src/components/vanna-chat.ts` | Component styling consuming tokens |
