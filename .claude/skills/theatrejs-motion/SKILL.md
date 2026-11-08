---
name: theatrejs-motion
description: Design and sequence motion on the web with Theatre.js - a JavaScript animation library with a professional visual Studio editor. Use when building keyframed animations, cinematic sequences, scroll-driven motion, or when sequencing Three.js and React Three Fiber scenes with an on-canvas timeline editor. Triggers on tasks involving Theatre.js, @theatre/core, @theatre/studio, @theatre/r3f, sheets, sheet objects, sequences, keyframes, visual animation editing, editable 3D cameras/meshes, or persisting animation state as JSON. Alternative to hand-coding GSAP timelines when a visual, keyframe-based workflow and reusable animation state are preferred.
---

# Theatre.js Motion

## Overview

Theatre.js is a JavaScript animation library paired with a professional visual editor (Studio). Define animatable properties in code, then keyframe and sequence them on a timeline directly in the browser. The resulting animation is saved as serializable JSON state and replayed in production without the editor.

**When to Use This Skill**:
- Building keyframed, cinematic, or timeline-based animations with a visual editor
- Sequencing Three.js / React Three Fiber scenes (cameras, meshes, lights) on a timeline
- Scroll-driven storytelling where scroll position maps to a sequence position
- Animating any value: DOM styles, SVG, canvas, audio params, shader uniforms
- Collaborative motion design where designers tweak timing without touching code
- When reusable, persistable animation state (JSON) is preferred over imperative tweens

**Key Benefits**:
- **Visual editor**: Keyframe on a real timeline, scrub, and fine-tune easing by hand
- **Code + data split**: Logic in code, timing/keyframes in portable JSON state
- **Framework-agnostic core**: Drive anything via `onValuesChange`
- **First-class R3F**: Make any R3F element `editable`, sequence cameras and transforms
- **Production-safe**: Ship `@theatre/core` only; Studio is a dev-only dependency

---

## Core Concepts

### 1. Project, Sheet, and Sheet Object

The hierarchy is **Project → Sheet → Sheet Object**. A project groups sheets; a sheet is a self-contained set of animations; a sheet object exposes animatable props.

```js
import { getProject, types } from '@theatre/core'
import studio from '@theatre/studio'

// Studio is dev-only — guard it out of production bundles
if (process.env.NODE_ENV !== 'production') studio.initialize()

const project = getProject('My Project')
const sheet = project.sheet('Intro')

// A sheet object with typed, animatable props
const obj = sheet.object('Logo', {
  x: 0,
  y: 0,
  opacity: types.number(1, { range: [0, 1] }),
  rotation: types.number(0, { range: [-180, 180], nudgeMultiplier: 1 }),
})

// React to every value change — this is where animation is applied
obj.onValuesChange((values) => {
  logoEl.style.transform = `translate(${values.x}px, ${values.y}px) rotate(${values.rotation}deg)`
  logoEl.style.opacity = values.opacity
})
```

### 2. Prop Types

Props define what can be animated and how the editor renders them.

```js
import { types } from '@theatre/core'

sheet.object('Panel', {
  // Numbers with range + nudge sensitivity
  width: types.number(200, { range: [0, 1000], nudgeMultiplier: 5 }),
  // Booleans
  visible: types.boolean(true),
  // Free strings
  label: types.string('Hello'),
  // Enumerated choices
  mode: types.stringLiteral('a', { a: 'Mode A', b: 'Mode B' }),
  // Colors (rgba, each channel 0–1)
  color: types.rgba({ r: 1, g: 0, b: 0.2, a: 1 }),
  // Nested/compound props for grouping
  position: types.compound({ x: 0, y: 0, z: 0 }),
})
```

### 3. Sequences

Each sheet has a `sequence` — the timeline. Play it, scrub it, or bind its position to scroll.

```js
// Play with options
sheet.sequence.play({
  iterationCount: Infinity,  // loop forever
  range: [0, 3],             // play seconds 0–3
  rate: 1,                   // 1 = normal speed, 2 = 2x, -1 = reverse
  direction: 'normal',       // 'normal' | 'reverse' | 'alternate' | 'alternateReverse'
})

// play() returns a Promise that resolves true if it finished, false if interrupted
await sheet.sequence.play({ range: [0, 2] })

// Manual control — set position directly (great for scroll)
sheet.sequence.position = 1.5
```

