# MediaPipe Hands 0.4.1675469240

Local runtime, WASM and model files from `@mediapipe/hands@0.4.1675469240`, the same pinned release used by the previous Monster AI Lab game. Upstream: https://www.npmjs.com/package/@mediapipe/hands/v/0.4.1675469240 . License: ../../licenses/MediaPipe-LICENSE.txt (Apache-2.0).

Keep all files together. `tools/generate.py` copies them into each independent GDevelop project. JavaScript sidecars use JavaScript resources; binary sidecars use resources with `disablePreload: true`, so the GDevelop JSON manager does not parse them. MediaPipe loads and decodes those files through the adapter's resource lookup. All inference stays in the browser.

`teacher/bridge.js` contains the readable fist/palm/two-finger rules and the command latch. This is the default play mode. Teachable Machine is an optional, collapsed classroom setting.
