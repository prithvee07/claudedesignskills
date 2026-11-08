import fragSource from './shader.frag?raw'

const canvas = document.querySelector('#gl')
const gl = canvas.getContext('webgl')
if (!gl) throw new Error('WebGL not supported')

const VERT = 'attribute vec2 a_position; void main() { gl_Position = vec4(a_position, 0.0, 1.0); }'

function compile(type, src) {
  const s = gl.createShader(type)
  gl.shaderSource(s, src)
  gl.compileShader(s)
  if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) {
    const log = gl.getShaderInfoLog(s)
    gl.deleteShader(s)
    throw new Error('Shader compile error: ' + log)
  }
  return s
}

const program = gl.createProgram()
gl.attachShader(program, compile(gl.VERTEX_SHADER, VERT))
gl.attachShader(program, compile(gl.FRAGMENT_SHADER, fragSource))
gl.linkProgram(program)
if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
  throw new Error('Program link error: ' + gl.getProgramInfoLog(program))
}
gl.useProgram(program)

// Full-screen quad
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
const mouse = { x: 0, y: 0 }

function resize() {
  const dpr = Math.min(window.devicePixelRatio || 1, 2)
  canvas.width = Math.floor(window.innerWidth * dpr)
  canvas.height = Math.floor(window.innerHeight * dpr)
  gl.viewport(0, 0, canvas.width, canvas.height)
}
window.addEventListener('resize', resize)
window.addEventListener('pointermove', (e) => {
  mouse.x = e.clientX
  mouse.y = window.innerHeight - e.clientY // flip to match gl_FragCoord origin
})
resize()

const start = performance.now()
function frame() {
  gl.uniform2f(uResolution, canvas.width, canvas.height)
  gl.uniform1f(uTime, (performance.now() - start) / 1000)
  gl.uniform2f(uMouse, mouse.x * (window.devicePixelRatio || 1), mouse.y * (window.devicePixelRatio || 1))
  gl.drawArrays(gl.TRIANGLES, 0, 6)
  requestAnimationFrame(frame)
}
requestAnimationFrame(frame)