### 4. State Persistence

Animation created in Studio is stored as JSON. Export it from Studio, then ship it so production replays without the editor.

```js
// Load exported state (state.json) and wait until values are applied
import projectState from './state.json'
const project = getProject('My Project', { state: projectState })

await project.ready // ensures initial values are set before first frame
sheet.sequence.play()
```

---

## Common Patterns

### Pattern 1: Animate DOM elements

```js
import { getProject, types } from '@theatre/core'
import studio from '@theatre/studio'

if (import.meta.env.DEV) studio.initialize()

const sheet = getProject('Landing').sheet('Hero')
const title = document.querySelector('.hero-title')

const titleObj = sheet.object('Title', {
  y: types.number(40, { range: [-200, 200] }),
  opacity: types.number(0, { range: [0, 1] }),
})

titleObj.onValuesChange(({ y, opacity }) => {
  title.style.transform = `translateY(${y}px)`
  title.style.opacity = opacity
})

sheet.sequence.play({ range: [0, 1.2] })
```

### Pattern 2: Scroll-driven sequence

Map scroll progress (0–1) onto the sequence length. Keeps motion in sync with the scrollbar.

```js
const sheet = getProject('Story').sheet('Scene')
// ...define objects + onValuesChange...

const seqLength = 5 // seconds, must match the sequence's authored length

function onScroll() {
  const max = document.documentElement.scrollHeight - window.innerHeight
  const progress = max > 0 ? window.scrollY / max : 0
  sheet.sequence.position = progress * seqLength
}

window.addEventListener('scroll', onScroll, { passive: true })
onScroll()
```

### Pattern 3: React Three Fiber integration

Use `@theatre/r3f` to make any element `editable` (aliased `e`) and sequence it with the on-canvas editor.

```jsx
import { Canvas } from '@react-three/fiber'
import { getProject } from '@theatre/core'
import { SheetProvider, editable as e, PerspectiveCamera } from '@theatre/r3f'
import studio from '@theatre/studio'
import extension from '@theatre/r3f/dist/extension'

if (import.meta.env.DEV) {
  studio.initialize()
  studio.extend(extension) // adds the R3F snapshot/editor panel
}

const sheet = getProject('R3F Demo').sheet('Scene')

export default function App() {
  return (
    <Canvas>
      <SheetProvider sheet={sheet}>
        <PerspectiveCamera theatreKey="Camera" makeDefault position={[0, 0, 6]} />
        <ambientLight intensity={0.6} />
        <e.mesh theatreKey="Cube">
          <boxGeometry />
          <meshStandardMaterial color="hotpink" />
        </e.mesh>
      </SheetProvider>
    </Canvas>
  )
}
```

Trigger playback from a React effect:

```jsx
import { useEffect } from 'react'
useEffect(() => {
  sheet.sequence.play({ iterationCount: Infinity, range: [0, 4] })
}, [])
```

### Pattern 4: Drive shader uniforms or audio params

Because animation flows through `onValuesChange`, Theatre.js drives anything numeric.

```js
const fx = sheet.object('FX', {
  intensity: types.number(0, { range: [0, 1] }),
  frequency: types.number(220, { range: [20, 2000] }),
})

fx.onValuesChange(({ intensity, frequency }) => {
  material.uniforms.uIntensity.value = intensity
  oscillator.frequency.value = frequency
})
```

### Pattern 5: Pointer-reactive object outside the sequence

Set a prop imperatively (e.g., follow the cursor) using Studio's transaction API in dev, or a secondary non-sequenced sheet in production.

```js
// In production, read-only playback is typical; for interactivity drive a
// separate object whose values you set from input rather than the timeline.
const pointer = sheet.object('Pointer', { x: 0, y: 0 })
window.addEventListener('pointermove', (e) => {
  // onValuesChange still fires; apply to taste
  target.style.setProperty('--px', e.clientX)
})
```

