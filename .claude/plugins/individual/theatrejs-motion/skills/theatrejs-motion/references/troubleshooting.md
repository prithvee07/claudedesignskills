# Theatre.js Troubleshooting & Decision Guide

Common problems, their causes, and fixes — plus when to choose Theatre.js over
hand-coded animation.

## Common Errors

### Studio UI appears in production
**Cause**: `studio.initialize()` ran in the production build.
**Fix**: Guard every `studio.*` call behind a dev check and keep
`@theatre/studio` in `devDependencies`.
```js
if (import.meta.env?.DEV) studio.initialize()
```

### First frame flashes default values, then snaps to the animation
**Cause**: Loaded `state.json` is applied asynchronously; rendering started
before it was ready.
**Fix**: `await project.ready` (or `project.ready.then(...)`) before the first
render or first `play()`.

### Scroll motion is out of sync with the scrollbar
**Cause**: The `SEQ_LENGTH` used to map scroll progress doesn't match the
sequence's authored length.
**Fix**: Set `SEQ_LENGTH` to the real authored length in seconds. If the
animation ends early or late, the two values disagree.

### `play()` seems to do nothing
**Causes & fixes**:
- No keyframes authored for the range → add keyframes in Studio.
- `range` is `[0, 0]` or outside the authored span → widen the range.
- A later `play()`/`position` assignment overrode it → ensure only one driver
  (either `play()` or scroll-driven `position`), not both.

### Values jump when scrubbing with `sequence.position`
**Cause**: Mixing `play()` and manual `position` assignment fights for control.
**Fix**: Pick one model. For scroll, drive `position` only and never call
`play()` on the same sheet.

### R3F edits collide / wrong object moves
**Cause**: Two `editable`/camera elements share a `theatreKey`.
**Fix**: Give every `theatreKey` a unique, stable string.

### `getProject('X')` returns stale or shared state
**Cause**: `getProject` is memoized by name; the same name returns the same
instance.
**Fix**: Use unique project names; call `getProject` once and share the handle.

### `@theatre/r3f` extension panel missing in Studio
**Cause**: `studio.extend(extension)` not called, or imported from the wrong
path.
**Fix**: Import the extension and extend Studio in dev:
```js
import extension from '@theatre/r3f/dist/extension'
studio.extend(extension)
```

### Bundle is unexpectedly large
**Cause**: `@theatre/studio` got bundled into production.
**Fix**: Confirm it's a dev dependency and that the dev guard is statically
analyzable (`import.meta.env.DEV` / `process.env.NODE_ENV`), so it tree-shakes.

## Performance Checklist

- One driver per sequence (play OR position).
- Throttle scroll→position with `requestAnimationFrame`.
- Prefer R3F `frameloop="demand"` for scroll-driven scenes; invalidate on change.
- Group related props with `types.compound` to shrink `onValuesChange` payloads.
- `await project.ready` before the first frame.

## Decision Guide: Theatre.js vs GSAP vs Framer Motion

| Need | Best fit |
| --- | --- |
| Visual, keyframe timeline a designer can tune | **Theatre.js** |
| Sequencing Three.js / R3F cameras and transforms | **Theatre.js** (`@theatre/r3f`) |
| Reusable, portable animation state as JSON | **Theatre.js** |
| Imperative, code-first tweens and scroll triggers | **GSAP / ScrollTrigger** |
| Component-level UI gestures, layout animations in React | **Framer Motion** |
| Fine-grained physics springs | **react-spring** |

They compose: use ScrollTrigger to compute scroll progress and feed it into
`sheet.sequence.position`, letting Theatre.js own the keyframes while GSAP owns
the scroll math.

## Where to Confirm Version-Specific Behavior

APIs evolve across `@theatre/*` releases. Verify current signatures at:
- https://www.theatrejs.com/docs/latest/api/core
- https://www.theatrejs.com/docs/latest/manual/Studio
