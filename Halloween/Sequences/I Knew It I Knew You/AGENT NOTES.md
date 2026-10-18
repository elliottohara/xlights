## Garage layout batch render — October 18, 2026

- Re-rendered from the canonical shared Halloween layout after restoring the garage line to outline, all-pixel and vertical groups. Native checks found no missing models, unexpected zero-node effects, impossible overlaps or effects beyond the end; authored effects and frame timing remain unchanged.
- All 73 Garage Left Bottom pixels and all 30 Wall - Garage Top pixels light in one-second samples at their new porch Genius port 8 addresses. Tune To output is lit. Full batch evidence and recoverable previous renders: `Halloween/garage-batch-render-latest.json`.
- This is a local render only; deployment remains pending. Master stayed running throughout and must remain running.

## Shared Halloween show — October 18, 2026

- Shared-show deployment completed: fresh playback uploaded to Master and Projector, with full Master checksums and every Projector frame verified. Final controller addresses read back; existing playlist/schedule preserved; Master returned to idle.
- Reusable current import maps are the `* - Shared Halloween.xjmap` files in Tools. These point at the merged group/submodel names and omit removed or uninstalled targets. Original maps remain unchanged for historical recovery.
- Open xLights with `/Users/elliott.ohara/xlights/Halloween` as the show folder, then open this song’s XSQ. The song directory now organizes sequences and media; its separate layout/network configuration was retired. This section supersedes older standalone-show launch instructions below.
- Song-specific groups, submodels, face/state definitions and view were merged into the shared Halloween layout. Conflicting names were separated and all affected effect references updated. Timing, layer order, palettes, blending and render settings were verified against the backed-up sequence; native checks and a fresh render completed.
- Cleared obsolete rows for removed floods/flakes/bulbs and empty mapping groups where present, and trimmed effect tails beyond the song’s final frame. Hidden arches remain available by explicit user instruction. Native render-style recommendations are retained in the check report; purchased render styles were preserved.
- Reusable vendor packages/maps and media remain in this song folder. Earlier one-off layout/import scripts describe historical layouts: do not rerun them against the shared show without adapting their scope and aliases.
- Consolidation, mapping aliases, native checks, original layouts/XSQs/renders and deployment progress: `/Users/elliott.ohara/xlights/Halloween/single-show-consolidation-latest.json`; backup: `/Users/elliott.ohara/xlights/Halloween/Backups/Single Halloween show 20261018-141143`. User authorized the full show upload; consult progress for actual transfer completion.

# I Knew It I Knew You — Sequence Agent Notes

Working notes for `Halloween/Sequences/I Knew It I Knew You/I Knew It I Knew You.xsq`. Read alongside the root `AGENTS.md`.

## Media

- Sequence media: `Halloween/Sequences/I Knew It I Knew You/Media/` (lyric video / audio)
- Song images: `Halloween/Sequences/I Knew It I Knew You/Media/Images/`

## Timing

- Song timing templates: `Halloween/Sequences/I Knew It I Knew You/Timing Templates/`

## Tools

- Song scripts: `Halloween/Sequences/I Knew It I Knew You/Tools/`
- Shared API client: `Tools/xlights_api.py` (import via `sys.path` to the repo `Tools/` folder)

## Session / status