### Pattern 6: Scroll-driven R3F camera (scroll scrubs the 3D sequence)

The most common real-world setup: author a camera/mesh sequence in Studio, then
let scroll position scrub it instead of `play()`. Combine `@theatre/r3f` with the
scroll-to-position mapping.

```jsx
import { Canvas, useThree } from '@react-three/fiber'
import { useEffect } from 'react'
import { getProject } from '@theatre/core'
import { SheetProvider, editable as e, PerspectiveCamera } from '@theatre/r3f'
import studio from '@theatre/studio'
import extension from '@theatre/r3f/dist/extension'
import projectState from './state.json' // exported from Studio

if (import.meta.env?.DEV) {
  studio.initialize()
  studio.extend(extension)
}

// In production, load authored state; in dev, omit state to author fresh
const project = getProject('Scroll Scene', import.meta.env?.DEV ? undefined : { state: projectState })
const sheet = project.sheet('Scene')
const SEQ_LENGTH = 6 // authored length in seconds

function ScrollRig() {
  useEffect(() => {
    let raf = 0
    const onScroll = () => {
      cancelAnimationFrame(raf)
      raf = requestAnimationFrame(() => {
        const max = document.documentElement.scrollHeight - window.innerHeight
        const progress = max > 0 ? window.scrollY / max : 0
        sheet.sequence.position = progress * SEQ_LENGTH
      })
    }
    window.addEventListener('scroll', onScroll, { passive: true })
    onScroll()
    return () => window.removeEventListener('scroll', onScroll)
  }, [])
  return null
}

export default function App() {
  return (
    <Canvas frameloop="demand">
      <SheetProvider sheet={sheet}>
        <PerspectiveCamera theatreKey="Camera" makeDefault position={[0, 0, 8]} />
        <ambientLight intensity={0.6} />
        <e.mesh theatreKey="Hero">
          <torusKnotGeometry args={[1, 0.3, 128, 32]} />
          <meshStandardMaterial color="hotpink" />
        </e.mesh>
        <ScrollRig />
      </SheetProvider>
    </Canvas>
  )
}
```

