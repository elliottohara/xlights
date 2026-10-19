## Garage layout batch render — October 18, 2026

- Re-rendered from the canonical shared Halloween layout after restoring the garage line to outline, all-pixel and vertical groups. Native checks found no missing models, unexpected zero-node effects, impossible overlaps or effects beyond the end; authored effects and frame timing remain unchanged.
- All 73 Garage Left Bottom pixels and all 30 Wall - Garage Top pixels light in one-second samples at their new porch Genius port 8 addresses. Tune To output is lit. Full batch evidence and recoverable previous renders: `Halloween/garage-batch-render-latest.json`.
- This batch is now deployed: Master and the projector have matching fresh sequences, with complete transfer checksums and matching frame counts/sequence IDs verified. Projector pixels match the rendered source. Required media verified on both players. Existing playlists, schedule and output routing preserved; Master stayed running. Evidence: `Halloween/garage-batch-upload-latest.json`.

## Shared Halloween show — October 18, 2026

- Shared-show deployment completed: fresh playback uploaded to Master and Projector, with full Master checksums and every Projector frame verified. Final controller addresses read back; existing playlist/schedule preserved; Master returned to idle.
- Open xLights with `/Users/elliott.ohara/xlights/Halloween` as the show folder, then open this song’s XSQ. The song directory now organizes sequences and media; its separate layout/network configuration was retired. This section supersedes older standalone-show launch instructions below.
- Song-specific groups, submodels, face/state definitions and view were merged into the shared Halloween layout. Conflicting names were separated and all affected effect references updated. Timing, layer order, palettes, blending and render settings were verified against the backed-up sequence; native checks and a fresh render completed.
- Cleared obsolete rows for removed floods/flakes/bulbs and empty mapping groups where present, and trimmed effect tails beyond the song’s final frame. Hidden arches remain available by explicit user instruction. Native render-style recommendations are retained in the check report; purchased render styles were preserved.
- Reusable vendor packages/maps and media remain in this song folder. Earlier one-off layout/import scripts describe historical layouts: do not rerun them against the shared show without adapting their scope and aliases.
- Consolidation, mapping aliases, native checks, original layouts/XSQs/renders and deployment progress: `/Users/elliott.ohara/xlights/Halloween/single-show-consolidation-latest.json`; backup: `/Users/elliott.ohara/xlights/Halloween/Backups/Single Halloween show 20261018-141143`. User authorized the full show upload; consult progress for actual transfer completion.

# The Dead Dance — Sequence Agent Notes

Working notes for `Halloween/Sequences/The Dead Dance/The Dead Dance.xsq`. Read alongside the root `AGENTS.md`.

## Media

- Sequence media: `Halloween/Sequences/The Dead Dance/Media/` (lyric video / audio)
- Song images: `Halloween/Sequences/The Dead Dance/Media/Images/`

## Timing

- Song timing templates: `Halloween/Sequences/The Dead Dance/Timing Templates/`

## Tools

- Song scripts: `Halloween/Sequences/The Dead Dance/Tools/`
- Shared API client: `Tools/xlights_api.py` (import via `sys.path` to the repo `Tools/` folder)

## Session / status

- Existing source sequence imported and prepared for the current Halloween layout.

## Halloween 2026 preparation

- Source: `/Volumes/Personal-Drive/xlights/Individual Sequences/The Dead Dance`
- Physical configuration copied from current Halloween master.
- Networks remain linked to the shared Halloween configuration.
- Original effects preserved: 6016.
- Unconnected source-reference models: GE Franken Monster (2), Robbie - Longhorn, Elliott - Star 1, Tree - Branches, Tree - Trunk, Mini Tree - 4 Star, Mini Tree - 2 Star, Mini Tree - 3 Star, Mini Tree - 1 Star, Mini Tree - 4, Mini Tree - 2, Mini Tree - 3, Mini Tree - 1, GE Priem Cube SM 1.

## Halloween 2026 deployment