- Built October 17, 2026 directly in the canonical Halloween sequence folder, following the ordinary-Halloween workflow override in root AGENTS.md. xLights A (49913) owns this song's show folder. The other active repair chat owns xLights B; do not interrupt that instance.
- Matching purchased audio attached October 17 after the user downloaded it. File: `Media/01 - I Knew It, I Knew You (From _Toy Story 5_).mp3`; SHA256 verified identical to Downloads. Duration 178.185986 seconds versus donor 178.185 seconds (0.986 ms difference). Title/artist match the donor. Sequence is now Media, with an absolute audio path and unchanged 178.200-second / 25 ms timeline. User approval remains pending; do not upload it.
- Original package retained in `Halloween/Source Packages/xTreme Sequences/i-knew-it-i-knew-you-aS1rbmV3LWl0LWkta25ldy1.zip`; intact extracted vendor show under `Tools/Vendor original/`. Original donor is 178.185 seconds at 25 ms. Review timeline is 178.200 seconds to include its full final frame.
- Imported directly from the original ZIP with xLights `importXLightsSequence` and saved `Tools/Vendor to Halloween.xjmap`. No donor choreography was reconstructed with addEffect. 121 source rows map to active destinations. Current final has 5,345 effects: 5,157 unchanged imported light effects, three physically adapted Faces effects, 183 mirrored Projector effects on Tune To, and its two local frequency/backing-strip effects. One decorative donor State effect on the lead singer was removed to comply with singing-only rules.
- Verified the 5,157 unmodified donor effects retain effect type, layer and row ordering, start/end times, palette, every authored setting, blending, and render styles. xLights explicitly serialized eleven otherwise implicit 2D preview-camera defaults. All six donor timing tracks match mark-for-mark: Beats, Bars, Main_Vocal, Winds, Ha, Backup_Vocal.
- Matching Rosa and Starlord banks remain separate from Mini Grand Illusion, left/right MOAW, and left/right Reel Max. Squared -> left MOAW and King Diamond -> right Reel Max reuse established Something In The Way mappings. Shape Shifter -> right MOAW and Space Odyssey -> left Reel Max are approximate geometric counterparts on their own physical props. No independent spinner families share a destination family.
- Added 110 **missing** donor Rosa part subsets only to this per-song layout. Verified compatible node numbering against 412 shared standard submodels (411 exact matches); preserved every existing user subset, including the pre-existing variant. New subsets all stay within 1-1392. Master layout and controller assignments remain unchanged.
- Main Matrix 1 art/video -> Projector. Window matrix choreography -> six column matrices. Physical window singers and all other singing props/submodels are excluded from decorative groups. House lines, roof flakes, shrubs, roses, garden/driveway borders, columns, oak, Lantanas, tombs, floods and both wing fans map by available role.
- Lead -> Teddy with exact `Teddy ` face definition and `Teddy RedBow static` state; backing -> Evil Clown and Singing Pumpkin with their physical definitions. Only lyric-driven Faces reach singers. **Latest user correction: singers stay visible throughout the entire song, including when not singing.** SuppressWhenNotSinging is disabled, Faces span 0-178200 ms, and face fades are zero. Mouths still follow original lyric tracks and rest between lyrics. Tune To displays white `Tune to 87.9` throughout.
- **Unavailable / disabled props:** master disables Mega Tree, Tree Topper, triple arches and all four large yard flakes, so their source rows were omitted after native Check Sequence reported zero nodes. Kraken, fireworks, spiral trees, Kings Ransom, Fuzion, CC Boom, and Starburst families lack remaining appropriate installed counterparts. All 2,569 omitted source effects remain intact in the original package, with row-by-row records in `Tools/import plan.json`; do not stack these independent families on already-used spinners.
- Native importer retained packaged assets under this song's Media directory. Five Sketch background references are resolved via local `Images/I_Knew_it -> ../Media/I_Knew_it`; their original effect settings are unchanged. Native getMediaIssues reports no playback compatibility issues. Check Sequence has no missing/hidden model effects, no effects with zero nodes, no impossible overlaps, and no effects beyond sequence end. Inherited unused layout/controller/face-definition warnings remain, plus a donor Sketch with an intentionally empty preview-background filename and asset downscaling warnings; do not describe the global report as clean.
- Rendered FSEQ is 7,128 frames at 25 ms (178.200 s). After the roof correction, checked channel output for all 113 mapped physical strands/props; none stay dark. Tune To pixels are additionally verified in their separate report. Sampled five distinct phonemes on each of three singers: all expected mouth nodes light, with zero extra mouth pixels. Evidence: `Tools/verification.json`, saved native import and comparisons, controller output reference, and backups.
- Final review with audio: `Preview/I Knew It I Knew You - approval preview.mp4` (1400x1120). Earlier silent visual baseline retained at `Preview/I Knew It I Knew You - visual review.mp4`. No uploads, playlist edits, or schedule changes performed. User approval remains pending.

