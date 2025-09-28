from __future__ import annotations

import argparse
import sys
from pathlib import Path

from annox.core import registry as reg
from annox.core.validate import validate_dataset_file
from annox.core.convert import convert as core_convert


def _cmd_validate(args: argparse.Namespace) -> int:
    path = Path(args.path)
    ok, report = validate_dataset_file(path)
    if ok:
        print(f"OK: {report['items']} items, {report['annotations']} annotations")
        return 0
    else:
        print("Validation failed:")
        for msg in report.get("errors", []):
            print(f"- {msg}")
        return 2


def _cmd_list_formats(_: argparse.Namespace) -> int:
    adapters = reg.AdapterRegistry().list_adapters()
    if not adapters:
        print("No adapters discovered yet. Install plugins exposing 'annox.adapters'.")
        return 0
    for name, adapter in adapters.items():
        caps = {}
        try:
            caps = adapter.capabilities()  # type: ignore[attr-defined]
        except Exception:
            pass
        print(f"{name}: {caps if caps else '{}'}")
    return 0


def _cmd_convert(args: argparse.Namespace) -> int:
    src_fmt = args.source_format
    dst_fmt = args.dest_format
    src = Path(args.src)
    dst = Path(args.dst)
    try:
        core_convert(src, dst, src_fmt, dst_fmt)
    except Exception as e:
        print(f"convert failed: {e}")
        return 2
    print(f"Wrote: {dst}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="annox", description="Annotation Exchange Tool")
    sub = p.add_subparsers(dest="cmd", required=True)

    pv = sub.add_parser("validate", help="Validate an intermediate dataset JSON/JSONL file")
    pv.add_argument("path", help="Path to dataset file (.json or .jsonl)")
    pv.set_defaults(func=_cmd_validate)

    pl = sub.add_parser("list-formats", help="List discovered adapters and capabilities")
    pl.set_defaults(func=_cmd_list_formats)

    pc = sub.add_parser("convert", help="Convert datasets between formats")
    pc.add_argument("--from", dest="source_format", required=True, help="Source format name")
    pc.add_argument("--to", dest="dest_format", required=True, help="Destination format name")
    pc.add_argument("--src", required=True, help="Source path")
    pc.add_argument("--dst", required=True, help="Destination path (file or dir)")
    pc.set_defaults(func=_cmd_convert)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
