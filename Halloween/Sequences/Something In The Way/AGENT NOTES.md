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

# Something In The Way — Sequence Agent Notes

Working notes for `Halloween/Sequences/Something In The Way/Something In The Way.xsq`. Read alongside the root `AGENTS.md`.

## Media

- Sequence media: `Halloween/Sequences/Something In The Way/Media/` (lyric video / audio)
- Song images: `Halloween/Sequences/Something In The Way/Media/Images/`

## Timing

- Song timing templates: `Halloween/Sequences/Something In The Way/Timing Templates/`

## Tools

- Song scripts: `Halloween/Sequences/Something In The Way/Tools/`
- Shared API client: `Tools/xlights_api.py` (import via `sys.path` to the repo `Tools/` folder)

## Session / status

- Rebuilt October 15, 2026 using native xLights Import Effects / Map Effects directly from the original purchased ZIP. The earlier effect-by-effect reconstruction was rejected and is retained only in Backups.
- Saved reusable map: `Tools/Vendor to Halloween.xjmap`. 892 donor effects imported, with their layers, colors, fades, and render styles; xLights converted older Wave and chase settings to the current format.
- Independent families stay separate: Squared → left MOAW; 8x8 Web → right MOAW; Dragonfly → Reel Max 1; King Diamond → Reel Max 2; Fuzion → Starlords; Rosa Grande → Rosa Grande; Grand Illusion → Mini Grand Illusion. Corresponding submodel groups preserve each family's detailed choreography.
- Tomb portions → tombstones; bat portions → flying bats; mini trees → Lantanas; pixel forest → shrubs and roses. Spider-size banks use separate pairs of the four physical spiders. Window video → window matrices; main video → Projector. Zombie-sign effects are omitted because there is no corresponding sign.
- Vendor singing rows map to Teddy (Spooky Tree), Evil Clown (Skull 1), and Pumpkin (Skull 2). Native imported timing and vocal blocks are preserved, with only physical face definitions and singing suppression adapted. Teddy uses the exact `Teddy ` definition. Its safe accent outline protects mouth and eye pixels.
- Rendered at 25 ms. Verified 107 physical strand/prop outputs, all three singing mouths, asset availability, and a visual preview. Controller assignments, wiring, and master layout are unchanged.
- Original ZIP: `Halloween/Source Packages/xTreme Sequences/something-in-the-way-c29tZXRoaW5nLWluLXRoZS1.zip`. Working evidence and deployment result: `Halloween/Backups/Native mapped imports 20261015/`.
- Deployment verified October 15: FSEQ on FPP Master; matching audio on Master and Projector; appended to the existing Halloween playlist without restoring removed songs or changing its schedule.

## Character continuity correction — October 15, 2026

- User dislikes characters blinking off between words or short vocal sections. Disabled whole-character suppression on Teddy, Evil Clown, and Pumpkin; retained the original timing tracks, casting, physical face definitions, and non-face effects.
- Characters hold a resting mouth between assigned vocal blocks separated by 10 seconds or less. Longer breaks use a 2.5-second exit and 1-second entrance; Teddy retains the original slow 10-second ending fade. Outlines remain enabled consistently.
- Replaced only Faces effects via native addEffect after backed-up selective deletion. No setEffectSettings, layout, wiring, playlist, or audio-setting changes.
- Rendered output checked every 25 ms: no unintended outline blackouts across 16,901 character-frames. Sampled original phonemes match exactly with no extra mouth pixels; exit brightness decreases gradually.
- Work branch: codex/halloween-face-continuity. Both permanent slots contained unrelated edits, so used a separate managed worktree and xLights B with render copies in Halloween/Backups/Face continuity 20261015/Sequences. Original XSQ/FSEQ/layout/notes and verification evidence are retained in that backup folder.
- Corrected FSEQ uploaded and verified on FPP Master October 15 at 08:31 CDT under its existing filename. Playlist, nightly schedule, controller outputs, and Projector audio configuration verified unchanged. Local preview refreshed.


## Radio station sign — October 16, 2026

- Added a full-duration white “Tune to 87.9” Text effect through the native xLights API. Existing effects and timing outside Tune To verified unchanged.
- Authored in permanent slot B on codex/halloween-tune-to-879; original files and renders backed up in Halloween/Backups/Tune to 879 20261016.
- Rendered sign pixels inspected and corrected FSEQ uploaded to FPP Master under the existing playback filename. Playlist, schedule and controller routing preserved.

## Full-show deployment — October 17, 2026

Physical model routing/positions synchronized to the current Halloween master, preserving sequence-specific groups and submodels. Singing props excluded from decorative groups and direct non-Faces effects removed; lyric Faces and projector content preserved. Re-rendered and verified FSEQ uploaded under existing playback filename Halloween 2026 - Something In The Way.fseq. Controller output readbacks, FPP Master DDP routing (including Genius Roof), and Tune To range verified. Playlist and schedule retained. Recoverable local and remote backups: /Users/elliott.ohara/xlights/Halloween/Backups/Full render deployment 20261017-163501


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
