#!/usr/bin/env python3
"""Copy GitHub Actions skill assets into a target project."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

WORKFLOW_ASSETS = {
    "ci": ("ci.yml", "ci.yml"),
    "app": ("app-release.yml", "app-release.yml"),
    "tauri": ("tauri-release.yml", "tauri-release.yml"),
    "docker": ("docker-release.yml", "docker-release.yml"),
}


def copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    print(f"copied {src.relative_to(ROOT)} -> {dst}")


def assert_copyable(operations: list[tuple[Path, Path]], force: bool) -> None:
    missing = [src for src, _ in operations if not src.is_file()]
    if missing:
        raise SystemExit("Asset file not found: " + str(missing[0]))

    conflicts = [dst for _, dst in operations if dst.exists()]
    if conflicts and not force:
        raise SystemExit(
            "Target already exists: "
            + str(conflicts[0])
            + ". Pass --force to overwrite.",
        )


def workflow_operation(kind: str, target: Path) -> tuple[Path, Path]:
    asset_name, workflow_name = WORKFLOW_ASSETS[kind]
    return (
        ASSETS / asset_name,
        target / ".github" / "workflows" / workflow_name,
    )


def docker_operations(target: Path) -> list[tuple[Path, Path]]:
    src_dir = ASSETS / "docker"
    if not src_dir.is_dir():
        raise SystemExit(f"Asset directory not found: {src_dir}")

    operations = []
    for src in sorted(path for path in src_dir.rglob("*") if path.is_file()):
        if src.name == ".DS_Store":
            continue
        operations.append((src, target / src.relative_to(src_dir)))
    return operations


def copy_operations(operations: list[tuple[Path, Path]], force: bool) -> None:
    assert_copyable(operations, force)
    for src, dst in operations:
        copy_file(src, dst)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Copy GitHub Actions workflow and project assets.",
    )
    parser.add_argument(
        "kind",
        choices=sorted(WORKFLOW_ASSETS),
        help="Asset set to copy.",
    )
    parser.add_argument(
        "--target",
        default=".",
        type=Path,
        help="Target project root. Defaults to the current directory.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing target files.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    target = args.target.resolve()
    if not target.exists():
        raise SystemExit(f"Target directory not found: {target}")
    if not target.is_dir():
        raise SystemExit(f"Target is not a directory: {target}")

    operations = [workflow_operation(args.kind, target)]

    if args.kind == "docker":
        operations.extend(docker_operations(target))

    copy_operations(operations, args.force)


if __name__ == "__main__":
    main()
