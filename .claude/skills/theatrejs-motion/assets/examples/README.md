# Theatre.js Design Gallery

Ready-made motion designs you can scaffold and author in Studio. Each is a
distinct, self-contained "design" driven by `onValuesChange`. Generate any of
them with the skill's `init_project.py`:

```bash
# from the skill root
./scripts/init_project.py --preset hero    --output src/hero.js
./scripts/init_project.py --preset loader  --output src/loader.js
./scripts/init_project.py --preset stagger --output src/stagger.js
./scripts/init_project.py --preset scroll  --output src/scroll.js
./scripts/init_project.py --preset r3f     --output src/App.jsx
./scripts/init_project.py --preset vanilla --output src/main.js
```

| Preset | Design | Best for |
| --- | --- | --- |
| `hero` | Headline + subtitle rise, fade, and de-blur, staggered | Landing page intros |
| `loader` | Progress ring sweeps and spins while a label pulses, looping | Loading / splash states |
| `stagger` | List/grid items cascade in, one after another | Galleries, feature grids, menus |
| `scroll` | Scroll position scrubs the sequence | Scroll storytelling |
| `r3f` | Editable R3F mesh + camera on a timeline | 3D product/hero scenes |
| `vanilla` | Single element transform/opacity | Smallest starting point |

## Authoring flow (same for every design)

1. Add the matching markup (each generated file names the elements it expects in
   a comment at the top).
2. Run `npm run dev` — Studio mounts in the corner.
3. Keyframe the props on the timeline. For `hero` and `stagger`, offset each
   object's keyframes to create the cascade.
4. Export the project state to `state.json` and ship with `@theatre/core` only.

## Fully worked example

`hero/` contains a complete, runnable version of the `hero` design (markup, CSS,
and the Theatre.js code) so the expected DOM structure and styling are clear.
Use it as a reference when wiring any of the other presets.

See the skill's `references/troubleshooting.md` for the Theatre.js-vs-GSAP
decision guide and common fixes.
