"""Local integrity and timing checks; no network or model calls."""
import inspect
import re
import tempfile
from pathlib import Path
from urllib.parse import unquote
from tests import test_timing

ROOT = Path(__file__).resolve().parent


def main():
    assert list(ROOT.rglob('SKILL.md')) == [ROOT / 'SKILL.md'], 'multiple discoverable entries'
    links = 0
    for source in ROOT.rglob('*.md'):
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', source.read_text(encoding='utf-8')):
            target = unquote(target.split('#', 1)[0]).strip('<>')
            if not target or re.match(r'^[a-z]+:', target, re.I):
                continue
            assert (source.parent / target).exists(), f'broken link: {source.relative_to(ROOT)} -> {target}'
            links += 1
    count = 0
    temp_root = Path('E:/CodexData/temp')
    temp_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='horizon-check-', dir=temp_root) as temp:
        for name, fn in inspect.getmembers(test_timing, inspect.isfunction):
            if name.startswith('test_'):
                fn(Path(temp))
                count += 1
    print(f'PASS: one entry, {links} internal links, {count} timing behavior tests; media quality not tested')


if __name__ == '__main__':
    main()