## Audio completion — October 17, 2026

- Saved and closed xLights A; backed up `Backups/Before audio attachment.xsq`. Changed only header sequence type/media path, verified all effect databases, palettes, display rows and timing/effect elements were unchanged. Reopened in xLights and verified the full audio path, 178200 ms length, 25 ms frames and no media compatibility issues.
- Checked decoded audio's low-frequency onset envelope against all 272 imported Beats marks. Best phase is +10 ms; zero phase is essentially equivalent, both within one 25 ms frame. Retained every original timing mark and effect time. Evidence: `Tools/audio beat alignment.json`, `Tools/audio attachment.json`.
- Re-rendered with audio and reran the full native-import fidelity / 105-output / three-mouth verification. Audio is now present and the final-sync blocker is cleared. Final approval preview is generated through xLights at 1400x1120.
- Final MP4 verified H.264 + AAC, both 178.200 seconds from time zero. Compared embedded preview audio against the purchased MP3 near 6, 80 and 165 seconds: zero measured offset at all three locations and 0.970-0.997 envelope correlation (AAC compression accounted for). No muxing offset or end-of-song drift found. Evidence: `Tools/preview audio verification.json`.
- Upload/deployment is not yet authorized. User must review and approve first.

## Continuous singer visibility — October 17, 2026

