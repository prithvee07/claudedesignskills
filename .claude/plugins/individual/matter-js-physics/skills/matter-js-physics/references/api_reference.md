# Matter.js API Reference

Reference for the `matter-js` 2D physics engine.

> Verify current module signatures at https://brm.io/matter-js/docs/.

## Installation

```bash
npm install matter-js
```

```js
import Matter from 'matter-js'
const { Engine, Render, Runner, Bodies, Composite, Body, Constraint,
        Composites, Mouse, MouseConstraint, Events, Vector } = Matter
```

## Core Modules

| Module | Purpose |
| --- | --- |
| `Engine` | Create/update the simulation; holds `world` and `gravity` |
| `Render` | Built-in canvas debug renderer (optional) |
| `Runner` | Game loop that steps the engine |
| `Bodies` | Factory for rectangle/circle/polygon/trapezoid bodies |
| `Body` | Operate on a body (setPosition, setVelocity, scale, rotate) |
| `Composite` | Add/remove/clear bodies and constraints (replaces `World`) |
| `Composites` | Helpers: `stack`, `chain`, `mesh`, `newtonsCradle` |
| `Constraint` | Springs/links between bodies or fixed points |
| `Mouse` / `MouseConstraint` | Pointer input and dragging |
| `Events` | Subscribe to engine/runner/render events |
| `Vector` | 2D vector math |

## Engine

```js
const engine = Engine.create({ enableSleeping: true })
engine.gravity.x = 0
engine.gravity.y = 1
engine.gravity.scale = 0.001
engine.positionIterations = 6  // raise to reduce tunneling
engine.velocityIterations = 4

Engine.update(engine, delta) // usually handled by Runner
Engine.clear(engine)         // teardown
```

## Render

```js
const render = Render.create({
  element: container,
  engine,
  options: {
    width: 800,
    height: 600,
    wireframes: false,       // false = filled styles
    background: '#0b0b12',
    pixelRatio: window.devicePixelRatio, // crisp on HiDPI
  },
})
Render.run(render)
Render.stop(render)          // teardown
```

## Runner

```js
const runner = Runner.create()
Runner.run(runner, engine)
Runner.stop(runner)          // teardown
```

## Bodies

```js
Bodies.rectangle(x, y, width, height, options)
Bodies.circle(x, y, radius, options)
Bodies.polygon(x, y, sides, radius, options)
Bodies.trapezoid(x, y, width, height, slope, options)
Bodies.fromVertices(x, y, vertexSets, options) // custom shapes
```

### Body options

| Option | Default | Meaning |
| --- | --- | --- |
| `isStatic` | `false` | Immovable (walls, ground) |
| `isSensor` | `false` | Detect collisions without physical response |
| `restitution` | `0` | Bounciness 0..1 |
| `friction` | `0.1` | Surface friction |
| `frictionStatic` | `0.5` | Static friction |
| `frictionAir` | `0.01` | Air drag |
| `density` | `0.001` | Mass per area |
| `angle` | `0` | Initial rotation (radians) |
| `render.fillStyle` | — | Fill color (filled render) |
| `render.strokeStyle` / `render.lineWidth` | — | Outline |
| `collisionFilter` | — | `{ group, category, mask }` for selective collisions |

## Body operations

```js
Body.setPosition(body, { x, y })
Body.setVelocity(body, { x, y })
Body.setAngle(body, radians)
Body.setAngularVelocity(body, v)
Body.applyForce(body, body.position, { x: 0, y: -0.05 })
Body.scale(body, sx, sy)
```

## Composite (the world)

```js
Composite.add(engine.world, [bodyA, bodyB, constraint])
Composite.remove(engine.world, body)
Composite.clear(engine.world, keepStatic /* bool */)
Composite.allBodies(engine.world)
```

## Constraint

```js
Constraint.create({
  bodyA, bodyB,              // or pointA/pointB for fixed anchors
  pointA: { x: 0, y: 0 },    // local offset on bodyA (or world point if no bodyA)
  pointB: { x: 0, y: 0 },
  length: 100,
  stiffness: 0.9,            // 1 = rigid, lower = springy
  damping: 0.1,
})
```

## Mouse & dragging

```js
const mouse = Mouse.create(render.canvas)
const mouseConstraint = MouseConstraint.create(engine, {
  mouse,
  constraint: { stiffness: 0.2, render: { visible: false } },
})
Composite.add(engine.world, mouseConstraint)
render.mouse = mouse
```

## Events

| Target | Events |
| --- | --- |
| `engine` | `beforeUpdate`, `afterUpdate`, `collisionStart`, `collisionActive`, `collisionEnd` |
| `runner` | `beforeTick`, `tick`, `afterTick` |
| `render` | `beforeRender`, `afterRender` |
| `mouseConstraint` | `mousedown`, `mouseup`, `startdrag`, `enddrag` |

```js
Events.on(engine, 'collisionStart', ({ pairs }) => {
  for (const { bodyA, bodyB } of pairs) { /* ... */ }
})
```

## Composites helpers

```js
const stack = Composites.stack(x, y, cols, rows, colGap, rowGap, (px, py) =>
  Bodies.circle(px, py, 20))
Composites.chain(stack, 0.5, 0, -0.5, 0, { stiffness: 0.8 })
const cradle = Composites.newtonsCradle(x, y, number, size, length)
```

## Teardown (SPA / React)

```js
Render.stop(render)
Runner.stop(runner)
Render.world(render) // flush
Composite.clear(engine.world, false)
Engine.clear(engine)
render.canvas.remove()
render.textures = {}
```

## DOM sync (headless)

Create the engine with no `Render`, run with `Runner`, and in `afterUpdate`
write each body's `position` and `angle` to a DOM element's `transform`. Cache
element sizes outside the loop to avoid reflow.
