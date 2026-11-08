import Matter from 'matter-js'

const { Engine, Render, Runner, Bodies, Composite, Mouse, MouseConstraint } = Matter

const container = document.querySelector('#world')
const W = window.innerWidth
const H = window.innerHeight

const engine = Engine.create({ enableSleeping: true })

const render = Render.create({
  element: container,
  engine,
  options: {
    width: W,
    height: H,
    wireframes: false,
    background: '#0b0b12',
    pixelRatio: Math.min(window.devicePixelRatio, 2),
  },
})
Render.run(render)
const runner = Runner.create()
Runner.run(runner, engine)

const palette = ['#7b5cff', '#ff4dd8', '#4dd8ff', '#ffd24d']

function walls() {
  return [
    Bodies.rectangle(W / 2, -10, W + 20, 20, { isStatic: true }),
    Bodies.rectangle(W / 2, H + 10, W + 20, 20, { isStatic: true }),
    Bodies.rectangle(-10, H / 2, 20, H + 20, { isStatic: true }),
    Bodies.rectangle(W + 10, H / 2, 20, H + 20, { isStatic: true }),
  ]
}

function spawnShapes(n = 28) {
  const bodies = []
  for (let i = 0; i < n; i++) {
    const x = 80 + Math.random() * (W - 160)
    const r = 16 + Math.random() * 28
    const body = Math.random() > 0.5
      ? Bodies.circle(x, -40 - i * 25, r, { restitution: 0.6 })
      : Bodies.rectangle(x, -40 - i * 25, r * 2, r * 2, { restitution: 0.4 })
    body.render.fillStyle = palette[i % palette.length]
    bodies.push(body)
  }
  return bodies
}

function populate() {
  Composite.add(engine.world, [...walls(), ...spawnShapes()])
}
populate()

// Dragging
const mouse = Mouse.create(render.canvas)
const mouseConstraint = MouseConstraint.create(engine, {
  mouse,
  constraint: { stiffness: 0.2, render: { visible: false } },
})
Composite.add(engine.world, mouseConstraint)
render.mouse = mouse

// HUD controls
document.querySelector('#gravity').addEventListener('click', () => {
  engine.gravity.y = engine.gravity.y === 0 ? 1 : 0
})
document.querySelector('#reset').addEventListener('click', () => {
  Composite.clear(engine.world, false)
  Composite.add(engine.world, mouseConstraint)
  populate()
})
