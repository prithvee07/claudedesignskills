# Lenis Starter

Minimal Vite project demonstrating Lenis smooth scroll with a progress bar,
parallax layers, and reveal-on-scroll.

## Setup

```bash
npm install
npm run dev
```

## What it shows

- Smooth scroll with a single RAF loop
- `prefers-reduced-motion` guard (disables smoothing when requested)
- Parallax via `data-speed` attributes driven from the `scroll` event
- Scroll progress bar from the `progress` value
- Reveal-on-scroll using IntersectionObserver (native scroll preserved)
- Smooth anchor links via `lenis.scrollTo`

## Structure

- `src/main.js` — Lenis setup + parallax/reveal/progress wiring
- `src/style.css` — layout and reveal transitions
- `index.html` — demo sections
