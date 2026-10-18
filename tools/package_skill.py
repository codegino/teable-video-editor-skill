#!/usr/bin/env python3
"""Build a deterministic, text-only .skill archive from an explicit allowlist."""
import argparse
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAME = 'teable-video-editor'
FILES = [
    'SKILL.md', 'LICENSE', 'THIRD_PARTY_NOTICES.md',
    'scripts/setup.mjs', 'scripts/transcribe.py',
    'examples/code-gino.md',
]


def build(output):
    payloads = {}
    for relative in FILES:
        path = ROOT / relative
        if path.is_symlink() or not path.is_file():
            raise ValueError(f'Expected an ordinary source file: {relative}')
        data = path.read_bytes()
        data.decode('utf-8')
        if len(data) > 500 * 1024:
            raise ValueError(f'File exceeds install limit: {relative}')
        payloads[relative] = data
    if len(payloads) > 100 or sum(map(len, payloads.values())) > 5 * 1024 * 1024:
        raise ValueError('Package exceeds skill install limits')
    skill = payloads['SKILL.md'].decode('utf-8')
    if not skill.startswith('---\n') or f'name: {NAME}\n' not in skill.split('---', 2)[1]:
        raise ValueError('Skill metadata name is missing or unexpected')
    output = Path(output)
    if output.suffix != '.skill':
        raise ValueError('Output must have a .skill extension')
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for relative, data in sorted(payloads.items()):
            info = zipfile.ZipInfo(f'{NAME}/{relative}', date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, data)
    print(f'Packaged {len(payloads)} text files: {output}')
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'dist' / f'{NAME}.skill')
    build(parser.parse_args().output)
