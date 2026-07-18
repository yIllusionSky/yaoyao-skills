#!/usr/bin/env python3
"""Copy validated GitHub Actions assets into an existing project."""

from __future__ import annotations

import argparse
import shutil
from dataclasses import dataclass, field
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"


@dataclass(frozen=True)
class Operation:
    src: Path
    dst: Path
    replacements: dict[str, str] = field(default_factory=dict)


WORKFLOWS = {
    "ci": "ci.yml",
    "app": "app-release.yml",
    "tauri": "tauri-release.yml",
    "docker": "docker-release.yml",
}


def require_files(target: Path, paths: list[str]) -> None:
    missing = [path for path in paths if not (target / path).is_file()]
    if missing:
        raise SystemExit("Required target file not found: " + missing[0])


def workflow_operation(
    kind: str,
    target: Path,
    replacements: dict[str, str],
) -> Operation:
    name = WORKFLOWS[kind]
    return Operation(
        ASSETS / name,
        target / ".github" / "workflows" / name,
        replacements,
    )


def docker_operations(
    target: Path,
    server_bin: str,
    with_client: bool,
) -> list[Operation]:
    docker = ASSETS / "docker"
    profile = "fullstack" if with_client else "server"
    operations = [
        Operation(
            docker / "server" / "Dockerfile",
            target / "server" / "Dockerfile",
            {"__SERVER_BIN__": server_bin},
        ),
        Operation(
            docker / "justfile",
            target / "justfile",
            {"__SERVER_BIN__": server_bin},
        ),
        Operation(
            docker / f"docker-compose.{profile}.yaml",
            target / "docker-compose.yaml",
        ),
        Operation(
            docker / "pingap" / "conf" / f"{profile}.conf",
            target / "pingap" / "conf" / "example.conf",
        ),
        Operation(
            docker / f"env.{profile}.example",
            target / ".env.example",
        ),
    ]
    if with_client:
        operations.append(
            Operation(
                docker / "client" / "Dockerfile",
                target / "client" / "Dockerfile",
            ),
        )
    return operations


def build_operations(args: argparse.Namespace, target: Path) -> list[Operation]:
    replacements: dict[str, str] = {}

    if args.kind in {"ci", "app"}:
        require_files(target, ["Cargo.toml"])
    elif args.kind == "tauri":
        require_files(target, ["package.json", "bun.lock", "src-tauri/Cargo.toml"])
    elif args.kind == "docker":
        required = ["server/Cargo.toml"]
        if args.with_client:
            required.extend(["client/package.json", "client/bun.lock"])
        require_files(target, required)

    if args.kind == "app":
        if not args.app_bin:
            raise SystemExit("--app-bin is required for app assets")
        replacements["__APP_BIN__"] = args.app_bin
    elif args.app_bin:
        raise SystemExit("--app-bin is only valid for app assets")

    if args.kind == "docker":
        if not args.server_bin:
            raise SystemExit("--server-bin is required for docker assets")
        replacements.update(
            {
                "__SERVER_BIN__": args.server_bin,
                "__WITH_CLIENT__": "true" if args.with_client else "false",
            },
        )
    elif args.server_bin or args.with_client:
        raise SystemExit("--server-bin and --with-client are only valid for docker assets")

    operations = [workflow_operation(args.kind, target, replacements)]
    if args.kind == "docker":
        operations.extend(
            docker_operations(target, args.server_bin, args.with_client),
        )
    return operations


def validate_operations(operations: list[Operation], force: bool) -> None:
    missing = [operation.src for operation in operations if not operation.src.is_file()]
    if missing:
        raise SystemExit("Asset file not found: " + str(missing[0]))

    conflicts = [operation.dst for operation in operations if operation.dst.exists()]
    if conflicts and not force:
        raise SystemExit(
            "Target already exists: " + str(conflicts[0]) + ". Pass --force to overwrite.",
        )


def copy_operation(operation: Operation) -> None:
    operation.dst.parent.mkdir(parents=True, exist_ok=True)
    if operation.replacements:
        content = operation.src.read_text(encoding="utf-8")
        for old, new in operation.replacements.items():
            content = content.replace(old, new)
        operation.dst.write_text(content, encoding="utf-8")
    else:
        shutil.copy2(operation.src, operation.dst)
    print(f"copied {operation.src.relative_to(ROOT)} -> {operation.dst}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Copy validated GitHub Actions assets into an existing project.",
    )
    parser.add_argument("kind", choices=sorted(WORKFLOWS))
    parser.add_argument("--target", default=".", type=Path)
    parser.add_argument("--app-bin")
    parser.add_argument("--server-bin")
    parser.add_argument("--with-client", action="store_true")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    target = args.target.resolve()
    if not target.is_dir():
        raise SystemExit(f"Target directory not found: {target}")

    operations = build_operations(args, target)
    validate_operations(operations, args.force)
    for operation in operations:
        copy_operation(operation)


if __name__ == "__main__":
    main()
