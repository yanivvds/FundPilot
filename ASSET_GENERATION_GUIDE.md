# FundPilot Asset Generation Guide

Visual assets checklist for the Data Bureau brand identity. Each entry includes file name, dimensions, tool, storage path, and generation prompt.

---

## Directory Structure

```
/Users/yanivvanderstigchel/Docs/FundPilot/
  img/
    fund_pilot.png          (existing logo)
    favicon-32.png          (new)
    favicon-16.png          (new)
    og-image.png            (new)
    avatar-placeholder.png  (new)
    app-icon-512.png        (new)
  static/
    illustrations/
      empty-no-data.svg     (new)
      empty-first-query.svg (new)
      empty-error.svg       (new)
```

---

## Asset Checklist

### 1. Favicon (32x32)

- [ ] **File:** `favicon-32.png`
- **Store:** `img/favicon-32.png`
- **Tool:** Midjourney v6 or DALL-E 3
- **Prompt:** `Minimal geometric icon, ascending bar chart with single upward arrow, gold gradient (#C9A84C to #8B6914) on dark background (#141218), sharp clean edges, no text, no extra decoration, financial data symbol, flat design, metallic sheen, centered in square frame, icon design --style raw --ar 1:1 --s 50`
- **Post-processing:** Resize to 32x32 in any image editor. Export as PNG with transparency.

### 2. Favicon (16x16)

- [ ] **File:** `favicon-16.png`
- **Store:** `img/favicon-16.png`
- **Tool:** Derived from favicon-32
- **Post-processing:** Resize the 32x32 favicon to 16x16. May need manual pixel cleanup at this size.

### 3. App Icon (512x512)

- [ ] **File:** `app-icon-512.png`
- **Store:** `img/app-icon-512.png`
- **Tool:** Midjourney v6 or DALL-E 3
- **Prompt:** `Minimal geometric app icon, ascending bar chart with single upward arrow, gold metallic gradient (#C9A84C to #8B6914) on dark navy-black background (#141218), sharp edges, no text, financial data visualization symbol, flat design with subtle metallic sheen, centered, app icon format, professional, premium --style raw --ar 1:1 --s 50`

### 4. Avatar Placeholder (128x128)

- [ ] **File:** `avatar-placeholder.png`
- **Store:** `img/avatar-placeholder.png`
- **Tool:** Midjourney v6 or DALL-E 3
- **Prompt:** `Minimal geometric portrait placeholder, abstract human silhouette made of simple clean shapes, gold (#F0A500) and dark charcoal (#141218) on warm off-white background (#F5F3EF), editorial design style, professional, flat vector aesthetic, no facial features, abstract, premium --style raw --ar 1:1 --s 50`

### 5. OG / Social Media Image (1200x630)

- [ ] **File:** `og-image.png`
- **Store:** `img/og-image.png`
- **Tool:** Figma (manual creation)
- **Spec:**
  - Canvas: 1200x630px, background `#141218`
  - FundPilot logo centered, 80px height
  - Below logo: 2px horizontal rule in `#F0A500`, width 200px, centered
  - Below rule: tagline "AI-Powered Data Analyst" in Fraunces 28px weight 600, color `#F5F3EF`
  - 2px `#F0A500` border inset 16px from all edges
  - No other decoration

### 6. Empty State: No Data (800x600)

- [ ] **File:** `empty-no-data.svg` (SVG for scalability)
- **Store:** `static/illustrations/empty-no-data.svg`
- **Tool:** Midjourney v6 for concept, then trace/recreate in Figma as SVG
- **Prompt:** `Minimal line illustration on pure white background, empty bar chart with three dotted placeholder bars at different heights, single thin axis line, warm gold (#F0A500) and charcoal (#141218) color scheme, editorial geometric style, Bloomberg aesthetic, no people, no text, professional data visualization concept, very thin precise lines, lots of white space --style raw --ar 4:3 --s 50`

### 7. Empty State: First Query (800x600)

- [ ] **File:** `empty-first-query.svg`
- **Store:** `static/illustrations/empty-first-query.svg`
- **Tool:** Midjourney v6 for concept, then trace/recreate in Figma as SVG
- **Prompt:** `Minimal line illustration on pure white background, abstract search cursor blinking over a minimal data grid of thin lines, warm gold (#F0A500) accent on single element, rest in charcoal (#141218) thin lines, editorial geometric style, Bloomberg terminal aesthetic, no people, no text, professional, very thin precise lines, lots of white space --style raw --ar 4:3 --s 50`

### 8. Empty State: Error (800x600)

- [ ] **File:** `empty-error.svg`
- **Store:** `static/illustrations/empty-error.svg`
- **Tool:** Midjourney v6 for concept, then trace/recreate in Figma as SVG
- **Prompt:** `Minimal line illustration on pure white background, disconnected geometric nodes with thin lines between them, one small triangle alert symbol, muted crimson (#D32F2F) accent on alert element, rest in charcoal (#141218) thin lines, editorial geometric style, no people, no text, professional, very thin precise lines, lots of white space --style raw --ar 4:3 --s 50`

### 9. Loading Skeleton (CSS only -- no asset needed)

- [ ] **Implementation in code:**
  - Shimmer gradient: `linear-gradient(90deg, #E2DFD8 25%, #F5F3EF 50%, #E2DFD8 75%)`
  - Background-size: 200% 100%
  - Animation: slide left-to-right, 1.5s infinite ease-in-out

---

## Notes for Asset Generation

- For Midjourney: use `--style raw` to avoid the "Midjourney look" and keep things clean
- Use `--s 50` or lower for less stylization
- After generating, always manually clean up in Figma/Illustrator to ensure the colors exactly match the brand hex values from `BRANDKIT.md`
- SVGs are preferred for illustrations (scalable, small file size, can be colored via CSS)
- PNGs for icons and photos (use 2x resolution for retina: generate at 1024x1024, export at 512x512)
- All assets should feel like they belong to the same visual system: thin lines, geometric shapes, the saffron/charcoal palette
