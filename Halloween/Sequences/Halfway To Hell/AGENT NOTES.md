## Garage layout batch render — October 18, 2026

- Re-rendered from the canonical shared Halloween layout after restoring the garage line to outline, all-pixel and vertical groups. Native checks found no missing models, unexpected zero-node effects, impossible overlaps or effects beyond the end; authored effects and frame timing remain unchanged.
- All 73 Garage Left Bottom pixels and all 30 Wall - Garage Top pixels light in one-second samples at their new porch Genius port 8 addresses. Tune To output is lit. Full batch evidence and recoverable previous renders: `Halloween/garage-batch-render-latest.json`.
- This batch is now deployed: Master and the projector have matching fresh sequences, with complete transfer checksums and matching frame counts/sequence IDs verified. Projector pixels match the rendered source. Required media verified on both players. Existing playlists, schedule and output routing preserved; Master stayed running. Evidence: `Halloween/garage-batch-upload-latest.json`.

## Shared Halloween show — October 18, 2026

- Shared-show deployment completed: fresh playback uploaded to Master and Projector, with full Master checksums and every Projector frame verified. Final controller addresses read back; existing playlist/schedule preserved; Master returned to idle.
- Reusable current import maps are the `* - Shared Halloween.xjmap` files in Tools. These point at the merged group/submodel names and omit removed or uninstalled targets. Original maps remain unchanged for historical recovery.
- Open xLights with `/Users/elliott.ohara/xlights/Halloween` as the show folder, then open this song’s XSQ. The song directory now organizes sequences and media; its separate layout/network configuration was retired. This section supersedes older standalone-show launch instructions below.
- Song-specific groups, submodels, face/state definitions and view were merged into the shared Halloween layout. Conflicting names were separated and all affected effect references updated. Timing, layer order, palettes, blending and render settings were verified against the backed-up sequence; native checks and a fresh render completed.
- Cleared obsolete rows for removed floods/flakes/bulbs and empty mapping groups where present, and trimmed effect tails beyond the song’s final frame. Hidden arches remain available by explicit user instruction. Native render-style recommendations are retained in the check report; purchased render styles were preserved.
- Reusable vendor packages/maps and media remain in this song folder. Earlier one-off layout/import scripts describe historical layouts: do not rerun them against the shared show without adapting their scope and aliases.
- Consolidation, mapping aliases, native checks, original layouts/XSQs/renders and deployment progress: `/Users/elliott.ohara/xlights/Halloween/single-show-consolidation-latest.json`; backup: `/Users/elliott.ohara/xlights/Halloween/Backups/Single Halloween show 20261018-141143`. User authorized the full show upload; consult progress for actual transfer completion.

# Halfway To Hell — Sequence Agent Notes

Working notes for `Halloween/Sequences/Halfway To Hell/Halfway To Hell.xsq`. Read alongside the root `AGENTS.md`.

## Media

- Sequence media: `Halloween/Sequences/Halfway To Hell/Media/` (lyric video / audio)
- Song images: `Halloween/Sequences/Halfway To Hell/Media/Images/`

## Timing

- Song timing templates: `Halloween/Sequences/Halfway To Hell/Timing Templates/`

## Tools

- Song scripts: `Halloween/Sequences/Halfway To Hell/Tools/`
- Shared API client: `Tools/xlights_api.py` (import via `sys.path` to the repo `Tools/` folder)

## Session / status