- Prepared on October 13, 2026 using an isolated preparation worktree and xLights slot B.
- Canonical files are now in this Halloween sequence folder; source originals were retained.
- Controller ranges verified against the open canonical Halloween configuration before rendering.
- Retained source-only models are unconnected references, not physical outputs. Existing inactive-model check warnings remain.
- Rendered FSEQ v2: 9140 frames at 25 ms.
- Uploaded to FPP Master (192.168.0.19): `Halloween 2026 - The Dead Dance.fseq`.
- Uploaded media: `Halloween 2026 - The Dead Dance.mp3`.
- Enabled in Halloween 2026: loops nightly from sunset to a hard stop at 10:30 PM, America/Chicago.
- FPP Master routing now matches the Halloween ranges; Tune To panel output is enabled at channel 243680.
- Controller 192.168.0.249 was initially unreachable but responded successfully during final verification.

## Original vendor package recovery

- Archived original ZIP: `/Users/elliott.ohara/xlights/Halloween/Source Packages/xTreme Sequences/the-dead-dance-by-lady-gaga-dGhlLWRlYWQtZGFuY2UtYnktbGFkeS1.zip` (SHA-256 `bbcb8f1d4396186dbaa926b6cd08ca760e832a5c40a4dd205ec087cbca5dc6fc`).
- Restored 22 exact-name effect assets into `Media/Vendor/`; preserved choreography and current controller configuration.
- Pre-recovery sequence backup: `/Users/elliott.ohara/xlights/Halloween/Sequences/The Dead Dance/Backups/before-media-recovery-20261013-183037.xsq`.

## Controller configuration verification

- Verified October 13, 2026: all 11 active controllers, 87 pixel ports, and 144 model-setting boundaries match the canonical Halloween configuration.
- Corrected the Raised Bed Falcon 192.168.0.249 from its old show configuration using xLights controller upload.
- Master sends DDP One Based to Porch Falcon 192.168.0.247; all other active targets retain raw global channel numbering.
- Projector 192.168.0.201 has exactly one enabled 256x192 virtual matrix, starting at channel 1.
- Background effects on Projector, Left Yard and Tune To are stopped; the playlist lead-in stops all three at show start.
- Corrected the stale Tune To controller reference in the main layout; all controller ranges remain unchanged, so existing verified renders remain valid.
- The three Halloween-inactive controllers were preserved. The nightly sunset-to-10:30 PM schedule was preserved and playback resumed.
- Correction backups: `/Users/elliott.ohara/xlights/Halloween/Backups/Controller corrections 20261013-184721`.


## Center shrub mapping repair — October 13, 2026

- Isolated worktree: /Users/elliott.ohara/.codex/worktrees/halloween-shrub-repair/xlights; branch codex/halloween-center-shrub.
- Garage Left Bottom (73 pixels) and Wall - Garage Top (30 pixels) previously rendered onto the first 103 pixels of Shrub Center despite having no hardware output ports.
- Retained those legacy models as unconnected references outside all active controller channel ranges. xLights may automatically reassign their unused reference addresses.
- Redirected their group memberships to the full 261-pixel Shrub Center, deduplicating the shrub where already present. Physical shrub channels, port 6, pixel count, brightness and geometry are unchanged.
- Existing timing, effects and palettes preserved; static halloween direct wall effect retargeted to Shrub Center.
- Re-rendered and atomically deployed to FPP Master as `Halloween 2026 - The Dead Dance.fseq`; all 261 shrub pixels verified in sampled frames.
- Effect settings, palettes, timings and effect counts preserved. Playlist, schedule and controller output routing unchanged.
- Original layouts, sequence files and renders backed up under `/Users/elliott.ohara/xlights/Halloween/Backups/Center shrub correction 20261013`.

## Kulp01 port cleanup — October 14, 2026

- User requested deletion of the ten Robbie models assigned to FPP-KULP16-01 only; other Robbie-area models retained.
- GE Dark Helmet assigned to port 15 and its broken self-chain removed; GE Evil Clown assigned to port 16.
- Deleted model memberships removed from groups/views and their direct sequence elements removed. Remaining timing, palettes and effects preserved.
- Removed direct effects for deleted props: 0; remaining effects: 1363.
- Prepared in isolated worktree /Users/elliott.ohara/.codex/worktrees/halloween-kulp01-ports/xlights; branch codex/halloween-kulp01-ports; rendering session B.
- Original files backed up under /Users/elliott.ohara/xlights/Halloween/Backups/Kulp01 port cleanup 20261014.
- All 21 corrected renders verified and deployed to FPP Master; Kulp01, Falcon .252, Tune To and Master routing updated to the new channel ranges. Playlist/order and nightly sunset–22:30 schedule preserved.