Note: with `frameloop="demand"`, request a render whenever the sequence position
changes (R3F's `invalidate()`), or keep the default loop while scrubbing.

### Pattern 7: Audio-synced sequence

Lock a sequence to an audio source so visuals stay in time with sound.

```js
const sheet = getProject('Music Video').sheet('Scene')

// attachAudio resolves once the audio is decoded and ready
await sheet.sequence.attachAudio({ source: '/track.mp3' })

// Now play() is synced to the audio clock
sheet.sequence.play({ range: [0, 30] })
```

---

## TypeScript

Prop types are inferred, and sheet objects expose typed `value` and
`onValuesChange` payloads. Import `ISheetObject` for explicit typing.

```ts
import { getProject, types, type ISheetObject } from '@theatre/core'

const props = {
  x: types.number(0, { range: [-100, 100] }),
  opacity: types.number(1, { range: [0, 1] }),
  label: types.string('Hello'),
}

const sheet = getProject('App').sheet('Main')
const obj: ISheetObject<typeof props> = sheet.object('Box', props)

// values is fully typed: { x: number; opacity: number; label: string }
obj.onValuesChange((values) => {
  const { x, opacity } = values
  // ...
})
```

For `@theatre/r3f`, `editable` elements accept the underlying Three.js element
props plus `theatreKey: string`, so JSX stays type-checked.

## Production Workflow

The dev editor and the shipped runtime are two phases:

1. **Author (dev)**: `studio.initialize()` mounts the editor. Keyframe on the
   timeline, scrub, and tune easing.
2. **Export**: From the Studio UI export the project, or
   `studio.createContentOfSaveFile('Project Name')` → save as `state.json`.
3. **Ship (prod)**: Load the state and never initialize Studio.

```js
import { getProject } from '@theatre/core'
import state from './state.json'

const project = getProject('Project Name', { state })
await project.ready           // apply initial values before first frame
project.sheet('Scene').sequence.play()
```

Keep `@theatre/studio` in `devDependencies` and guard every `studio.*` call
behind a dev check so bundlers tree-shake it out of production.

---

## Integration Patterns

- **Three.js (vanilla)**: Drive `camera.position`, `mesh.rotation`, and material props from `onValuesChange` inside the render loop. See `threejs-webgl` skill for scene setup.
- **React Three Fiber**: Use `@theatre/r3f` `SheetProvider` + `editable`. Pairs with the `react-three-fiber` skill.
- **GSAP / ScrollTrigger**: Use ScrollTrigger to compute scroll progress, then set `sheet.sequence.position`. Theatre.js owns the keyframes; ScrollTrigger owns the scroll math. See `gsap-scrolltrigger`.
- **Smooth scroll (Lenis/Locomotive)**: Feed the smoothed scroll value into `sequence.position` for buttery scroll-synced motion. See `locomotive-scroll`.
- **Framer Motion**: Keep Theatre.js for cinematic/3D sequences; Framer Motion for component-level UI gestures. See `motion-framer`.

---

## Performance Optimization

- **Exclude Studio from production**: Only `@theatre/core` ships. Guard `studio.initialize()` and `studio.extend()` behind a dev check (`import.meta.env.DEV` / `NODE_ENV`).
- **Await `project.ready`** before the first render to avoid a one-frame flash of default values.
- **Throttle scroll → position** with `requestAnimationFrame`; set `sequence.position` once per frame, not per scroll event.
- **Prefer `demand` frameloop in R3F** when motion is scroll-driven, so the canvas only renders when the sequence position changes.
- **Keep sheet objects lean**: fewer animated props = fewer `onValuesChange` payloads. Group related values with `types.compound`.
- **Reuse one project**: `getProject` is memoized by name; call it once and share the instance.

---

## Common Pitfalls

- **Shipping Studio to production**: Bloats the bundle and shows the editor UI. Always tree-shake/guard it out.
- **Forgetting `project.ready`**: Values from loaded `state.json` apply asynchronously; render before it resolves and the first frame shows defaults.
- **Mismatched sequence length**: Scroll mapping needs the authored length in seconds; hardcoding the wrong value desyncs scroll from motion.
- **Mutating props outside the sequence expecting keyframes**: `onValuesChange` reflects current values; authoring keyframes happens in Studio (or via the state JSON), not by assigning to `values`.
- **Duplicate project names**: Two `getProject('Same')` calls return the same instance; unique names avoid state collisions.
- **`theatreKey` not unique**: In R3F, each `editable`/camera needs a unique `theatreKey` or edits collide.

---

## Resources

**Scripts** (`scripts/`):
- `init_project.py` — Scaffold a motion design from a preset: `vanilla`, `r3f`, `scroll`, `hero` (intro reveal), `loader` (looping ring), `stagger` (cascading list/grid)
- `generate_sheet_object.py` — Generate a typed sheet object + `onValuesChange` handler from a prop spec
- `check_production_ready.py` — Scan source for common footguns (unguarded Studio, missing `project.ready`, Studio in dependencies)

**References** (`references/`):
- `api_reference.md` — Full API: core, types, sequence, studio, and `@theatre/r3f`
- `troubleshooting.md` — Common errors, fixes, and a Theatre.js-vs-GSAP decision guide

**Assets** (`assets/`):
- `starter_theatre/` — Minimal Vite starter wired for Theatre.js core + Studio
- `examples/` — Design gallery (hero intro, loader, stagger, scroll, R3F) with a fully worked `hero/` example (HTML + CSS + JS)

**Official**:
- Docs: https://www.theatrejs.com/docs/latest
- Getting started: https://www.theatrejs.com/docs/latest/getting-started
- API: https://www.theatrejs.com/docs/latest/api/core

## Related Skills

- `threejs-webgl` — Scene, camera, and material setup to animate
- `react-three-fiber` — Declarative R3F scenes; pairs with `@theatre/r3f`
- `gsap-scrolltrigger` — Compute scroll progress to drive `sequence.position`
- `locomotive-scroll` — Smooth scroll values for scroll-synced sequences
- `motion-framer` — Component-level UI gestures alongside cinematic sequences