- Imported October 15, 2026 using native xLights Import Effects / Map Effects directly from the purchased `Final Halfway To Hell - EZ 2026.xsqz` package. Original retained under `Halloween/Source Packages/`.
- Saved reusable maps: `Tools/Vendor to Halloween.xjmap` and `Tools/Flood accents.xjmap`. 2,679 vendor effects imported, preserving their layers, colors, fades, timing tracks, and render styles.
- Similar roles: bats → flying bats; small spiders → physical spiders; large spiders → Reel Max pair; webs → MOAW pair; spinners → Starlords; large central prop → Rosa Grande; topper → Mini Grand Illusion; eerie tree → oak; pixel field → shrubs, roses, and Lantanas; arches → garden borders; matrix effects → window matrices and Projector. House thirds use actual left/center/right model positions.
- Individual moving-head dimmer pulses map to the eight floods (172 effects). Motor and shutter commands are omitted. RIP-letter effects are omitted because the physical tombs have no separate RIP lettering; tomb-body effects remain mapped. Eight source tomb positions compress onto the seven existing tombs.
- Vendor singing rows map to Clown (right/bow, including Preacher), Teddy (left/tooth), and Pumpkin (center), preserving the source's Main, Backing, and Preacher track choices and vocal blocks. Physical face definitions are adapted, with Teddy's exact `Teddy ` definition and safe accent outline.
- Source was 10 ms; final rendered output uses the show's 25 ms frame interval. Original-rate render is retained in the import backup. Verified 112 physical strand/prop outputs, three singing mouths, media availability, and visual preview.
- Controller assignments, wiring, master layout, and audio settings are unchanged. Working evidence and deployment result: `Halloween/Backups/Native mapped imports 20261015/`.
- Deployment verified October 15: FSEQ on FPP Master; matching audio on Master and Projector; appended after Something In The Way, preserving all prior playlist entries and the nightly schedule.

## Character continuity correction — October 15, 2026

- Disabled whole-character suppression on Teddy, Evil Clown, and Pumpkin. Characters stay visible between words and hold a resting mouth across assigned vocal-block gaps up to 10 seconds; longer breaks receive a 2.5-second exit and 1-second entrance. Outlines remain enabled consistently, including Preacher and backing sections.
- Kept every original vocal block and Main/Backing/Preacher assignment, original timing marks, character colors, eye expressions, and all non-face effects. Removed rapid boundary fades that caused short disappearances.
- Authored replacements through native addEffect after selective backed-up deletion; did not use setEffectSettings or alter layout, wiring, audio settings, or playlist.
- Rendered output checked every 25 ms: no unintended outline blackouts across 13,099 character-frames. Original sampled phonemes match exactly with no extra mouth pixels; exit brightness decreases gradually.
- Work branch: codex/halloween-face-continuity. Both permanent slots contained unrelated edits, so used a separate managed worktree and xLights B with render copies in Halloween/Backups/Face continuity 20261015/Sequences. Original files and verification evidence are retained in that backup folder.
- Corrected FSEQ uploaded and verified on FPP Master October 15 at 08:31 CDT under its existing filename. Playlist, nightly schedule, controller outputs, and Projector audio configuration verified unchanged. Local preview refreshed.


## Radio station sign — October 16, 2026

- Added a full-duration white “Tune to 87.9” Text effect through the native xLights API. Existing effects and timing outside Tune To verified unchanged.
- Authored in permanent slot B on codex/halloween-tune-to-879; original files and renders backed up in Halloween/Backups/Tune to 879 20261016.
- Rendered sign pixels inspected and corrected FSEQ uploaded to FPP Master under the existing playback filename. Playlist, schedule and controller routing preserved.

## Full-show deployment — October 17, 2026

Physical model routing/positions synchronized to the current Halloween master, preserving sequence-specific groups and submodels. Singing props excluded from decorative groups and direct non-Faces effects removed; lyric Faces and projector content preserved. Re-rendered and verified FSEQ uploaded under existing playback filename Halloween 2026 - Halfway To Hell.fseq. Controller output readbacks, FPP Master DDP routing (including Genius Roof), and Tune To range verified. Playlist and schedule retained. Recoverable local and remote backups: /Users/elliott.ohara/xlights/Halloween/Backups/Full render deployment 20261017-163501


## Occasional voting overlay — October 17, 2026

- Added one native Pictures effect on a new top layer of `Tune To`, 48.175–64.175 seconds. Transparent media leaves the existing matrix motion visible around the text bands.
- Invitation: Vote for songs; oharafamilylightshow.com/live. Tune To variants also keep a white Tune to 87.9 footer during the prompt.
- Original effects, settings, palettes, layer order and timing tracks verified unchanged. Physical layout and controller configuration unchanged.
- Website and voting catalog switched to Halloween on October 17, 2026. Rendered overlay uploaded to FPP Master under the existing playback filename; original FSEQ backed up remotely. Existing playback continues through the atomic file replacement.
- Backup: `/Users/elliott.ohara/xlights/Halloween/Sequences/Halfway To Hell/Backups/Voting overlay 20261017-195839`. Details: `Tools/voting-overlay-2026.json`. Shared tool: `Halloween/Tools/voting_overlays_2026.py`.


