# Licenses and source

The browser application and generated educational project are distributed under
AGPL-3.0-or-later; see LICENSE. Original monster drawings and backgrounds are
included in the editable Scratch project under the same license.

| Component | Version | License | Upstream source |
|---|---|---|---|
| Scratch VM | 5.0.300 | AGPL-3.0 | https://github.com/scratchfoundation/scratch-vm |
| Scratch Render | 2.2.84 | AGPL-3.0 | https://github.com/scratchfoundation/scratch-render |
| Scratch Storage | 6.2.1 | AGPL-3.0 | https://github.com/scratchfoundation/scratch-storage |
| MediaPipe Hands + bundled models/WASM | 0.4.1675469240 | Apache-2.0 | https://github.com/google-ai-edge/mediapipe |
| Playwright (development only) | 1.56.1 | Apache-2.0 | https://github.com/microsoft/playwright |

The exact npm dependency tree and integrity hashes are in package-lock.json.
The unmodified upstream bundles retain their copyright/license headers.
Additional package license/notice files are copied into `licenses/` by the
build. Generated binaries, WASM and model files come from the versioned
`@mediapipe/hands` npm package, not an unverified model mirror.

Complete source for this application, packaging tools, tests, instructions and
lockfile: https://github.com/olgaschev418-tech/my-first-project/tree/main/monster-ai-lab
To reconstruct the bundle: `npm ci` then `npm run build`, then
`python3 tools/package_classroom.py`. Python 3.10+ and Node.js 22+ are required
for reconstruction. Classroom users do not need npm.

Scratch and MediaPipe are trademarks of their respective owners. This project
is independent and is not endorsed by Scratch Foundation or Google.
