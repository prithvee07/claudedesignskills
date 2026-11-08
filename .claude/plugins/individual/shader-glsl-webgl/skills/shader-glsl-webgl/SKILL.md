---
name: shader-glsl-webgl
description: Write custom GLSL shaders for the web - fragment and vertex shaders for WebGL and Three.js. Use when building shader-driven backgrounds, gradients, noise and procedural patterns, raymarched scenes, displacement effects, image/post-processing passes, or custom materials. Triggers on tasks involving GLSL, fragment shaders, vertex shaders, uniforms, varyings, WebGL/WebGL2, ShaderMaterial, RawShaderMaterial, signed distance fields (SDF), raymarching, noise/fbm, or Shadertoy-style effects. Covers raw WebGL setup and Three.js integration, GLSL ES 1.00 and 3.00 differences, and performance.
---

# Shader GLSL WebGL

## Overview

GLSL (OpenGL Shading Language) programs run on the GPU to compute vertex positions and pixel colors. On the web they power procedural backgrounds, custom materials, displacement, and post-processing — either through raw WebGL or a framework like Three.js.

**When to Use This Skill**:
- Full-screen shader backgrounds (gradients, noise, plasma, patterns)
- Custom Three.js materials via `ShaderMaterial` / `RawShaderMaterial`
- Vertex displacement (waves, morphing, GPU animation)
- Raymarched / signed-distance-field scenes
- Image effects and post-processing passes
- Porting Shadertoy effects into a site

**Key Concepts**:
- **Two stages**: the **vertex** shader positions geometry; the **fragment** shader colors each pixel.
- **Parallel**: the fragment shader runs once per pixel with no knowledge of neighbors.
- **Inputs**: `attribute`/`in` (per-vertex), `uniform` (global), `varying`/`in`/`out` (vertex→fragment).
- **Everything is math**: colors, shapes, and motion come from `uv`, `u_time`, and functions like `sin`, `mix`, `smoothstep`, `fract`.

---

## Core Concepts

### 1. A minimal fragment shader (GLSL ES 1.00 / WebGL1)

```glsl
precision highp float;

uniform vec2 u_resolution;
uniform float u_time;

void main() {
  vec2 uv = gl_FragCoord.xy / u_resolution.xy; // 0..1
  vec3 color = vec3(uv.x, uv.y, abs(sin(u_time)));
  gl_FragColor = vec4(color, 1.0);
}
```

### 2. Normalized, aspect-corrected coordinates

```glsl
// Center at 0, keep circles round regardless of canvas ratio
vec2 uv = (gl_FragCoord.xy * 2.0 - u_resolution.xy) / u_resolution.y;
```

### 3. Standard uniforms

Most web shaders expose a small, Shadertoy-like set:
- `u_resolution` (vec2) — canvas size in px
- `u_time` (float) — seconds since start
- `u_mouse` (vec2) — pointer position

### 4. WebGL1 vs WebGL2 (GLSL ES 1.00 vs 3.00)

| Concept | ES 1.00 (WebGL1) | ES 3.00 (WebGL2) |
| --- | --- | --- |
| Version tag | _(none)_ | `#version 300 es` (first line) |
| Vertex input | `attribute` | `in` |
| V→F passing | `varying` | `out` (vert) / `in` (frag) |
| Fragment output | `gl_FragColor` | custom `out vec4` |
| Texture lookup | `texture2D()` | `texture()` |

### 5. Vertex shader + displacement

```glsl
// Three.js ShaderMaterial provides position, uv, and matrices automatically
uniform float u_time;
varying vec2 vUv;

void main() {
  vUv = uv;
  vec3 p = position;
  p.z += sin(p.x * 4.0 + u_time) * 0.2; // ripple
  gl_Position = projectionMatrix * modelViewMatrix * vec4(p, 1.0);
}
```

---

## Common Patterns

### Pattern 1: Linear / radial gradient

```glsl
precision highp float;
uniform vec2 u_resolution;
uniform float u_time;

void main() {
  vec2 uv = gl_FragCoord.xy / u_resolution.xy;
  vec3 a = vec3(0.1, 0.1, 0.3);
  vec3 b = vec3(0.9, 0.3, 0.6);
  vec3 color = mix(a, b, uv.y + 0.1 * sin(u_time + uv.x * 6.28));
  gl_FragColor = vec4(color, 1.0);
}
```

### Pattern 2: Value noise + fbm

```glsl
float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }

float noise(vec2 p) {
  vec2 i = floor(p), f = fract(p);
  vec2 u = f * f * (3.0 - 2.0 * f);
  return mix(mix(hash(i), hash(i + vec2(1,0)), u.x),
             mix(hash(i + vec2(0,1)), hash(i + vec2(1,1)), u.x), u.y);
}

float fbm(vec2 p) {
  float v = 0.0, a = 0.5;
  for (int i = 0; i < 5; i++) { v += a * noise(p); p *= 2.0; a *= 0.5; }
  return v;
}
```

### Pattern 3: Signed distance field (circle)

```glsl
// Negative inside, positive outside; smoothstep gives an anti-aliased edge
float sdCircle(vec2 p, float r) { return length(p) - r; }

void main() {
  vec2 uv = (gl_FragCoord.xy * 2.0 - u_resolution.xy) / u_resolution.y;
  float d = sdCircle(uv, 0.5);
  float mask = 1.0 - smoothstep(0.0, 0.01, d);
  gl_FragColor = vec4(vec3(mask), 1.0);
}
```