## Column Left wiring correction — October 18, 2026

- User corrected the physical location to Kulp 1601 (`FPP-KULP16-01`, 192.168.0.253), port 14. Port 16 remains Evil Clown. Column Left remains 66 pixels at 30% brightness. Falcon 1602 keeps its physical 16 x 500-pixel test configuration.
- User explicitly allowed channel repacking and re-rendering. Propagated xLights native routing changes from the master while preserving this song's groups, views, geometry and submodel definitions. Existing effects, palettes, layers and timing tracks verified unchanged.
- Re-rendered locally for the new channel ranges. Column Left output: 66 of 66 pixels light in half-second samples. Native allocation/evidence/backups: `Halloween/column-left-port14-native-latest.json`. Hardware and live FPP deployment are tracked separately; do not assume they completed from this render note.


## House Left porch wiring — October 18, 2026

- User confirmed House Left is after Window - Bottom Left on FPP-KULP08-FrontPorch (192.168.0.250), port 3: 134 window pixels followed by 86 House Left pixels, with House Left at 30% brightness. Native xLights allocation and exact chain verified.
- Propagated only routing fields from the master; song-specific groups, submodels, effects, palettes, layers and timing tracks are preserved. Re-rendered for the new addresses. Hardware/live deployment is recorded separately in Halloween/house-left-porch-port3-latest.json. Falcon 1602 test strings are preserved.

- House Left controller outputs are now uploaded and verified for physical testing: porch Kulp port 3 is Window - Bottom Left (134 pixels) then House Left (86 pixels, 30%). The affected Kulp services restarted successfully; Falcon 1602 test settings are unchanged. User explicitly deferred further sequence transfers until physical testing is complete. The earlier deployment was interrupted partway through; consult Halloween/house-left-porch-port3-latest.json and its per-file progress before resuming. Master playback service remains intentionally stopped. Do not upload I Knew It I Knew You without its separate approval.


## Eleventh Lantana — October 18, 2026

- Local layout corrected to 11 x 60-pixel lantanas: porch Kulp port 1 = 01–08; port 2 = 09–11. New Lantana 11 matches Lantana 07 with 20 leading nulls. Native routing propagated; custom geometry/groups and sequence effects preserved. Existing renders now require re-rendering before deployment. No hardware or playback uploads performed. See Halloween/lantana-eleven-layout-latest.json.


## All floods removed — October 18, 2026

- User confirmed there are no physical floods. Removed all eight flood models, their empty groups/views, and flood-only sequence rows. Non-flood model definitions and effect rows are preserved. Native routing recalculated; existing renders/output references are stale. No sequence rendering or transfers: user is still correcting/testing the layout. See Halloween/remove-all-floods-latest.json for backups and hardware status.


## Hidden flakes and bulbs disconnected — October 18, 2026

- User kept the arches but removed the four hidden GE Flake N/A props and Singing Bulb Left/Right from the oak-tree Kulp. Live ports 9/10/19/20 cleared and read back; other physical outputs and arches unchanged. The six inactive models now have No Controller and no port assignment. Definitions, groups, song-specific models and sequence effects remain preserved. Native layout allocation was recalculated; older output-address plans/renders are stale. No sequences rendered or sent. Evidence: Halloween/disconnect-hidden-flakes-bulbs-latest.json.


## Website and radio promotion — October 18, 2026

- Tune To now carries `oharafamilylightshow.com` and `TUNE TO 87.9 FM` throughout the sequence, using readable opaque text bands over the retained sign visuals. Superseded radio-only Text effects were removed.
- Projector website QR cards hold still for 15 seconds at 10–25, 70–85, 130–145 seconds. The QR points to `https://oharafamilylightshow.com/`; song visuals resume between cards.
- Native rendering and original-effect preservation checks passed. Actual sign pixels and every QR interval were checked; a QR extracted from this render decoded to the correct URL.
- Deployed to Master and Projector under the existing playback filenames with complete remote checksum and sequence metadata checks. Master kept running; playlists, schedule, routing and AV settings were preserved.
- Evidence and recoverable originals: `Halloween/website-promotion-latest.json`, `/Users/elliott.ohara/xlights/Halloween/Backups/Website promotion 20261018-201813`.
