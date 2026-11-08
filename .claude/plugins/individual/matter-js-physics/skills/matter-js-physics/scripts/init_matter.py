#!/usr/bin/env python3
"""
Matter.js Boilerplate Generator

Generates a Matter.js setup from a preset. Each preset includes a bounded world
and teardown-friendly structure.

Usage:
    ./init_matter.py                       # interactive
    ./init_matter.py --preset basic        # canvas render + falling box + ground
    ./init_matter.py --preset draggable    # pile of shapes you can drag
    ./init_matter.py --preset dom-sync      # headless engine driving DOM elements
    ./init_matter.py --preset draggable --output src/physics.js

Presets:
    basic     - minimal engine, render, runner, a falling box and ground
    draggable - bounded world, random shapes, MouseConstraint dragging
    dom-sync  - headless engine syncing .chip elements to body transforms

Dependencies: Python 3 standard library only.
"""

import argparse
import sys

BASIC = """import Matter from 'matter-js'

const { Engine, Render, Runner, Bodies, Composite } = Matter

const engine = Engine.create()

const render = Render.create({
  element: document.body,
  engine,
  options: { width: 800, height: 600, wireframes: false, background: '#0b0b12' },
})
Render.run(render)

const runner = Runner.create()
Runner.run(runner, engine)

const box = Bodies.rectangle(400, 100, 80, 80, {
  restitution: 0.6,
  render: { fillStyle: '#7b5cff' },
})
const ground = Bodies.rectangle(400, 590, 800, 20, { isStatic: true })
Composite.add(engine.world, [box, ground])

// Teardown when needed:
// Render.stop(render); Runner.stop(runner); Engine.clear(engine); render.canvas.remove()
"""

DRAGGABLE = """import Matter from 'matter-js'

const { Engine, Render, Runner, Bodies, Composite, Mouse, MouseConstraint } = Matter

const W = 800
const H = 600

const engine = Engine.create({ enableSleeping: true })

const render = Render.create({
  element: document.body,
  engine,
  options: { width: W, height: H, wireframes: false, background: '#0b0b12' },
})
Render.run(render)
Runner.run(Runner.create(), engine)

// Bounded world
const walls = [
  Bodies.rectangle(W / 2, -10, W + 20, 20, { isStatic: true }),
  Bodies.rectangle(W / 2, H + 10, W + 20, 20, { isStatic: true }),
  Bodies.rectangle(-10, H / 2, 20, H + 20, { isStatic: true }),
  Bodies.rectangle(W + 10, H / 2, 20, H + 20, { isStatic: true }),
]
Composite.add(engine.world, walls)

// Random shapes
const palette = ['#7b5cff', '#ff4dd8', '#4dd8ff']
for (let i = 0; i < 30; i++) {
  const x = 100 + Math.random() * (W - 200)
  const r = 14 + Math.random() * 26
  const body = Math.random() > 0.5
    ? Bodies.circle(x, -40 - i * 25, r, { restitution: 0.6 })
    : Bodies.rectangle(x, -40 - i * 25, r * 2, r * 2, { restitution: 0.4 })
  body.render.fillStyle = palette[i % palette.length]
  Composite.add(engine.world, body)
}

// Dragging
const mouse = Mouse.create(render.canvas)
const mouseConstraint = MouseConstraint.create(engine, {
  mouse,
  constraint: { stiffness: 0.2, render: { visible: false } },
})
Composite.add(engine.world, mouseConstraint)
render.mouse = mouse
"""

DOM_SYNC = """import Matter from 'matter-js'

const { Engine, Runner, Bodies, Composite, Events } = Matter

// Expects elements with class .chip in the DOM
const engine = Engine.create()

const chips = [...document.querySelectorAll('.chip')].map((el, i) => {
  const w = el.offsetWidth
  const h = el.offsetHeight
  const body = Bodies.rectangle(80 + i * 70, -80 - i * 40, w, h, {
    restitution: 0.5,
    frictionAir: 0.02,
  })
  return { el, body, w, h } // cache sizes to avoid per-frame reflow
})

const floor = Bodies.rectangle(innerWidth / 2, innerHeight + 10, innerWidth * 2, 40, { isStatic: true })
const left = Bodies.rectangle(-10, innerHeight / 2, 20, innerHeight * 2, { isStatic: true })
const right = Bodies.rectangle(innerWidth + 10, innerHeight / 2, 20, innerHeight * 2, { isStatic: true })

Composite.add(engine.world, [...chips.map((c) => c.body), floor, left, right])

Events.on(engine, 'afterUpdate', () => {
  for (const { el, body, w, h } of chips) {
    el.style.transform =
      `translate(${body.position.x - w / 2}px, ${body.position.y - h / 2}px) rotate(${body.angle}rad)`
  }
})

Runner.run(Runner.create(), engine)
"""

PRESETS = {'basic': BASIC, 'draggable': DRAGGABLE, 'dom-sync': DOM_SYNC}


def main() -> int:
    parser = argparse.ArgumentParser(description='Generate Matter.js boilerplate.')
    parser.add_argument('--preset', choices=sorted(PRESETS), help='Boilerplate preset')
    parser.add_argument('--output', help='Write to a file instead of stdout')
    args = parser.parse_args()

    preset = args.preset
    if not preset:
        print('Available presets: ' + ', '.join(sorted(PRESETS)))
        try:
            preset = input('Choose preset [basic]: ').strip() or 'basic'
        except (EOFError, KeyboardInterrupt):
            print()
            return 1
        if preset not in PRESETS:
            print(f"Error: unknown preset '{preset}'", file=sys.stderr)
            return 1

    code = PRESETS[preset]

    if args.output:
        try:
            with open(args.output, 'w') as fh:
                fh.write(code)
            print(f'Wrote {preset} boilerplate to {args.output}')
        except OSError as exc:
            print(f'Error writing file: {exc}', file=sys.stderr)
            return 1
    else:
        print(code)
    return 0


if __name__ == '__main__':
    sys.exit(main())
