"""Add the 9 `Rose Bush N` models to the sequence master view (idempotent).

They ship excluded from this sequence's master view, so the automation API
rejects them ("target element doesn't exists."). There is no API to add
master-view elements, so this is a direct .xsq edit: add each to
<DisplayElements> (next to the other shrubs) and give it an empty
<EffectLayer/> in <ElementEffects>.

Run with the sequence CLOSED in xLights, then reopen:
    python3 .../Tools/add_rosebush_masterview.py [--dry-run]
"""
import shutil
import sys

XSQ = ('/Users/elliott.ohara/xlights-worktrees/slot-a/Christmas/Sequences/'
       'Holy Forever 2026/Holy Forever 2026.xsq')
ROSE = [f'Rose Bush {i}' for i in range(1, 10)]

DISPLAY_ANCHOR = (
    '    <Element collapsed="false" type="model" name="Shrub Right" '
    'visible="true" />\n'
)
EFFECTS_ANCHOR = (
    '    <Element type="model" name="Rose Bush GRP">\n'
    '      <EffectLayer />\n'
    '    </Element>\n'
)


def main():
    dry = '--dry-run' in sys.argv
    with open(XSQ, encoding='utf-8') as f:
        text = f.read()

    already = all(f'name="{n}" visible=' in text for n in ROSE)
    if already:
        print('rose bushes already in master view — nothing to do')
        return

    display_block = ''.join(
        f'    <Element collapsed="false" type="model" name="{n}" '
        f'visible="true" />\n' for n in ROSE)
    effects_block = ''.join(
        f'    <Element type="model" name="{n}">\n'
        f'      <EffectLayer />\n    </Element>\n' for n in ROSE)

    assert DISPLAY_ANCHOR in text, 'DisplayElements anchor not found'
    assert EFFECTS_ANCHOR in text, 'ElementEffects anchor not found'
    text = text.replace(DISPLAY_ANCHOR, DISPLAY_ANCHOR + display_block, 1)
    text = text.replace(EFFECTS_ANCHOR, EFFECTS_ANCHOR + effects_block, 1)

    print(f'adding {len(ROSE)} rose bushes to DisplayElements + ElementEffects')
    if dry:
        print('dry-run: no writes')
        return
    shutil.copyfile(XSQ, XSQ + '.bak-before-add-rosebush-masterview')
    with open(XSQ, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f'wrote {XSQ}')


if __name__ == '__main__':
    main()
