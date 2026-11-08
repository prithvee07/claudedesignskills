# GLSL & WebGL Reference

Reference for writing GLSL shaders for WebGL and Three.js on the web.

## GLSL Types

| Type | Description |
| --- | --- |
| `float`, `int`, `bool` | Scalars |
| `vec2`, `vec3`, `vec4` | Float vectors |
| `ivec2/3/4`, `bvec2/3/4` | Int / bool vectors |
| `mat2`, `mat3`, `mat4` | Square matrices |
| `sampler2D`, `samplerCube` | Texture handles |

Swizzling: `v.xy`, `v.rgb`, `v.xxyy`. Construction: `vec3(1.0)`,
`vec4(rgb, 1.0)`.

## Qualifiers

| Qualifier | Stage | Meaning |
| --- | --- | --- |
| `attribute` (ES1) / `in` (ES3) | vertex | Per-vertex input |
| `uniform` | both | Constant across the draw call |
| `varying` (ES1) / `out`→`in` (ES3) | v→f | Interpolated per-fragment value |
| `const` | both | Compile-time constant |
| `precision` | both | `lowp` / `mediump` / `highp` |

Fragment shaders require a default float precision in ES 1.00:
```glsl
precision highp float;
```

## Built-in Functions (common)

| Category | Functions |
| --- | --- |
| Trig | `sin cos tan asin acos atan radians degrees` |
| Exponential | `pow exp log exp2 log2 sqrt inversesqrt` |
| Common | `abs sign floor ceil fract mod min max clamp` |
| Interpolation | `mix step smoothstep` |
| Geometric | `length distance dot cross normalize reflect refract` |
| Vector relational | `lessThan greaterThan equal any all` |
| Texture | `texture2D` (ES1) / `texture` (ES3) |
| Derivatives | `dFdx dFdy fwidth` (fragment only) |

Key ones for procedural work:
- `mix(a, b, t)` — linear blend
- `step(edge, x)` — 0 or 1
- `smoothstep(e0, e1, x)` — smooth 0→1 (anti-aliasing)
- `fract(x)` — repeat / tiling
- `clamp(x, 0.0, 1.0)` — saturate

## Standard Web Shader Uniforms

```glsl
uniform vec2  u_resolution; // px
uniform float u_time;       // seconds
uniform vec2  u_mouse;      // px
```

## Coordinate Recipes

```glsl
vec2 uv = gl_FragCoord.xy / u_resolution.xy;                 // 0..1
vec2 c  = (gl_FragCoord.xy * 2.0 - u_resolution) / u_resolution.y; // centered, aspect-correct
uv.y = 1.0 - uv.y;                                          // flip Y for textures
```

## GLSL ES 1.00 vs 3.00

**ES 1.00 (WebGL1) fragment shader**
```glsl
precision highp float;
varying vec2 vUv;
uniform sampler2D u_tex;
void main() {
  gl_FragColor = texture2D(u_tex, vUv);
}
```

**ES 3.00 (WebGL2) fragment shader**
```glsl
#version 300 es
precision highp float;
in vec2 vUv;
uniform sampler2D u_tex;
out vec4 fragColor;
void main() {
  fragColor = texture(u_tex, vUv);
}
```

`#version 300 es` must be the very first line (no comment/whitespace before it).

## Raw WebGL Setup (essentials)

```js
const gl = canvas.getContext('webgl') // or 'webgl2'

function compile(type, src) {
  const s = gl.createShader(type)
  gl.shaderSource(s, src)
  gl.compileShader(s)
  if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) {
    throw new Error(gl.getShaderInfoLog(s))
  }
  return s
}

const program = gl.createProgram()
gl.attachShader(program, compile(gl.VERTEX_SHADER, vertSrc))
gl.attachShader(program, compile(gl.FRAGMENT_SHADER, fragSrc))
gl.linkProgram(program)
if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
  throw new Error(gl.getProgramInfoLog(program))
}
gl.useProgram(program)
```

Full-screen quad as two triangles:
```js
const buf = gl.createBuffer()
gl.bindBuffer(gl.ARRAY_BUFFER, buf)
gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([
  -1, -1,  1, -1,  -1, 1,
  -1,  1,  1, -1,   1, 1,
]), gl.STATIC_DRAW)
const loc = gl.getAttribLocation(program, 'a_position')
gl.enableVertexAttribArray(loc)
gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0)
```

Set uniforms each frame:
```js
gl.uniform1f(gl.getUniformLocation(program, 'u_time'), t)
gl.uniform2f(gl.getUniformLocation(program, 'u_resolution'), canvas.width, canvas.height)
gl.drawArrays(gl.TRIANGLES, 0, 6)
```

Handle resize (match drawing buffer to CSS size × dpr):
```js
function resize() {
  const dpr = Math.min(window.devicePixelRatio, 2)
  canvas.width = canvas.clientWidth * dpr
  canvas.height = canvas.clientHeight * dpr
  gl.viewport(0, 0, canvas.width, canvas.height)
}
```

## Three.js ShaderMaterial vs RawShaderMaterial

| | `ShaderMaterial` | `RawShaderMaterial` |
| --- | --- | --- |
| Auto attributes | `position`, `uv`, `normal` | none |
| Auto uniforms | `projectionMatrix`, `modelViewMatrix`, `normalMatrix`, etc. | none |
| Boilerplate | low | you declare everything |

Pass GLSL as template strings; tag with `/* glsl */` for editor highlighting.
Update `material.uniforms.NAME.value` in the render loop.

## Debugging Tips

- Log `gl.getShaderInfoLog` / `gl.getProgramInfoLog` — they name the line.
- Output intermediate values as color: `gl_FragColor = vec4(vec3(d), 1.0);`.
- Check for `NaN` (black/weird artifacts) from `pow`, `sqrt`, or divide-by-zero.
- Confirm WebGL1 vs WebGL2 context matches the GLSL dialect.