- User explicitly rejected singers disappearing between vocals and requested them on all the time. This overrides earlier suppression notes and is recorded in root AGENTS.md for future work.
- Replaced only the three Faces effects through native addEffect after backed-up selective removal. Kept their face definitions (including Teddy's trailing space), states, palettes, original vocal tracks and layers. Disabled whole-character suppression, extended all three through the full song, and removed entrance/exit fades. All other effects and timing remain unchanged.
- Script: `Tools/keep_singers_visible.py`. Recoverable pre-change XSQ, preview and verification under `Backups/Always visible singers <timestamp>/`. Updated verification checks all 7,128 frames for each singer, alongside the existing imported-effect and phoneme checks. Updated approval preview uses the same path.

## Roof outline grouping correction — October 17, 2026

- User noticed the upper roof ridges were missing from outline choreography. Checked master and per-song layouts: `House Outline` already contains all eight upper pieces, but the sequence's imported `Eaves GRP` expanded only `Eves GRP`, omitting the ridges. No sequence effect reached any of those eight pieces.
- Corrected only `Import Xtreme - Eaves GRP` in this song's layout to expand the existing full `Roof` group. Added `Roof  - Peak`, `Roof - Line Right`, `Roof - Top Left`, `Roof - Left Ridge`, `Roof - Middle Ridge Line`, `Roof - Top Center`, `Roof - Garage Ridge`, `Roof - Middle Ridge`, and `Icicles - Gutters/Gutters`. Its 211 original vendor effects now cover the complete roof outline.
- Master `House Outline`, master layout, model channel assignments and all effects remain unchanged. Verified XSQ SHA256 identical before/after the group edit. Updated `Tools/prepare_mapping.py` and import-plan membership so rebuilding preserves the fix. Backups and evidence: `Backups/Roof outline group <timestamp>/`, `Tools/roof outline group repair.json`.
- Reloaded only this song's xLights A instance and re-rendered the existing approval preview path. Singing characters retain continuous visibility.

## Projector content on Tune To and harness default — October 17, 2026

- User requested Tune To mirror the projector with the radio frequency overlaid, and requested this as the default for every new sequence. Copied all 183 effects / 15 source layers from `Import Xtreme - Matrix 1` onto Tune To using native Import Effects with a saved map and complete media package. Source timing, palette, settings and relative layer order match exactly after resolving equivalent media paths. Other elements are unchanged.
- Tune To has two top layers: white `Tune to 87.9` (Arial 14) above a solid black strip occupying the lower 30% of the sign. Full-song coverage, no fades. The projector choreography remains visible above it. Verified every frame of the 192x64 output: frequency strip pixels are constant, the white label is present, and more than 100 sampled content frames differ. `Tools/Tune To pixel verification.json` records the results.
- Shared helper: root `Tools/apply_sequence_defaults.py`. Native clone was rejected after its function-static source pointer produced a wrong copy on reuse across reopen; use the helper's native import instead. An initial loose-XSQ import triggered missing-media warnings despite existing files; the helper now packages the referenced media and verifies paths. Complete-package imports and repeated application passed. Unchanged defaults are detected and skipped; no duplicate effects or layers accrue.
- New scaffold creates `Tools/sequence_defaults.json` and `Tools/finalize_sequence.py`; this song has both. Root `Tools/xlights_api.py::render_all()` applies the policy automatically for scaffolded songs. Direct API render callers must apply the finalizer first. Root AGENTS.md and the setup-sequence skill document the default. Scaffold smoke test and Python/shell syntax checks pass; skill frontmatter validated with Ruby YAML because the optional validator's PyYAML dependency is absent.
- Final native media compatibility check reports no issues. Check Sequence has zero active sequence error items; inherited unused layout warnings and the donor's empty Sketch preview-background warnings remain. Final preview includes audio at the same approval-preview path. No live upload performed.

## Garage matrix and matching window outlines — October 18, 2026

- User requested the garage matrix behave like the column matrices and reported inconsistent windows. Worked directly in the canonical Halloween folder using xLights A (49913); left B and the other song untouched.
- `Import Xtreme - Widow Matrix GRP` now contains all six `Matrix - C1..C6` models plus `Matrix-Garage Window`. The full garage matrix follows the existing native matrix choreography, including every layer, palette, timing and render style. It is excluded from the window-outline effect group to avoid competing stacks on its pixels.
- `Import Xtreme - Windows GRP` previously contained only `Window - Bottom Left` and `Window - Play Room`; the blanket singer exclusion had removed the two other matrix perimeter submodels. Restored `Matrix - Downstairs Window/Window - Bedroom` and `Matrix - Entry/Window - Entry` to this imported destination group. All four window outlines now receive the same vendor window choreography. Only their existing perimeter nodes are used; matrix interiors stay dark.
- These are explicit per-song exceptions to the former blanket decorative exclusion for window matrix models. The physical vocal cast remains Teddy, Evil Clown and Singing Pumpkin. Their full-song Faces effects and resting-mouth visibility are unchanged. Existing model/submodel definitions, controller routing and both master layout files remain untouched.
- Changed only the two imported group memberships in the per-song layout. Verified the sequence EffectDB, ColorPalettes, DisplayElements and ElementEffects are byte-for-byte identical as parsed XML before/after. All 5,157 donor light effects remain unchanged; total remains 5,345. Original six timing tracks, source layer order/blending/buffer styles, audio, Tune To/projector effects and all three continuous singer checks pass.
- Updated `Tools/prepare_mapping.py` and `Tools/import plan.json` to preserve this routing on future rebuilds. `Tools/verify_mapping.py` permits only these exact group-specific decorative exceptions; other singers remain protected. Repair script: `Tools/match_garage_and_windows.py`; focused pixel verification: `Tools/verify_garage_and_windows.py`.
- Re-rendered all 7,128 frames and refreshed `Preview/I Knew It I Knew You - approval preview.mp4` with audio. Checked all seven matrix outputs and all four outlines at 713 samples across the song: every target lights, with zero interior pixel leaks on entry/downstairs. Full verification now covers 119 physical output strands/props and all-frame singer visibility. Visually inspected 2 s, 60 s and 100 s preview frames. Native media check is empty; sequence section has no missing/hidden models, zero-node effects, impossible overlaps or per-model buffer errors. Inherited unused controller/model/face warnings and donor Sketch background warnings remain.
- Recoverable original sequence/layout/preview/import-plan/verification are under the backup recorded by `Tools/garage and windows repair.json`. Approval preview remains local; no upload or playlist/schedule changes were made.


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
