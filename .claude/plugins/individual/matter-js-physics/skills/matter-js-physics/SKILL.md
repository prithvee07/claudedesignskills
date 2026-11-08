---
name: matter-js-physics
description: Add 2D rigid-body physics to the web with Matter.js - gravity, collisions, dragging, and constraints. Use when building playful interactive designs like falling shapes, draggable objects, physics-based hero sections, pinball/toy interactions, or DOM elements driven by a physics simulation. Triggers on tasks involving Matter.js, 2D physics, rigid bodies, gravity, collisions, MouseConstraint dragging, constraints/chains, or syncing DOM elements to a physics world. Lightweight 2D physics engine for canvas or DOM, distinct from 3D engines like Babylon.js.
---

# Matter.js Physics

## Overview

Matter.js is a 2D rigid-body physics engine for the web. It simulates gravity, collisions, friction, and constraints, and renders to a canvas (or drives DOM/SVG elements). It's ideal for playful, interactive design moments.

**When to Use This Skill**:
- Falling / stacking shapes and "toy box" interactions
- Draggable, bouncy objects in a hero or 404 page
- Physics-based layouts where DOM elements tumble or settle
- Pinball-style toys, chains, pendulums, ragdolls
- Any 2D simulation with gravity, collisions, and dragging

**Core objects**:
- **Engine** — the simulation (holds the world and gravity)
- **World / Composite** — the container of bodies and constraints
- **Bodies** — rectangles, circles, polygons (static or dynamic)
- **Render** — optional built-in canvas renderer
- **Runner** — advances the engine each frame
- **MouseConstraint** — drag bodies with the pointer
- **Constraint** — springs/links between bodies or points

---

## Core Concepts

### 1. Minimal setup (canvas render)

```js
import Matter from 'matter-js'
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

// A falling box and a static ground
const box = Bodies.rectangle(400, 100, 80, 80, { restitution: 0.6 })
const ground = Bodies.rectangle(400, 590, 800, 20, { isStatic: true })
Composite.add(engine.world, [box, ground])
```

### 2. Bodies and options

```js
Bodies.rectangle(x, y, w, h, opts)
Bodies.circle(x, y, radius, opts)
Bodies.polygon(x, y, sides, radius, opts)

// Common options:
{
  isStatic: false,     // immovable if true
  restitution: 0.6,    // bounciness (0..1)
  friction: 0.1,       // surface friction
  frictionAir: 0.01,   // air drag
  density: 0.001,      // mass per area
  render: { fillStyle: '#7b5cff' },
}
```

### 3. Dragging with MouseConstraint

```js
const { Mouse, MouseConstraint } = Matter
const mouse = Mouse.create(render.canvas)
const mouseConstraint = MouseConstraint.create(engine, {
  mouse,
  constraint: { stiffness: 0.2, render: { visible: false } },
})
Composite.add(engine.world, mouseConstraint)
render.mouse = mouse // keep render in sync
```

### 4. Gravity

```js
engine.gravity.y = 1    // default downward
engine.gravity.y = 0    // zero-g
engine.gravity.x = 0.3  // sideways pull
engine.gravity.scale = 0.001 // strength multiplier
```

### 5. Events

```js
const { Events } = Matter
Events.on(engine, 'collisionStart', ({ pairs }) => {
  pairs.forEach(({ bodyA, bodyB }) => { /* react to a hit */ })
})
Events.on(engine, 'afterUpdate', () => { /* runs each simulation step */ })
```

---

## Common Patterns

### Pattern 1: Walls / boundaries

```js
const walls = [
  Bodies.rectangle(400, -10, 810, 20, { isStatic: true }), // top
  Bodies.rectangle(400, 610, 810, 20, { isStatic: true }), // bottom
  Bodies.rectangle(-10, 300, 20, 620, { isStatic: true }), // left
  Bodies.rectangle(810, 300, 20, 620, { isStatic: true }), // right
]
Composite.add(engine.world, walls)
```

### Pattern 2: A pile of random shapes

```js
for (let i = 0; i < 40; i++) {
  const x = 100 + Math.random() * 600
  const r = 12 + Math.random() * 24
  const body = Math.random() > 0.5
    ? Bodies.circle(x, -50 - i * 30, r, { restitution: 0.5 })
    : Bodies.rectangle(x, -50 - i * 30, r * 2, r * 2, { restitution: 0.4 })
  body.render.fillStyle = ['#7b5cff', '#ff4dd8', '#4dd8ff'][i % 3]
  Composite.add(engine.world, body)
}
```

### Pattern 3: Constraints (pendulum)

