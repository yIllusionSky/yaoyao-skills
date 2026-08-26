#!/usr/bin/env python3
"""Copy validated GitHub Actions assets into an existing project."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import tomllib
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

BINARY_NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")


def require_files(target: Path, paths: list[str]) -> None:
    missing = [path for path in paths if not (target / path).is_file()]
    if missing:
        raise SystemExit("Required target file not found: " + missing[0])


def require_binary_name(option: str, value: str | None) -> str:
    if not value:
        raise SystemExit(f"{option} is required")
    if not BINARY_NAME_PATTERN.fullmatch(value):
        raise SystemExit(
            f"{option} must contain only ASCII letters, digits, '-' or '_': {value!r}",
        )
    return value


def dependency_major(value: object) -> int | None:
    if isinstance(value, dict):
        value = value.get("version")
    if not isinstance(value, str):
        return None
    match = re.search(r"\d+", value)
    return int(match.group()) if match else None


def require_tauri_two(target: Path) -> None:
    package = json.loads((target / "package.json").read_text(encoding="utf-8"))
    frontend_dependencies = {
        **package.get("dependencies", {}),
        **package.get("devDependencies", {}),
    }
    cli_major = dependency_major(frontend_dependencies.get("@tauri-apps/cli"))

    manifest = tomllib.loads(
        (target / "src-tauri" / "Cargo.toml").read_text(encoding="utf-8"),
    )
    rust_major = dependency_major(manifest.get("dependencies", {}).get("tauri"))
    if cli_major != 2 or rust_major != 2:
        raise SystemExit(
            "tauri assets require @tauri-apps/cli 2 and Rust tauri dependency 2",
        )


def contains_workspace_inheritance(value: object) -> bool:
    if isinstance(value, dict):
        if value.get("workspace") is True:
            return True
        return any(contains_workspace_inheritance(item) for item in value.values())
    if isinstance(value, list):
        return any(contains_workspace_inheritance(item) for item in value)
    return False


def external_paths(value: object, base: Path) -> list[Path]:
    paths: list[Path] = []
    if isinstance(value, dict):
        path = value.get("path")
        if isinstance(path, str):
            resolved = (base / path).resolve()
            if not resolved.is_relative_to(base.resolve()):
                paths.append(resolved)
        for item in value.values():
            paths.extend(external_paths(item, base))
    elif isinstance(value, list):
        for item in value:
            paths.extend(external_paths(item, base))
    return paths


def require_standalone_server(target: Path) -> None:
    server = target / "server"
    manifest = tomllib.loads((server / "Cargo.toml").read_text(encoding="utf-8"))
    if not isinstance(manifest.get("package"), dict):
        raise SystemExit("server/Cargo.toml must define a package")
    if contains_workspace_inheritance(manifest):
        raise SystemExit("server/Cargo.toml must not inherit values from a parent workspace")
    paths = external_paths(manifest, server)
    if paths:
        raise SystemExit(
            "server/Cargo.toml path dependency is outside server/: " + str(paths[0]),
        )


def require_adapter_node_client(target: Path) -> None:
    package = json.loads((target / "client" / "package.json").read_text(encoding="utf-8"))
    build = package.get("scripts", {}).get("build")
    dependencies = {
        **package.get("dependencies", {}),
        **package.get("devDependencies", {}),
    }
    if not isinstance(build, str) or not build.strip():
        raise SystemExit("client/package.json must define a build script")
    if "@sveltejs/adapter-node" not in dependencies:
        raise SystemExit("client must explicitly depend on @sveltejs/adapter-node")


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
            docker / "server" / ".dockerignore",
            target / "server" / ".dockerignore",
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
            {"__SERVER_BIN__": server_bin},
        ),
    ]
    if with_client:
        operations.append(
            Operation(
                docker / "client" / "Dockerfile",
                target / "client" / "Dockerfile",
            ),
        )
        operations.append(
            Operation(
                docker / "client" / ".dockerignore",
                target / "client" / ".dockerignore",
            ),
        )
    return operations


def build_operations(args: argparse.Namespace, target: Path) -> list[Operation]:
    replacements: dict[str, str] = {}

    if args.kind in {"ci", "app"}:
        require_files(target, ["Cargo.toml"])
    elif args.kind == "tauri":
        require_files(target, ["package.json", "bun.lock", "src-tauri/Cargo.toml"])
        require_tauri_two(target)
    elif args.kind == "docker":
        required = ["server/Cargo.toml", "server/Cargo.lock"]
        if args.with_client:
            required.extend(["client/package.json", "client/bun.lock"])
        require_files(target, required)
        require_standalone_server(target)
        if args.with_client:
            require_adapter_node_client(target)

    if args.kind == "app":
        replacements["__APP_BIN__"] = require_binary_name("--app-bin", args.app_bin)
    elif args.app_bin:
        raise SystemExit("--app-bin is only valid for app assets")

    if args.kind == "docker":
        server_bin = require_binary_name("--server-bin", args.server_bin)
        replacements.update(
            {
                "__SERVER_BIN__": server_bin,
                "__WITH_CLIENT__": "true" if args.with_client else "false",
            },
        )
    elif args.server_bin or args.with_client:
        raise SystemExit("--server-bin and --with-client are only valid for docker assets")

    operations = [workflow_operation(args.kind, target, replacements)]
    if args.kind == "docker":
        operations.extend(
            docker_operations(target, server_bin, args.with_client),
        )
    return operations


def validate_operations(target: Path, operations: list[Operation], force: bool) -> None:
    missing = [operation.src for operation in operations if not operation.src.is_file()]
    if missing:
        raise SystemExit("Asset file not found: " + str(missing[0]))

    for operation in operations:
        relative = operation.dst.relative_to(target)
        current = target
        for part in relative.parts:
            current /= part
            if current.is_symlink():
                raise SystemExit("Symbolic link is not allowed in target path: " + str(current))

    conflicts = [
        operation.dst
        for operation in operations
        if operation.dst.exists() or operation.dst.is_symlink()
    ]
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
    validate_operations(target, operations, args.force)
    for operation in operations:
        copy_operation(operation)


if __name__ == "__main__":
    main()