### Pattern 4: Repeating pattern (grid)

```glsl
vec2 uv = gl_FragCoord.xy / u_resolution.xy;
vec2 g = fract(uv * 10.0) - 0.5;      // tile and center each cell
float dots = 1.0 - smoothstep(0.2, 0.22, length(g));
```

### Pattern 5: Raymarching a sphere (minimal)

```glsl
float map(vec3 p) { return length(p) - 1.0; } // one sphere

void main() {
  vec2 uv = (gl_FragCoord.xy * 2.0 - u_resolution.xy) / u_resolution.y;
  vec3 ro = vec3(0.0, 0.0, 3.0);          // ray origin
  vec3 rd = normalize(vec3(uv, -1.5));    // ray direction
  float t = 0.0;
  for (int i = 0; i < 64; i++) {
    vec3 p = ro + rd * t;
    float d = map(p);
    if (d < 0.001 || t > 20.0) break;
    t += d;
  }
  vec3 col = (t < 20.0) ? vec3(1.0 - t * 0.2) : vec3(0.05);
  gl_FragColor = vec4(col, 1.0);
}
```

### Pattern 6: Three.js ShaderMaterial

```js
import * as THREE from 'three'

const material = new THREE.ShaderMaterial({
  uniforms: {
    u_time: { value: 0 },
    u_resolution: { value: new THREE.Vector2() },
  },
  vertexShader: /* glsl */ `
    varying vec2 vUv;
    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: /* glsl */ `
    precision highp float;
    varying vec2 vUv;
    uniform float u_time;
    void main() {
      gl_FragColor = vec4(vUv, abs(sin(u_time)), 1.0);
    }
  `,
})

// In the render loop:
material.uniforms.u_time.value = clock.getElapsedTime()
```

---

## Integration Patterns

- **Three.js**: `ShaderMaterial` auto-provides `position`, `uv`, `normal`, and matrices; `RawShaderMaterial` provides nothing — declare everything. See `threejs-webgl`.
- **React Three Fiber**: Wrap a `shaderMaterial` (drei's `shaderMaterial` helper) and update uniforms in `useFrame`. See `react-three-fiber`.
- **GSAP / scroll**: Animate a uniform (e.g. `u_progress`) from scroll or a timeline. See `gsap-scrolltrigger`, `lenis-smooth-scroll`.
- **Post-processing**: Render the scene to a `WebGLRenderTarget`, then draw a full-screen quad with a fragment shader sampling it.
- **Vanta/backgrounds**: Full-screen fragment shaders make lightweight animated backgrounds. See `lightweight-3d-effects`.

---

## Performance Optimization

- **Set precision deliberately**: `highp` for positions/raymarching; `mediump` is cheaper where banding is acceptable (especially mobile).
- **Avoid dynamic branching** in hot loops; prefer `mix`/`step`/`smoothstep` over `if`.
- **Keep loops bounded** with constant iteration counts (GLSL requires it in ES 1.00) and `break` early.
- **Minimize texture lookups** and avoid dependent (computed-coordinate) reads where possible.
- **Reduce overdraw**: render full-screen effects on a single triangle/quad, not many layers.
- **Lower resolution** for expensive effects (render to a smaller target and upscale).
- **Precompute on CPU** what doesn't vary per pixel and pass as uniforms.

---

## Common Pitfalls

- **Missing precision qualifier**: fragment shaders need `precision ... float;` in GLSL ES 1.00 or they fail to compile.
- **WebGL1/WebGL2 mismatch**: mixing `gl_FragColor` with `#version 300 es`, or `varying` with `in/out`, fails. Pick one dialect.
- **Flipped Y**: `gl_FragCoord` origin is bottom-left; textures/UVs may need `uv.y = 1.0 - uv.y`.
- **No aspect correction**: circles become ellipses — normalize by `u_resolution.y`.
- **Integer/float types**: `1` is an int; write `1.0`. `2.0 / u.x` not `2 / u.x`.
- **Unbounded loops**: ES 1.00 disallows non-constant loop bounds; use a constant max and `break`.
- **Uniform not updated**: forgetting to set `u_time`/`u_resolution` each frame or on resize.
- **NaN from `pow(negative, x)`**: guard with `abs()` or `max()`.

---

## Resources

**Scripts** (`scripts/`):
- `generate_shader.py` — Generate a fragment shader from a preset (gradient, noise, pattern, sdf, raymarch), targeting raw GLSL or Three.js
- `setup_webgl.py` — Generate raw WebGL boilerplate (full-screen quad, compile/link with error handling, `u_time`/`u_resolution`/`u_mouse`)

**References** (`references/`):
- `api_reference.md` — GLSL types, qualifiers, built-in functions, WebGL setup, and the GLSL ES 1.00 vs 3.00 cheat sheet

**Assets** (`assets/`):
- `starter_shader/` — Minimal Vite starter: a full-screen animated fragment shader via raw WebGL

**Reference links**:
- The Book of Shaders: https://thebookofshaders.com/
- MDN WebGL: https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API
- Inigo Quilez (SDF/raymarching): https://iquilezles.org/articles/

## Related Skills

- `threejs-webgl` — Scenes and materials that host shaders
- `react-three-fiber` — Declarative shader materials in React
- `lightweight-3d-effects` — Shader backgrounds (Vanta.js)
- `gsap-scrolltrigger` / `lenis-smooth-scroll` — Drive shader uniforms from motion/scroll
