#!/usr/bin/env python3
"""
Build stub NSS/NSPR shared libraries so a downloaded Chromium can launch on a
bare sandbox that has no system NSS (no apt, no libnss3).

Why this exists
---------------
`@sparticuz/chromium` ships a portable Chromium binary, but it still links
against the host's `libnss3.so`, `libnssutil3.so` and `libnspr4.so`. Chromium
only uses NSS for its certificate database — never for WebGL, layout or the
scroll engine — so empty stubs are sufficient to run the mascot verification
on a machine where NSS cannot be installed.

The shim only provides the exact symbols and version tags the binary asks for,
which are read straight out of its dynamic symbol table, so it stays correct
even if the Chromium build changes.

Usage
-----
    python3 testing/tools/build_headless_chromium_shims.py /tmp/chromium --out /tmp/nssshim

Then launch with:
    LD_LIBRARY_PATH=/tmp/nssshim python3 testing/e2e/verify_mascot_walk_dock.py
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

LIB_BY_PREFIX = {'nss': 'libnss3.so', 'nssutil': 'libnssutil3.so', 'nspr': 'libnspr4.so'}
SONAME = {'nss': 'libnss3.so', 'nssutil': 'libnssutil3.so', 'nspr': 'libnspr4.so'}

DYNSYM_RE = re.compile(
    r'^\s*\d+:\s+([0-9a-f]+)\s+(\d+)\s+(\w+)\s+\w+\s+\w+\s+UND\s+'
    r'(\S+?)(?:@([\w.]+))?\s*(?:\(\d+\))?\s*$')


def read_undefined(chromium: Path):
    """Return {(symbol, version or None): (type, size)} for undefined symbols."""
    out = subprocess.run(['readelf', '--dyn-syms', '-W', str(chromium)],
                         capture_output=True, text=True, check=True).stdout
    symbols = {}
    for line in out.splitlines():
        if ' UND ' not in line:
            continue
        m = DYNSYM_RE.match(line)
        if not m:
            continue
        _, size, sym_type, name, version = m.groups()
        symbols[(name, version)] = (sym_type, int(size or 0))
    return symbols


def classify(name: str, version: str | None) -> str | None:
    if name.startswith('PR_') and version is None:
        return 'nspr'
    if version and version.startswith('NSSUTIL_'):
        return 'nssutil'
    if version and version.startswith('NSS_'):
        return 'nss'
    return None


def emit_stubs(buckets: dict, out_dir: Path):
    """Write one C file + linker version script per shim library."""
    written = {}
    for lib, entries in buckets.items():
        if not entries:
            continue
        funcs, objects, versions = [], [], {}
        for (name, version), (sym_type, size) in sorted(entries.items()):
            if sym_type == 'OBJECT':
                objects.append(f'char {name}[{max(size, 64)}] = {{0}};')
            else:
                funcs.append(f'void {name}(void) {{ }}')
            if version:
                versions.setdefault(version, []).append(name)

        c_path = out_dir / f'{lib}.c'
        c_path.write_text(
            f'/* Auto-generated NSS shim for {SONAME[lib]} — see '
            f'testing/tools/build_headless_chromium_shims.py */\n'
            + '\n'.join(funcs + objects) + '\n', encoding='utf-8')

        map_path = out_dir / f'{lib}.map'
        if versions:
            blocks = []
            for version, names in versions.items():
                blocks.append('{version} {{ global: {names}; }};'.format(
                    version=version, names='; '.join(names)))
            # NOTE: an anonymous `local: *;` clause cannot be combined with
            # named version tags (ld: "anonymous version tag cannot be combined
            # with other version tags"), so only named blocks are emitted.
            map_path.write_text('\n'.join(blocks) + '\n', encoding='utf-8')
        else:
            map_path.write_text('{ global: PR_*; };\n', encoding='utf-8')
        written[lib] = (c_path, map_path)

    return written


def compile_shims(written: dict, out_dir: Path):
    built = []
    for lib, (c_path, map_path) in written.items():
        so = out_dir / SONAME[lib]
        cmd = ['gcc', '-shared', '-fPIC', '-w', '-o', str(so), str(c_path),
               f'-Wl,--version-script={map_path}', f'-Wl,-soname,{SONAME[lib]}']
        subprocess.run(cmd, check=True)
        built.append(so)
    return built


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('chromium', nargs='?', default='/tmp/chromium')
    parser.add_argument('--out', default='/tmp/nssshim')
    args = parser.parse_args()

    chromium = Path(args.chromium)
    if not chromium.exists():
        print(f'Chromium binary not found: {chromium}', file=sys.stderr)
        return 1
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    symbols = read_undefined(chromium)
    buckets = {'nss': {}, 'nssutil': {}, 'nspr': {}}
    for key, meta in symbols.items():
        lib = classify(*key)
        if lib:
            buckets[lib][key] = meta

    summary = {lib: len(entries) for lib, entries in buckets.items()}
    print(f'stub symbols per library: {summary}')
    written = emit_stubs(buckets, out_dir)
    built = compile_shims(written, out_dir)
    for so in built:
        print(f'built {so}')
    print(f'\nLaunch Chromium with LD_LIBRARY_PATH={out_dir}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
