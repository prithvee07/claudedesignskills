#!/usr/bin/env python3
"""
GLSL Fragment Shader Generator

Generates a fragment shader from a preset, as raw GLSL or wrapped in a Three.js
ShaderMaterial. All presets use the standard uniforms u_resolution, u_time, and
u_mouse.

Usage:
    ./generate_shader.py                              # interactive
    ./generate_shader.py --type gradient
    ./generate_shader.py --type raymarch --target three
    ./generate_shader.py --type noise --output src/shader.frag

Types:
    gradient - animated two-color gradient
    noise    - value noise + fbm field
    pattern  - repeating grid of dots
    sdf      - signed-distance circle with anti-aliased edge
    raymarch - minimal raymarched sphere

Targets:
    glsl  - a standalone fragment shader (default)
    three - a THREE.ShaderMaterial(...) JavaScript snippet

Dependencies: Python 3 standard library only.
"""

import argparse
import sys

HEADER = """precision highp float;

uniform vec2 u_resolution;
uniform float u_time;
uniform vec2 u_mouse;
"""

BODIES = {
    'gradient': """
void main() {
  vec2 uv = gl_FragCoord.xy / u_resolution.xy;
  vec3 a = vec3(0.10, 0.10, 0.30);
  vec3 b = vec3(0.90, 0.30, 0.60);
  float t = uv.y + 0.10 * sin(u_time + uv.x * 6.2831);
  gl_FragColor = vec4(mix(a, b, t), 1.0);
}
""",
    'noise': """
float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }

float noise(vec2 p) {
  vec2 i = floor(p), f = fract(p);
  vec2 u = f * f * (3.0 - 2.0 * f);
  return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), u.x),
             mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), u.x), u.y);
}

float fbm(vec2 p) {
  float v = 0.0, a = 0.5;
  for (int i = 0; i < 5; i++) { v += a * noise(p); p *= 2.0; a *= 0.5; }
  return v;
}

void main() {
  vec2 uv = gl_FragCoord.xy / u_resolution.xy;
  float n = fbm(uv * 4.0 + u_time * 0.2);
  gl_FragColor = vec4(vec3(n), 1.0);
}
""",
    'pattern': """
void main() {
  vec2 uv = gl_FragCoord.xy / u_resolution.xy;
  uv.x *= u_resolution.x / u_resolution.y;
  vec2 g = fract(uv * 10.0 + u_time * 0.1) - 0.5;
  float dots = 1.0 - smoothstep(0.18, 0.22, length(g));
  gl_FragColor = vec4(vec3(dots), 1.0);
}
""",
    'sdf': """
float sdCircle(vec2 p, float r) { return length(p) - r; }

void main() {
  vec2 uv = (gl_FragCoord.xy * 2.0 - u_resolution.xy) / u_resolution.y;
  float r = 0.4 + 0.05 * sin(u_time);
  float d = sdCircle(uv, r);
  float mask = 1.0 - smoothstep(0.0, 0.01, d);
  gl_FragColor = vec4(vec3(mask) * vec3(0.8, 0.4, 1.0), 1.0);
}
""",
    'raymarch': """
float map(vec3 p) { return length(p) - 1.0; }

void main() {
  vec2 uv = (gl_FragCoord.xy * 2.0 - u_resolution.xy) / u_resolution.y;
  vec3 ro = vec3(0.0, 0.0, 3.0);
  vec3 rd = normalize(vec3(uv, -1.5));
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
""",
}


def raw_glsl(kind: str) -> str:
    return HEADER + BODIES[kind]


def three_wrapper(kind: str) -> str:
    frag = (HEADER + BODIES[kind]).strip()
    # Indent the GLSL for readability inside the template literal
    indented = '\n'.join('    ' + line if line else '' for line in frag.splitlines())
    return f'''import * as THREE from 'three'

export const material = new THREE.ShaderMaterial({{
  uniforms: {{
    u_time: {{ value: 0 }},
    u_resolution: {{ value: new THREE.Vector2() }},
    u_mouse: {{ value: new THREE.Vector2() }},
  }},
  vertexShader: /* glsl */ `
    varying vec2 vUv;
    void main() {{
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }}
  `,
  fragmentShader: /* glsl */ `
{indented}
  `,
}})

// In your render loop:
//   material.uniforms.u_time.value = clock.getElapsedTime()
//   material.uniforms.u_resolution.value.set(width, height)
'''


def main() -> int:
    parser = argparse.ArgumentParser(description='Generate a GLSL fragment shader.')
    parser.add_argument('--type', choices=sorted(BODIES), help='Shader preset')
    parser.add_argument('--target', choices=['glsl', 'three'], default='glsl')
    parser.add_argument('--output', help='Write to file instead of stdout')
    args = parser.parse_args()

    kind = args.type
    if not kind:
        print('Available types: ' + ', '.join(sorted(BODIES)))
        try:
            kind = input('Choose type [gradient]: ').strip() or 'gradient'
        except (EOFError, KeyboardInterrupt):
            print()
            return 1
        if kind not in BODIES:
            print(f"Error: unknown type '{kind}'", file=sys.stderr)
            return 1

    code = three_wrapper(kind) if args.target == 'three' else raw_glsl(kind)

    if args.output:
        try:
            with open(args.output, 'w') as fh:
                fh.write(code)
            print(f'Wrote {kind} shader ({args.target}) to {args.output}')
        except OSError as exc:
            print(f'Error writing file: {exc}', file=sys.stderr)
            return 1
    else:
        print(code)
    return 0


if __name__ == '__main__':
    sys.exit(main())
