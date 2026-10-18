# Teddy Interactive — agent notes

Deployed October 18, 2026. Authoring branch `codex/teddy-gpio-controls`, slot B / API 49914. Use the single Halloween show root; this folder is not a standalone show.

## Controls

- White, P1-11 / GPIO17: arms up; retained pull-down wiring, rising edge.
- Green, P1-13 / GPIO27: arms down; pull-up, falling edge.
- Blue, P1-15 / GPIO22: look left and return to center; pull-up, falling edge.
- Yellow, P1-18 / GPIO24: look right and return to center; pull-up, falling edge.
- Red, P1-16 / GPIO23: raised eyebrows and open eyes plus `dry-fart.mp3` once; pull-up, falling edge.
- Debounce both edges at 100 ms. Re-enable after 1100 ms, or 2200 ms for Red. Unnamed P1-10 legacy wing input is disabled. Previously disabled P1-23/24 are preserved.

## Playback and isolation

FPPWINGS2 `192.168.0.133` is the button/audio controller. The detached Python worker launches through `teddy_controls.sh`, and a `FPPD_STARTED` preset restores it after startup. It remembers arm position in `config/teddy-runtime.json`; subsequent glances and eyebrow reactions use matching arms-up/down clips. Repeat arm commands hold the existing pose without jumping. Only one short reaction plays at a time; a newer press can replace the queued press while a reaction finishes.

FPP-Selfie-Station `192.168.0.213` plays the ten native compressed model effect sequences. Every ESEQ contains only Teddy's 1500 channels, zero-based sparse range 214642–216141 (user-facing start 214643). The pumpkin on the next port is excluded. Existing controller routing, RGB order, 20% brightness and physical wiring are preserved.

The worker reads Master status but never sends commands to Master. During a song, a button reaction briefly takes over Teddy, then yields to the song. When Master is idle, Teddy holds the selected arm pose with normal blinking. Idle poses are removed when the show begins, without stopping or restarting Master. Failures to read Master conservatively suppress the idle pose.

## Native authoring

`Tools/build_teddy_controls.py` uses xLights `newSequence`, `addEffect`, `saveSequence`, and `exportModelWithRender`; no effect databases or rendered frames were authored by hand. Faces definition is `Teddy `, including the trailing space. Costume is `Teddy RedBow`, with the vendor arm masks, eye-direction states, and Brows/highbrows layered above it. Preserve Teddy's forced brown mouth and blue eyes.

Native clips use 25 ms frames and `eseqcompressed` export; uncompressed ESEQ requires 50 ms and prompts a blocking error. `newSequence` requires whole-second durations; fractional durations truncate to zero and open the wizard. Launch with `-q -b -s <checkout>/Halloween` to suppress the command-line notice. On relaunch, keep the layout XML newer than the task's identical autosave to avoid a recovery prompt.

## Validation

- All ten native exports decoded: exactly 500 pixels, 25 ms, correct sparse offset, nonblack frames.
- Glances change only the expected four eye nodes and return to center. Surprise changes only the existing eyebrow nodes. Arm states differ as expected.
- Native model video was visually inspected.
- Live FPP script-command tests verified up, left, right, Red, down, and Red again; glances preserve arms-up, and each Red event increases the sound-play count by exactly one. FPP logs confirm the sound decoded and its audio stream opened.
- All five GPIO lines are claimed by `FPPD-GPIO Input`, both edges, with the intended pull resistor, verified using read-only `gpioinfo`.
- Repeated Down uses a held down pose, avoiding an unwanted up/down flash; after a reaction, the active main show regains Teddy.
- Master stayed running and the Selfie Station pixel configuration read back unchanged.
- Physical button presses and audible sound at the station still need the user's observation. The GPIO GET route in this build exposes manually set output values, not monitored input levels; do not SET an input to test it.

## Rebuild/deploy

Open this checkout's Halloween show in the intended xLights instance, then set `XLIGHTS_API_PORT` and run `Tools/build_teddy_controls.py`. Run `Tools/deploy_teddy_controls.py` to upload effects/scripts, set the five mappings and the startup preset, and restart only the button Pi's service. Deployment preserves unrelated GPIO entries and presets, and refuses to overwrite another user's FPPD_STARTED command. Run `Tools/verify_teddy_controls.py` for live command-path checks; it deliberately reports physical presses/audibility as unverified.

Rendered FSEQ/ESEQ files follow the repository's ignore rules. The source XSQs, builder, runtime/deployment scripts, manifest and verification records are retained here. Generated ESEQ files are installed on the Selfie Station and kept in the local Effects folder.