## Remaining Robbie removal — October 14, 2026

- User requested removal of all remaining Robbie props, including source-only Longhorn, from the master and all 21 current Halloween song layouts. Empty Robbie - Whole Scene group and deleted model/group references removed.
- Removed direct effects on deleted props: 0; all other effects, timing and palettes preserved.
- User explicitly deferred controller changes, rendering and uploads while further layout edits are underway. Existing deployed playback files, hardware routing, playlist and nightly schedule remain unchanged. Final consolidated render/deployment is pending.
- Recoverable originals: /Users/elliott.ohara/xlights/Halloween/Backups/All remaining Robbie removal 20261014. Isolated worktree: /Users/elliott.ohara/.codex/worktrees/halloween-remove-robbie/xlights; branch codex/halloween-remove-robbie.

## Rose-bush strand — October 14, 2026

- Rose Bush 1–9 assigned to FPP-KULP16-01 port 8, chained in numeric order as one physical strand and retained as nine separate models. GE Evil Clown stays on port 16.
- Existing pixel counts, null pixels, geometry, groups, faces and all sequence effects preserved.
- Layout-only update: controller uploads, renders and FPP deployment remain explicitly deferred until user finishes other layout work.
- Backups: /Users/elliott.ohara/xlights/Halloween/Backups/Rose bushes Kulp01 port 8 20261014.

## Toni cleanup (penguins retained) — October 14, 2026

- User requested removal of the 21 Toni props other than Toni - Penguin 1 and Toni - Penguin 2, from the master and all 21 current Halloween song layouts. Empty Toni-only groups and deleted model/group references removed.
- Removed direct effects on deleted props: 0; all other effects, timing and palettes preserved.
- User explicitly deferred controller changes, rendering and uploads while further layout edits are underway. Existing deployed playback files, hardware routing, playlist and nightly schedule remain unchanged. Final consolidated render/deployment is pending.
- Recoverable originals: /Users/elliott.ohara/xlights/Halloween/Backups/Toni cleanup keep penguins 20261014. Isolated worktree: /Users/elliott.ohara/.codex/worktrees/halloween-remove-toni/xlights; branch codex/halloween-remove-toni.
- Final consolidated deployment completed October 14, 2026: all 21 renders verified and uploaded; affected controller outputs and Master routing updated. Roses 1–9 share Kulp01 port 8; Dark Helmet 15, Evil Clown 16; both Toni penguins retained. Playlist and sunset–22:30 schedule preserved. Backups: /Users/elliott.ohara/xlights/Halloween/Backups/Final show deployment 20261014.

## Group and yard mapping repair — October 14, 2026

- Approved task: codex/halloween-group-repair in /Users/elliott.ohara/.codex/worktrees/halloween-group-repair/xlights; rendering session B.
- Removed shrub membership from Verts and architectural groups. Added Shrubs, Lantanas, All Bushes, Garden Borders, and four rose banks; retained compatibility group aliases.
- Rebuilt whole-scene coverage with unique enabled physical members; projector/Tune To and inactive Christmas props excluded. Singing accents use outlines; penguin group colors are belly-only.
- Corrected asymmetric MOAW/Starlord/Reel Max part groups. Ports, nulls, pixel counts, geometry, and face definitions unchanged.
- Compatibility mappings: Canes → Garden Borders; Large Spiral Trees → Lantanas; Mini Trees → roses; Mini Tree Stars → borders; Flames → Oak Accents; Mega Tree GRP → oak; Reindeer and Santa → Halloween Accents.
- Native-API additions: [{"source": "Arches - All", "target": "Shrubs", "effects": 47}, {"source": "Arches - All", "target": "Rose Bush GRP", "effects": 47}, {"source": "Arches - All", "target": "Lantanas", "effects": 47}, {"source": "Arches - All", "target": "Garden Borders", "effects": 47}, {"source": "Tombstones", "target": "Halloween Accents", "effects": 4}]
- Removed backed-up direct effects from unconnected mini-tree references after transferring them to matching rose banks: []
- Backup: /Users/elliott.ohara/xlights/Halloween/Backups/Group and mapping repair 20261014. Rendering/deployment pending.
- Final group safety check: removed the unconnected EFL Wing - Left reference from EFL - Wings GRP; its stale relative address overlapped the oak. Connected right wing retained; physical models, ports and addresses unchanged.
- Completed: corrected groups and native effect mappings rendered and verified; uploaded to FPP Master under the existing playlist filename. All 24 yard props verified pixel-by-pixel in musical/static renders; Tune To utility retained. Physical output configuration and nightly schedule unchanged.

