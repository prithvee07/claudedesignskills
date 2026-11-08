# CSS Scroll-Driven Animations Starter

A static, zero-JavaScript demo of native CSS scroll-driven animations.

## Run

No build step. Open `index.html` directly, or serve the folder:

```bash
python3 -m http.server
```

Then visit the printed URL.

## What it shows

- **Progress bar** — a fixed bar scaling with page scroll (`scroll(root)`)
- **Reveal on enter** — fade + rise as blocks enter the viewport (`view()`)
- **Parallax** — slow drift while in view
- **Sticky clip reveal** — a sticky element un-clipping as it crosses the viewport
- **Progressive enhancement** — every effect is wrapped in `@supports`, so
  unsupported browsers show a clean static page
- **Reduced motion** — all effects disable under `prefers-reduced-motion: reduce`

## Structure

- `index.html` — markup only, no scripts
- `src/style.css` — all effects with `@supports` fallbacks and a11y guard

## Browser support

Scroll-driven animations ship in Chromium browsers; Safari/Firefox support
varies. The `@supports` wrappers keep the page usable everywhere.
