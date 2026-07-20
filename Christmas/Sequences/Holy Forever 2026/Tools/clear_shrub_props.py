"""Direct .xsq reset of every `All Shrubs GRP` member to a single empty
EffectLayer.

Needed because the xLights automation API cannot delete effects on
layers above L0 (`cloneModelEffects` from a 1-layer source only clears L0,
and even a multi-layer/group source did not clear L1 in 2026.13 — verified
by probe). Per AGENTS.md, removing effects the API can't touch is a
legitimate direct .xsq edit.

Run with the sequence CLOSED in xLights (it rewrites the .xsq), then reopen:
    python3 .../Tools/clear_shrub_props.py [--dry-run]
"""
import re
import shutil
import sys

XSQ = ('/Users/elliott.ohara/xlights-worktrees/slot-a/Christmas/Sequences/'
       'Holy Forever 2026/Holy Forever 2026.xsq')

PROPS = [
    'Shrub Left', 'Shrub Center', 'Shrub Right',
    'Door Tree Left', 'Door Tree Right',
] + [f'Rose Bush {i}' for i in range(1, 10)]


def main():
    dry = '--dry-run' in sys.argv
    with open(XSQ, encoding='utf-8') as f:
        text = f.read()

    total_effects = 0
    for name in PROPS:
        pat = re.compile(
            r'(<Element type="model" name="' + re.escape(name) + r'">)'
            r'.*?(</Element>)',
            re.DOTALL,
        )
        m = pat.search(text)
        assert m, f'element not found: {name}'
        block = m.group(0)
        n = block.count('<Effect ')
        total_effects += n
        replacement = m.group(1) + '\n      <EffectLayer />\n    ' + m.group(2)
        text = text[:m.start()] + replacement + text[m.end():]
        print(f'{name}: cleared {n} effect(s)')

    print(f'total effects removed: {total_effects}')
    if dry:
        print('dry-run: no writes')
        return
    shutil.copyfile(XSQ, XSQ + '.bak-before-clear-shrub-props')
    with open(XSQ, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f'wrote {XSQ}')


if __name__ == '__main__':
    main()
