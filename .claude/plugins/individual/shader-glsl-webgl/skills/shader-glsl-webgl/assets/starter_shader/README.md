# GLSL Shader Starter

Minimal Vite project running a full-screen animated fragment shader via raw
WebGL — no framework, no dependencies beyond Vite.

## Setup

```bash
npm install
npm run dev
```

## What it shows

- Raw WebGL setup: compile, link, and error-check a shader program
- A full-screen quad driven by a fragment shader
- Standard uniforms: `u_resolution`, `u_time`, `u_mouse`
- DPR-aware resize and pointer interaction
- An fbm (fractal noise) gradient in `src/shader.frag` that reacts to the cursor

## Structure

- `index.html` — a single `<canvas id="gl">`
- `src/main.js` — WebGL boilerplate; imports the shader with Vite's `?raw`
- `src/shader.frag` — the fragment shader (edit this to change the visual)
- `src/style.css` — full-viewport canvas

## Next steps

Swap `src/shader.frag` for any preset from the skill's generator:

```bash
# from the skill root
./scripts/generate_shader.py --type raymarch --output assets/starter_shader/src/shader.frag
```