```js
const { Constraint } = Matter
const bob = Bodies.circle(400, 300, 30)
const string = Constraint.create({
  pointA: { x: 400, y: 100 }, // fixed anchor
  bodyB: bob,
  stiffness: 0.9,
  length: 200,
})
Composite.add(engine.world, [bob, string])
```

### Pattern 4: Chain

```js
const { Composites, Body } = Matter
const chain = Composites.stack(200, 100, 8, 1, 10, 10, (x, y) =>
  Bodies.rectangle(x, y, 40, 12))
Composites.chain(chain, 0.5, 0, -0.5, 0, { stiffness: 0.8, length: 2 })
// Pin the first link
chain.bodies[0].isStatic = true
Composite.add(engine.world, chain)
```

### Pattern 5: DOM-synced physics (no canvas)

Run the engine headless and apply body transforms to DOM elements.

```js
const engine = Engine.create()
const items = [...document.querySelectorAll('.chip')].map((el, i) => {
  const b = Bodies.rectangle(100 + i * 60, -100, el.offsetWidth, el.offsetHeight, { restitution: 0.5 })
  return { el, body: b }
})
Composite.add(engine.world, [
  ...items.map((i) => i.body),
  Bodies.rectangle(innerWidth / 2, innerHeight, innerWidth, 40, { isStatic: true }),
])

Events.on(engine, 'afterUpdate', () => {
  for (const { el, body } of items) {
    el.style.transform =
      `translate(${body.position.x - el.offsetWidth / 2}px, ${body.position.y - el.offsetHeight / 2}px) rotate(${body.angle}rad)`
  }
})
Runner.run(Runner.create(), engine)
```

### Pattern 6: Toggle gravity / reset

```js
function toggleGravity() { engine.gravity.y = engine.gravity.y === 0 ? 1 : 0 }
function reset() { Composite.clear(engine.world, false); /* re-add walls + bodies */ }
```

---

## Integration Patterns

- **GSAP / scroll**: trigger a drop or change gravity on scroll. See `gsap-scrolltrigger`, `lenis-smooth-scroll`.
- **DOM / React**: run headless and sync body positions to elements (Pattern 5); in React, drive refs in an effect loop. See `animated-component-libraries`.
- **PixiJS / canvas**: render bodies yourself with Pixi for styled sprites instead of the debug renderer. See `pixijs-2d`.
- **Responsive**: recompute wall positions and `Render` size on resize.

---

## Performance Optimization

- **Cap body count**: hundreds of bodies strain the solver; remove off-screen bodies.
- **Sleeping**: enable `engine.enableSleeping = true` so settled bodies stop computing.
- **Simpler shapes**: circles and boxes are cheaper than many-sided polygons; avoid complex concave bodies (decompose or approximate).
- **Fixed timestep**: let `Runner` manage timing; avoid manually calling `Engine.update` with wildly variable deltas.
- **Headless + own render**: for many styled elements, skip the built-in `Render` and draw with Canvas/Pixi.
- **Throttle DOM sync**: batch style writes in the `afterUpdate` handler; use `transform` only.

---

## Common Pitfalls

- **Tunneling**: fast bodies pass through thin walls. Use thicker walls, lower speeds, or increase solver iterations (`engine.positionIterations`, `engine.velocityIterations`).
- **Mouse drag not working**: forgot `render.mouse = mouse`, or the canvas is covered by another element capturing events.
- **Deprecated `World`**: use `Composite.add(engine.world, ...)` rather than the old `World.add`.
- **Memory leaks**: not calling `Render.stop`, `Runner.stop`, and `Engine.clear` on teardown (especially in SPAs/React).
- **Scaling bodies**: resizing a canvas doesn't move bodies; reposition static walls on resize.
- **Layout reads in loop**: reading `offsetWidth` every frame in DOM sync causes reflow; cache sizes.
- **Pixel ratio**: on HiDPI, set `render.options.pixelRatio` for crisp rendering.

---

## Resources

**Scripts** (`scripts/`):
- `init_matter.py` — Scaffold a Matter.js setup from a preset: `basic`, `draggable`, `dom-sync`
- `generate_body.py` — Generate `Bodies.*` creation code for shapes (rectangle, circle, polygon) with options

**References** (`references/`):
- `api_reference.md` — Modules, body/constraint options, events, mouse, and teardown

**Assets** (`assets/`):
- `starter_matter/` — Vite starter: falling, draggable, bouncy shapes in a bounded world

**Official**:
- Docs: https://brm.io/matter-js/docs/
- Demos: https://brm.io/matter-js/demo/

## Related Skills

- `pixijs-2d` — Render physics bodies as styled sprites
- `gsap-scrolltrigger` / `lenis-smooth-scroll` — Trigger physics from scroll
- `babylonjs-engine` — 3D physics when 2D isn't enough
- `animated-component-libraries` — DOM-synced physics in component UIs
