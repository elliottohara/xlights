## Shared Halloween show — October 18, 2026

- Shared-show deployment completed: fresh playback uploaded to Master and Projector, with full Master checksums and every Projector frame verified. Final controller addresses read back; existing playlist/schedule preserved; Master returned to idle.
- Reusable current import maps are the `* - Shared Halloween.xjmap` files in Tools. These point at the merged group/submodel names and omit removed or uninstalled targets. Original maps remain unchanged for historical recovery.
- Consolidation follow-up: the original Tune To row was empty and the rendered sign was black. Native-mirrored all 9 Projector effects onto Tune To, preserving their settings/layers/palettes, then added a white “Tune to 87.9” label on a black 30% backing strip. Other choreography verified unchanged. Details: `Tools/tune_to_defaults_applied.json`.
- Open xLights with `/Users/elliott.ohara/xlights/Halloween` as the show folder, then open this song’s XSQ. The song directory now organizes sequences and media; its separate layout/network configuration was retired. This section supersedes older standalone-show launch instructions below.
- Song-specific groups, submodels, face/state definitions and view were merged into the shared Halloween layout. Conflicting names were separated and all affected effect references updated. Timing, layer order, palettes, blending and render settings were verified against the backed-up sequence; native checks and a fresh render completed.
- Cleared obsolete rows for removed floods/flakes/bulbs and empty mapping groups where present, and trimmed effect tails beyond the song’s final frame. Hidden arches remain available by explicit user instruction. Native render-style recommendations are retained in the check report; purchased render styles were preserved.
- Reusable vendor packages/maps and media remain in this song folder. Earlier one-off layout/import scripts describe historical layouts: do not rerun them against the shared show without adapting their scope and aliases.
- Consolidation, mapping aliases, native checks, original layouts/XSQs/renders and deployment progress: `/Users/elliott.ohara/xlights/Halloween/single-show-consolidation-latest.json`; backup: `/Users/elliott.ohara/xlights/Halloween/Backups/Single Halloween show 20261018-141143`. User authorized the full show upload; consult progress for actual transfer completion.

# Thriller Xtreme Remap — Agent Notes

Fresh review version made October 17, 2026 in slot A. Original Thriller and deployed FPP playback are unchanged.

- Started from current Halloween master layout, including confirmed roof wiring and unassigned FrankenMonster. Per-sequence mapping groups are custom to this copy.
- Imported effects natively with xLights `importXLightsSequence` directly from intact owned Xtreme original ZIP and HD ZIP. Saved `.xjmap` files in Tools. 1,566 retained vendor light effects after preserving existing windows and omitting one unavailable storm-video effect. Source layer ordering, timings, palettes, blend modes, and buffer styles imported by xLights, not reconstructed with addEffect.
- Mapped matching Starlord, MOAW, Rosa Grande, Mini Grand Illusion, Preying Spider and Reel Max families separately. House, roofs, icicles, arches, borders, rose bushes, tombstones, floods and pixel forest mapped by physical role. Original source submodel RIP effects mapped explicitly via `/RIP`.
- Unsupported vendor families (Jolly Roger ship, full 8x8 web, GE Squared, King Diamond, Dragonfly, Triune tomb/cross variants, additional arches/tombs) remain documented in Tools/Base unavailable.json and HD unavailable.json rather than collapsed across unrelated spinner families.
- Base vendor ZIP lacks Michael_Jackson_Thriller_HD.mp4 and Michael Jackson - Thriller.mp4; HD lacks Halloween Storm Clouds.mp4. Retained existing physical window matrix effects; omitted the one unavailable cloud-video effect on the mapped pixel forest. No missing referenced media remains. User was asked optionally whether to substitute window videos; absent a reply, existing window effects were retained.
- Projector preserved from original canonical Thriller via native import. Every projector effect retains its effect type, layer, start/end times, settings, palette, and SHA256-identical media. Only file paths changed as xLights copied assets. Existing physical singing-face effects and lyric timing tracks retained through native import.
- Verification: Tools/verification.json. Preview MP4 and rendered FSEQ are review deliverables; no upload/deployment performed.
- Worktree has unrelated pre-existing dirty work; no branch switch or cleanup was performed.

## Singing-only and media repair — October 17, 2026

User forbids decorative effects on any singing prop. Removed 64 direct/group/submodel memberships involving singers (including the three singing window matrices), plus 106 decorative effects on singers or now-empty accent groups. Re-added 31 Faces effects using addEffect, preserving each face definition (including Teddy trailing space), palette, timing and layers, and enabling SuppressWhenNotSinging. Clipped the overlong downstairs Faces effect at sequence end. No setEffectSettings used.

Repaired 490 stale face-image attribute paths to existing local assets in this per-sequence layout. Native Check Sequence now reports no missing files for the effects in use. Other unused layout face-definition/controller warnings still exist; the report is not globally clean. Actual projector MP4s are valid and decode at their used start times; no YouTube download was needed. All projector effects, content, timing and parameters remain untouched. No non-Faces effect reaches any singer, verified by recursively expanding every effect target group. Re-rendered and exported the review MP4. Nothing uploaded to live FPP.

## Tombstone chain — October 17, 2026

Six photo-matched tombstones reassigned to Kulp16-01 port11: Tombsone large, Tombsone Small, Boscoyo ChromaStone1, Tombsone large-2, Boscoyo ChromaStone5 (cross), Boscoyo ChromaStone3. 169 configured pixels. Extra Tombsone Small-2 retained unassigned and hidden. Layout positions updated left-to-right. Hardware upload and fresh rendering remain pending; existing renders predate this channel change. Backup: /Users/elliott.ohara/xlights/Halloween/Backups/Tombstones one chain 20261017-162320

## Full-show deployment — October 17, 2026

Physical model routing/positions synchronized to the current Halloween master, preserving sequence-specific groups and submodels. Singing props excluded from decorative groups and direct non-Faces effects removed; lyric Faces and projector content preserved. Re-rendered and verified FSEQ uploaded under existing playback filename Halloween 2026 - Thriller.fseq. Controller output readbacks, FPP Master DDP routing (including Genius Roof), and Tune To range verified. Playlist and schedule retained. Recoverable local and remote backups: /Users/elliott.ohara/xlights/Halloween/Backups/Full render deployment 20261017-163501


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
