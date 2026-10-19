# Teddy Interactive — agent notes

## Talking speech integration — October 18, 2026

Authored on `codex/teddy-speech-integration`, slot B / port 49914. Speech uses the existing split setup: pixel/effect output on Selfie Station .213, Sound Blaster S3 audio and button inputs on .133. Preserve Player/DDP operation, the pumpkin, all GPIO assignments and Master playback. Website PRs #49 and #51 were reviewed, merged and deployed.

The button worker cooperates through Linux flock at `/home/fpp/media/tmp/teddy-interaction.lock`. It holds the lock through each five-second gesture and defers the latest button/idle pose while speech holds it. No commands go to Master. Native calibration uses 25ms frames and ten one-second mouth holds in rest, AI, E, etc, FV, L, MBP, O, U, WQ order, exported only for Teddy. The calibration, cooperating worker and dedicated speech service are deployed. Messages are enabled while the show and calibrated prop are online; physical speaker and perceptual lip-sync verification remain pending. The lock is owned by fpp:fpp with mode 0660, including when the worker runs as root.

## Five-second button routines — October 18, 2026

User requested clearly visible movement for every button, lasting five seconds, with its scarf matching the button color and a marquee for White. Authoring branch `codex/teddy-five-second-routines`, slot B / API 49914. Use the canonical Halloween show folder.

- White / P1-10 / GPIO15: both arms sweep down–middle–up–middle; moving white marquee on a dark gray scarf.
- Green / P1-13 / GPIO27: left arm wave; green scarf.
- Blue / P1-15 / GPIO22: right arm wave; blue scarf.
- Yellow / P1-18 / GPIO24: both arms flap between middle and up; yellow scarf.
- Red / P1-16 / GPIO23: arms alternate leaning left/right; red scarf, raised brows, and one fart sound.

All routines run for 5000 ms at 25 ms per frame. Poses change every 250 ms. These use the existing `arms` states and `Bow Tie` submodel; no layout or channel changes. Native xLights authoring uses newSequence/addEffect/saveSequence/exportModelWithRender, never setEffectSettings or handwritten rendered frames. Native compressed ESEQ exports include only Teddy's 1500 channels at sparse zero-based offset 214642.

The Pi at 192.168.0.133 accepts the five physical rising edges and invokes color-named actions. Debounce is 100 ms, both edges; re-enable after 5100 ms prevents one held/rapidly repeated button from piling up routines. The worker allows the current five-second animation to finish, then handles the latest queued button. Red still attempts the fart once.

The Selfie Station at 192.168.0.213 plays the clips. The worker changes only its explicit Teddy whitelist, leaving the pumpkin and physical output configuration untouched. It reads Master 192.168.0.19 status but never sends a command to Master. During the show it yields after five seconds; outside the show it returns to a neutral arms-down hold. FPPD_STARTED starts the worker after boot. The deploy helper pauses the worker and stops only its whitelisted effects before replacing files (a running hold keeps its file locked), skips identical uploads, waits for the local service after restart, and explicitly restarts the detached worker, which otherwise survives fppd re-exec with its previous Python code loaded.

## Sound and physical inputs

User explicitly selected the Sound Blaster Play! 3 USB adapter for audio. Saved AudioOutput is stable ALSA ID `S3`, MediaBackend=pipewire-simple, PipeWireSinkName=fpp_group_default. The native AudioOutput setting handler applied the new graph. USB hardware was verified RUNNING with advancing hardware pointers during a test fart; speakers remained inaudible to the user, who suspects cabling. Leave Sound Blaster routing selected; actual sound remains unconfirmed.

Physical input monitoring proved Red/Green/Blue/Yellow go low at rest and high on press. The previous falling-edge mapping was corrected. Installed FPP starts the delay on every rising edge, even when no rising command exists, suppressing a short press's falling action. White is physically wired to GPIO15 / P1-10, as established by an isolated White-only press test. The old GPIO17 / P1-11 assignment was wrong. GPIO15 had been disabled as an unnamed legacy trigger; it now runs White, with its original plain gpio input mode. GPIO17 is disabled. Multiple GPIO15 rising/falling pairs and no GPIO17 transitions were observed while the user pressed only White. Do not SET a pin to test it; read-only pinctrl get is safe.

## Validation and tools

Tools/build_teddy_controls.py authors all five routines plus the two neutral holds and exports native model MP4 previews. The library.json manifest defines the active deployment; old short gesture files are retained as historical sources and are no longer mapped to buttons.

