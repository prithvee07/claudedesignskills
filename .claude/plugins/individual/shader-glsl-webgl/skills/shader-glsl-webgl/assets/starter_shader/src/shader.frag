precision highp float;

uniform vec2 u_resolution;
uniform float u_time;
uniform vec2 u_mouse;

float hash(vec2 p) {
  return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

float noise(vec2 p) {
  vec2 i = floor(p), f = fract(p);
  vec2 u = f * f * (3.0 - 2.0 * f);
  return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), u.x),
             mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), u.x), u.y);
}

float fbm(vec2 p) {
  float v = 0.0, a = 0.5;
  for (int i = 0; i < 6; i++) {
    v += a * noise(p);
    p *= 2.0;
    a *= 0.5;
  }
  return v;
}

void main() {
  // Aspect-corrected, centered coordinates
  vec2 uv = (gl_FragCoord.xy * 2.0 - u_resolution.xy) / u_resolution.y;

  // Flowing fbm field, nudged by the pointer
  vec2 m = (u_mouse / u_resolution.y);
  float n = fbm(uv * 1.5 + vec2(u_time * 0.1, u_time * 0.05) + m);

  // Map the field to a two-tone gradient
  vec3 a = vec3(0.05, 0.03, 0.16);
  vec3 b = vec3(0.55, 0.25, 0.85);
  vec3 color = mix(a, b, smoothstep(0.3, 0.8, n));

  gl_FragColor = vec4(color, 1.0);
}
