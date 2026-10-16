# static halloween — Sequence Agent Notes

Working notes for `Halloween/Sequences/static halloween/static halloween.xsq`. Read alongside the root `AGENTS.md`.

## Media

- Sequence media: `Halloween/Sequences/static halloween/Media/` (lyric video / audio)
- Song images: `Halloween/Sequences/static halloween/Media/Images/`

## Timing

- Song timing templates: `Halloween/Sequences/static halloween/Timing Templates/`

## Tools

- Song scripts: `Halloween/Sequences/static halloween/Tools/`
- Shared API client: `Tools/xlights_api.py` (import via `sys.path` to the repo `Tools/` folder)

## Session / status

- Existing source sequence imported and prepared for the current Halloween layout.

## Halloween 2026 preparation

- Source: `/Volumes/Personal-Drive/xlights/Individual Sequences/static halloween`
- Physical configuration copied from current Halloween master.
- Networks remain linked to the shared Halloween configuration.
- Original effects preserved: 265.
- Unconnected source-reference models: GE Franken Monster (2), Robbie - Longhorn, Elliott - Star 1, Tree - Branches, Tree - Trunk, Mini Tree - 4 Star, Mini Tree - 2 Star, Mini Tree - 3 Star, Mini Tree - 1 Star, Mini Tree - 4, Mini Tree - 2, Mini Tree - 3, Mini Tree - 1, GE Priem Cube SM 1.

## Halloween 2026 deployment

- Prepared on October 13, 2026 using an isolated preparation worktree and xLights slot B.
- Canonical files are now in this Halloween sequence folder; source originals were retained.
- Controller ranges verified against the open canonical Halloween configuration before rendering.
- Retained source-only models are unconnected references, not physical outputs. Existing inactive-model check warnings remain.
- Rendered FSEQ v2: 1200 frames at 25 ms.
- Uploaded to FPP Master (192.168.0.19): `Halloween 2026 - static halloween.fseq`.
- Enabled in Halloween 2026: loops nightly from sunset to a hard stop at 10:30 PM, America/Chicago.
- FPP Master routing now matches the Halloween ranges; Tune To panel output is enabled at channel 243680.
- Controller 192.168.0.249 was initially unreachable but responded successfully during final verification.

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
- Re-rendered and atomically deployed to FPP Master as `Halloween 2026 - static halloween.fseq`; all 261 shrub pixels verified in sampled frames.
- Effect settings, palettes, timings and effect counts preserved. Playlist, schedule and controller output routing unchanged.
- Original layouts, sequence files and renders backed up under `/Users/elliott.ohara/xlights/Halloween/Backups/Center shrub correction 20261013`.

## Kulp01 port cleanup — October 14, 2026

- User requested deletion of the ten Robbie models assigned to FPP-KULP16-01 only; other Robbie-area models retained.
- GE Dark Helmet assigned to port 15 and its broken self-chain removed; GE Evil Clown assigned to port 16.
- Deleted model memberships removed from groups/views and their direct sequence elements removed. Remaining timing, palettes and effects preserved.
- Removed direct effects for deleted props: 0; remaining effects: 145.
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
- Native-API additions: [{"source": "Shrub Center", "target": "Shrubs", "effects": 1}, {"source": "Shrub Center", "target": "Rose Bush GRP", "effects": 1}, {"source": "Shrub Center", "target": "Lantanas", "effects": 1}, {"source": "Shrub Center", "target": "Garden Borders", "effects": 1}, {"source": "Tombstones", "target": "Halloween Accents", "effects": 6}]
- Removed backed-up direct effects from unconnected mini-tree references after transferring them to matching rose banks: []
- Backup: /Users/elliott.ohara/xlights/Halloween/Backups/Group and mapping repair 20261014. Rendering/deployment pending.
- Static-yard verification correction: changed the four mapped Marquee effects from Per Preview to Single Line using delete/re-add through the API; removed the redundant center-only Marquee. Per Preview outlined only group edges and missed interior shrubs. Existing colors, timing, speed and all other effects preserved.
- Final group safety check: removed the unconnected EFL Wing - Left reference from EFL - Wings GRP; its stale relative address overlapped the oak. Connected right wing retained; physical models, ports and addresses unchanged.
- Completed: corrected groups and native effect mappings rendered and verified; uploaded to FPP Master under the existing playlist filename. All 24 yard props verified pixel-by-pixel in musical/static renders; Tune To utility retained. Physical output configuration and nightly schedule unchanged.


## Approved ambient redesign and overnight deployment — October 16, 2026

- User approved the refined look and requested Teddy, then approved scheduling and immediate playback.
- Authored in permanent slot A, branch `codex/static-halloween-refinement`, using xLights 2026.18 automation API. Baseline snapshot commit `8e8e096`; original XSQ also retained in `Backups/Before ambient refinement 20261016/`.
- Replaced the previous decorative pass with 69 effects: amber/violet architectural motion, sparse moving yard texture, distinct Rosa/Starlord/Reel Max/Baby Grand/MOAW part-bank layers, and readable Halloween characters. Existing timings and both Tune To utility effects retained. Layout geometry, face definitions, controller configuration and physical channel ranges unchanged.
- Reviewed the Xtreme style report and actual mapped donor buffer/render strings. Reused approved Holy Forever part-bank recipes; exact reference strings are in `Tools/reference-render-styles.json`. The local source-share volume was unavailable.
- Teddy (`Elliott - EFL Teddy`) uses the exact `Teddy ` face definition (trailing space), `Teddy RedBow static` state, resting mouth and slow automatic blinking. Brown body, forced-color mouth/eyes and red bow preserved.
- Rebuild with `Tools/build_static_halloween.py`: close the sequence before `--prepare`, then `--build` adds effects through the API, renders, and saves again after rendering. The final save is essential: a pre-render save can write a black FSEQ even while the in-memory preview looks correct.
- Verified no same-layer overlaps; final FSEQ has 1,200 frames at 25 ms. At 10 seconds, 368 Teddy pixels and 63,658 scene channels are lit. Details and SHA256 are in `Tools/render-verification.json` and `Tools/overnight-deployment.json`.
- Preview exported to `Preview/static-halloween-refined.mp4` (local, not committed).
- Deployed to FPP Master 192.168.0.19 as `Halloween 2026 - static halloween refined.fseq`; added playlist `Halloween Overnight`. Nightly schedule starts at 22:30 after the musical show and repeats until `SunRise`, zero offset, hard stop. Uses the existing Halloween season date range and America/Chicago time zone.
- Verified actual scheduled playback immediately at 00:34 CDT October 16, with sunrise hard stop at 07:35. Musical show playlist, its sunset–22:30 schedule and all Master output routes remained unchanged. FPP validated all playlists.
- Remote configuration snapshots are in `Backups/Overnight deployment 20261016/`. Previous deployed static FSEQ remains available under its original filename.
- Kulp01 (.253) remains unreachable; user is aware and will fix it in the morning. This did not block deployment.
- Runtime workaround: xLights initially could not follow shared config symlinks on slot startup. Used identical regular copies to launch, then restored relative symlinks before commit; no config changes.
- Unrelated pre-existing slot A Holy Forever/network/media work was preserved in stash `96308ab8c550e5654c7e7271ea99267c80a22bc8` before this task; restore after parking the slot. Do not drop this stash until its contents are verified restored.