Tools/verify_rendered_routines.py decodes native compressed outputs using libzstd, verifies 200 frames at 25 ms, exact sparse range, five distinct moving arm patterns, exact solid scarf colors, and moving neutral-color White marquee. Tools/verify_teddy_controls.py checks the real FPP script command path for all five, confirms each stays active beyond four seconds and finishes after five, preserves USB output, and leaves Master running and the physical pixel config unchanged. Physical illumination and sound require user observation.

Launch a slot with -q -b -s <checkout>/Halloween. newSequence durationSecs must be whole seconds. Use eseqcompressed for 25 ms; uncompressed eseq requires 50 ms and opens a blocking error. Keep an identical task-created autosave older than the layout to avoid a startup recovery prompt.

Final validation: all five rendered routines passed channel, color and moving-arm checks. All five deployed script actions remained visible in the running-effects API beyond four seconds and completed after five seconds, then returned to neutral. Red increased sound_count once. Five GPIO mappings and 5100 ms re-enable delays read back correctly. The deployed Python file matched the saved source byte-for-byte. Master remained running and Selfie Station pixel output settings matched the pre-deployment snapshot.

## White input correction — October 18, 2026

An all-input read-only monitor found White presses on GPIO15 (physical header pin 10), not GPIO17 (header pin 11). Moved the existing White action unchanged to P1-10, preserving the plain gpio mode originally used on that pin. Disabled the unused P1-11 mapping. Other buttons, five-second timing, Sound Blaster audio, and pixel outputs were unchanged. Restarted only the button Pi to load the new input; Master remained running. The user confirmed: “Yes, White works now.” The worker logged a physical White press and ran Teddy White Routine. All five pin mappings read back correctly and Master was still running.

### Effect timing under live DDP

Live verification found a native five-second effect ended near 3.9 seconds because the installed FPP advanced a frame for every compositor pass, including forced DDP updates. Installed a narrowly scoped monotonic-clock timing patch in Selfie Station .213 only; effects keep their authored timing, restart from frame zero, and paused background effects retain their position. Native compilation was staged and memory limited before activation. Restarted only Selfie Station; Master stayed playing and pixel/output config, routes, schedule and GPIO were unchanged. Original source, object and library are recoverable at `/home/fpp/media/backups/ofls-speech-timing-20261018/`. The patch is saved in `Tools/fpp-effect-clock.patch`. An FPP update may replace it; recheck actual effect duration before enabling speech after an update.

The final live cooperation check passed: a Green button queued while another process held the speech lock, began after release, remained active after four seconds and finished after five, then yielded to the ongoing show. No Red sound was triggered. `Tools/live-button-cooperation-final.json` records the result. Native calibration: 400 frames, 25ms, sparse start 214642, 1500 channels, ten distinct shapes, no nonmouth differences. Actual speaker sound and perceptual lip sync still require observation.

### Website speech deployment and test

The audio Pi runs Node 20.19.2 and the verified website bridge at source head `93a9ddcc5124361e227b70f7073903066a9fc99f` in `/opt/ofls-bridge`. Its independent `ofls-speech-bridge.service` is active and enabled as user fpp. Root-only `/etc/ofls-speech-bridge.env` selects speech role, pixels .213, audio localhost on .133, model `Elliott - EFL Teddy`, native `bear-calibration`, Kevin voice and the shared interaction lock. No frame-time override or guessed AV offset is set. The dedicated speech HMAC was delivered encrypted; transient plaintext upload was removed. Never print credentials or use the show bridge HMAC here.

Successful cloud apply: run 39187794284. Guarded activation: run 39188807507 required a fresh calibrated heartbeat before setting mode auto. On the live `/live/` page, message `c2c4a426-2530-4b38-82b8-f2037b35f6b9` generated a 7672ms Kevin MP3 and matching effect. Both exact files were observed playing together; the worker yielded with status speech, both outputs returned idle and the worker returned to show. The website receipt became spoken. Master stayed running and playing. This verifies delivery/playback, not physical speaker audibility or perceived alignment. Evidence: `Tools/website-speech-observation.json` and `Tools/speech-local-deployment.json`.

To close messages without affecting the show, run the website repository's `Talking prop control` workflow with mode off. To stop speech locally, stop only `ofls-speech-bridge.service` on .133; the existing button worker and Master remain independent. Preserve the native timing patch and run the live duration/loop checks after an FPP upgrade before reopening messages. The five-second button and lock regression tests are in Tools/test_worker_lock.py and Tools/test_worker_scheduler.py.
