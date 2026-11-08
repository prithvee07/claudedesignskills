# Matter.js Starter

Minimal Vite project with a bounded world of falling, bouncy, draggable shapes.

## Setup

```bash
npm install
npm run dev
```

## What it shows

- Engine + canvas Render + Runner setup
- A bounded world (four static walls)
- Random circles and boxes with restitution
- Pointer dragging via MouseConstraint (HiDPI-aware pixelRatio)
- HUD buttons: toggle gravity and reset the scene

## Structure

- `index.html` — HUD + `#world` mount point
- `src/main.js` — engine, walls, shapes, dragging, controls
- `src/style.css` — full-viewport canvas and HUD styling

## Next steps

Swap in other presets from the skill's generator:

```bash
# from the skill root
./scripts/init_matter.py --preset dom-sync --output src/main.js
```