## Approved singing-face cast — October 14, 2026

- Worktree: codex/halloween-face-casting; native authoring/rendering session B.
- Cast: clown — hook (Gaga); pumpkin — backing responses (Backing Vocals); teddy — verse (Gaga).
- Faces use real lyric phonemes, automatic blinking, and short handoff fades. Teddy keeps the exact `Teddy ` forced-color face and has independent sparse arm/brow States.
- Added virtual `Cast Safe Outline` for Teddy and redirected six accent/whole-scene group memberships to it: 48 mouth/eye/brow nodes no longer receive group accents. Original submodel, face definitions, states, geometry, pixels, ports and controller connections preserved.
- All non-character effect settings, layers, timing marks and sequence duration preserved; Monster Mash additionally repairs three matrix Faces effects pointing at the absent Monsters track.
- Rendered, mouth-channel verified and deployed under the existing FPP filename. Playlist and schedule were not written; user removals preserved. No controller uploads or audio setting changes.
- Recoverable originals and verification: /Users/elliott.ohara/xlights/Halloween/Backups/Face casting 20261014.

## Full-show deployment — October 17, 2026

Physical model routing/positions synchronized to the current Halloween master, preserving sequence-specific groups and submodels. Singing props excluded from decorative groups and direct non-Faces effects removed; lyric Faces and projector content preserved. Re-rendered and verified FSEQ uploaded under existing playback filename Halloween 2026 - The Dead Dance.fseq. Controller output readbacks, FPP Master DDP routing (including Genius Roof), and Tune To range verified. Playlist and schedule retained. Recoverable local and remote backups: /Users/elliott.ohara/xlights/Halloween/Backups/Full render deployment 20261017-163501


## Occasional voting overlay — October 17, 2026

- Added one native Pictures effect on a new top layer of `Projector`, 109.7–125.7 seconds. Transparent media leaves the existing matrix motion visible around the text bands.
- Invitation: Vote for songs; oharafamilylightshow.com/live. Tune To variants also keep a white Tune to 87.9 footer during the prompt.
- Original effects, settings, palettes, layer order and timing tracks verified unchanged. Physical layout and controller configuration unchanged.
- Website and voting catalog switched to Halloween on October 17, 2026. Rendered overlay uploaded to FPP Master under the existing playback filename; original FSEQ backed up remotely. Existing playback continues through the atomic file replacement.
- Backup: `/Users/elliott.ohara/xlights/Halloween/Sequences/The Dead Dance/Backups/Voting overlay 20261017-195532`. Details: `Tools/voting-overlay-2026.json`. Shared tool: `Halloween/Tools/voting_overlays_2026.py`.


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
- Projector website QR cards hold still for 15 seconds at 10–25, 70–85, 130–145, 190–205 seconds. The QR points to `https://oharafamilylightshow.com/`; song visuals resume between cards.
- Native rendering and original-effect preservation checks passed. Actual sign pixels and every QR interval were checked; a QR extracted from this render decoded to the correct URL.
- Deployed to Master and Projector under the existing playback filenames with complete remote checksum and sequence metadata checks. Master kept running; playlists, schedule, routing and AV settings were preserved.
- Evidence and recoverable originals: `Halloween/website-promotion-latest.json`, `/Users/elliott.ohara/xlights/Halloween/Backups/Website promotion 20261018-201813`.
