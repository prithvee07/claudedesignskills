#!/usr/bin/env python3
"""
Raw WebGL Full-Screen Shader Boilerplate Generator

Generates a self-contained JavaScript module that compiles and runs a
full-screen fragment shader with the standard uniforms u_resolution, u_time,
and u_mouse. Includes compile/link error handling, DPR-aware resize, and a
pointer handler.

Usage:
    ./setup_webgl.py                        # WebGL1 boilerplate to stdout
    ./setup_webgl.py --webgl2               # WebGL2 (GLSL ES 3.00) boilerplate
    ./setup_webgl.py --frag shader.frag     # load the fragment source at runtime via fetch
    ./setup_webgl.py --output src/gl.js

Options:
    --webgl2   Emit a WebGL2 context + GLSL ES 3.00 default fragment shader
    --frag     Reference an external .frag file (fetched) instead of inlining
    --output   Write to a file instead of stdout

Dependencies: Python 3 standard library only.
"""

import argparse
import sys

INLINE_FRAG_1 = r"""precision highp float;
uniform vec2 u_resolution;
uniform float u_time;
uniform vec2 u_mouse;
void main() {
  vec2 uv = gl_FragCoord.xy / u_resolution.xy;
  gl_FragColor = vec4(uv, abs(sin(u_time)), 1.0);
}"""

INLINE_FRAG_3 = r"""#version 300 es
precision highp float;
uniform vec2 u_resolution;
uniform float u_time;
uniform vec2 u_mouse;
out vec4 fragColor;
void main() {
  vec2 uv = gl_FragCoord.xy / u_resolution.xy;
  fragColor = vec4(uv, abs(sin(u_time)), 1.0);
}"""

VERT_1 = "attribute vec2 a_position; void main() { gl_Position = vec4(a_position, 0.0, 1.0); }"
VERT_3 = "#version 300 es\nin vec2 a_position; void main() { gl_Position = vec4(a_position, 0.0, 1.0); }"


def build(webgl2: bool, frag_path: str | None) -> str:
    ctx = "'webgl2'" if webgl2 else "'webgl'"
    vert = VERT_3 if webgl2 else VERT_1
    default_frag = INLINE_FRAG_3 if webgl2 else INLINE_FRAG_1

    if frag_path:
        frag_setup = (
            f"const fragSource = await fetch('{frag_path}')"
            ".then((r) => r.text())"
        )
        async_kw = "async "
        run_call = "run()"
        wrapper_open = "async function run() {"
        wrapper_close = "}\nrun()"
    else:
        frag_setup = "const fragSource = DEFAULT_FRAG"
        async_kw = ""
        run_call = ""
        wrapper_open = ""
        wrapper_close = ""

    body = f'''// Raw WebGL full-screen fragment shader runner.
const canvas = document.querySelector('#gl') || document.body.appendChild(document.createElement('canvas'))
canvas.id = 'gl'
const gl = canvas.getContext({ctx})
if (!gl) throw new Error('WebGL not supported')

const VERT = `{vert}`
const DEFAULT_FRAG = `{default_frag}`

function compile(type, src) {{
  const s = gl.createShader(type)
  gl.shaderSource(s, src)
  gl.compileShader(s)
  if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) {{
    const log = gl.getShaderInfoLog(s)
    gl.deleteShader(s)
    throw new Error('Shader compile error: ' + log)
  }}
  return s
}}

function createProgram(vertSrc, fragSrc) {{
  const p = gl.createProgram()
  gl.attachShader(p, compile(gl.VERTEX_SHADER, vertSrc))
  gl.attachShader(p, compile(gl.FRAGMENT_SHADER, fragSrc))
  gl.linkProgram(p)
  if (!gl.getProgramParameter(p, gl.LINK_STATUS)) {{
    throw new Error('Program link error: ' + gl.getProgramInfoLog(p))
  }}
  return p
}}

{wrapper_open}
{frag_setup}
const program = createProgram(VERT, fragSource)
gl.useProgram(program)

// Full-screen quad (two triangles)
const buffer = gl.createBuffer()
gl.bindBuffer(gl.ARRAY_BUFFER, buffer)
gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([
  -1, -1, 1, -1, -1, 1,
  -1, 1, 1, -1, 1, 1,
]), gl.STATIC_DRAW)
const aPosition = gl.getAttribLocation(program, 'a_position')
gl.enableVertexAttribArray(aPosition)
gl.vertexAttribPointer(aPosition, 2, gl.FLOAT, false, 0, 0)

const uResolution = gl.getUniformLocation(program, 'u_resolution')
const uTime = gl.getUniformLocation(program, 'u_time')
const uMouse = gl.getUniformLocation(program, 'u_mouse')
const mouse = {{ x: 0, y: 0 }}

function resize() {{
  const dpr = Math.min(window.devicePixelRatio || 1, 2)
  canvas.width = Math.floor(canvas.clientWidth * dpr) || window.innerWidth
  canvas.height = Math.floor(canvas.clientHeight * dpr) || window.innerHeight
  gl.viewport(0, 0, canvas.width, canvas.height)
}}
window.addEventListener('resize', resize)
window.addEventListener('pointermove', (e) => {{
  mouse.x = e.clientX
  mouse.y = e.clientY
}})
resize()

const start = performance.now()
function frame() {{
  gl.uniform2f(uResolution, canvas.width, canvas.height)
  gl.uniform1f(uTime, (performance.now() - start) / 1000)
  gl.uniform2f(uMouse, mouse.x, mouse.y)
  gl.drawArrays(gl.TRIANGLES, 0, 6)
  requestAnimationFrame(frame)
}}
requestAnimationFrame(frame)
{wrapper_close}
'''
    # Clean up any empty async markers left unused
    _ = (async_kw, run_call)
    return body


def main() -> int:
    parser = argparse.ArgumentParser(description='Generate raw WebGL boilerplate.')
    parser.add_argument('--webgl2', action='store_true',
                        help='Use a WebGL2 context and GLSL ES 3.00 default shader')
    parser.add_argument('--frag',
                        help='External .frag path to fetch at runtime instead of inlining')
    parser.add_argument('--output', help='Write to a file instead of stdout')
    args = parser.parse_args()

    code = build(args.webgl2, args.frag)

    if args.output:
        try:
            with open(args.output, 'w') as fh:
                fh.write(code)
            print(f'Wrote WebGL boilerplate to {args.output}')
        except OSError as exc:
            print(f'Error writing file: {exc}', file=sys.stderr)
            return 1
    else:
        print(code)
    return 0


if __name__ == '__main__':
    sys.exit(main())
