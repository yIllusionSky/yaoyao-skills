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
    "ci": ("ci.yml", "ci.yml"),
    "monorepo-ci": ("monorepo/workflows/ci.yml", "monorepo-ci.yml"),
    "monorepo-release": (
        "monorepo/workflows/release.yml",
        "monorepo-release.yml",
    ),
    "app": ("app-release.yml", "app-release.yml"),
    "tauri": ("tauri-release.yml", "tauri-release.yml"),
    "docker": ("docker-release.yml", "docker-release.yml"),
}

BINARY_NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")
EXACT_BUN_PATTERN = re.compile(r"^bun@\d+\.\d+\.\d+$")
TYPESCRIPT_PACKAGE_PATTERN = re.compile(
    r"^(?:@[a-z0-9][a-z0-9._-]*/)?[a-z0-9][a-z0-9._-]*$",
)
MONOREPO_SCRIPTS = ("lint", "typecheck", "test", "build")


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


def require_monorepo(target: Path) -> tuple[str, list[str]]:
    manifest = tomllib.loads((target / "Cargo.toml").read_text(encoding="utf-8"))
    if not isinstance(manifest.get("workspace"), dict):
        raise SystemExit("Cargo.toml must define a workspace")

    package = json.loads((target / "package.json").read_text(encoding="utf-8"))
    if package.get("private") is not True:
        raise SystemExit("package.json must set private to true")
    package_manager = package.get("packageManager")
    if not isinstance(package_manager, str) or not EXACT_BUN_PATTERN.fullmatch(package_manager):
        raise SystemExit("package.json packageManager must use an exact bun@X.Y.Z version")
    workspaces = package.get("workspaces")
    if not isinstance(workspaces, list) or not workspaces or not all(
        isinstance(item, str) and item.strip() for item in workspaces
    ):
        raise SystemExit("package.json must define a non-empty workspaces array")
    scripts = package.get("scripts")
    missing_scripts = [
        name
        for name in MONOREPO_SCRIPTS
        if not isinstance(scripts, dict)
        or not isinstance(scripts.get(name), str)
        or not scripts[name].strip()
    ]
    if missing_scripts:
        raise SystemExit("package.json must define script: " + missing_scripts[0])
    return package_manager.removeprefix("bun@"), workspaces


def require_typescript_package(value: str | None) -> str:
    if not value or not TYPESCRIPT_PACKAGE_PATTERN.fullmatch(value):
        raise SystemExit(
            "--typescript-package must be a lowercase Bun package name: " + repr(value),
        )
    return value


def require_relative_directory(option: str, value: str | None, target: Path) -> str:
    if not value:
        raise SystemExit(f"{option} is required")
    relative = Path(value)
    if relative.is_absolute() or ".." in relative.parts:
        raise SystemExit(f"{option} must stay inside the target repository: {value!r}")
    resolved = (target / relative).resolve()
    if not resolved.is_relative_to(target.resolve()) or not resolved.is_dir():
        raise SystemExit(f"{option} directory not found inside target: {value!r}")
    return relative.as_posix()


def expand_braces(pattern: str) -> list[str]:
    """Expand the comma form of Bun workspace braces, including nested braces."""
    opening = -1
    escaped = False
    for index, character in enumerate(pattern):
        if escaped:
            escaped = False
            continue
        if character == "\\":
            escaped = True
        elif character == "{":
            opening = index
            break
    if opening < 0:
        return [pattern]

    depth = 0
    closing = -1
    for index in range(opening, len(pattern)):
        character = pattern[index]
        if character == "{":
            depth += 1
        elif character == "}":
            depth -= 1
            if depth == 0:
                closing = index
                break
    if closing < 0:
        raise SystemExit("Invalid Bun workspace glob (unclosed brace): " + pattern)

    body = pattern[opening + 1 : closing]
    alternatives: list[str] = []
    start = 0
    depth = 0
    for index, character in enumerate(body):
        if character == "{":
            depth += 1
        elif character == "}":
            depth -= 1
        elif character == "," and depth == 0:
            alternatives.append(body[start:index])
            start = index + 1
    if not alternatives:
        return [pattern]
    alternatives.append(body[start:])

    expanded: list[str] = []
    prefix = pattern[:opening]
    suffix = pattern[closing + 1 :]
    for alternative in alternatives:
        expanded.extend(expand_braces(prefix + alternative + suffix))
    return expanded


def workspace_package_directories(target: Path, workspaces: list[str]) -> set[Path]:
    """Resolve workspace package directories using filesystem-aware glob semantics."""
    included: set[Path] = set()
    excluded: set[Path] = set()
    target_root = target.resolve()

    for raw_pattern in workspaces:
        is_exclusion = raw_pattern.startswith("!")
        pattern = raw_pattern.removeprefix("!").removeprefix("./").rstrip("/")
        pattern_path = Path(pattern)
        if not pattern or pattern_path.is_absolute() or ".." in pattern_path.parts:
            raise SystemExit("Bun workspace glob must stay inside the repository: " + raw_pattern)

        matches = excluded if is_exclusion else included
        for expanded_pattern in expand_braces(pattern):
            try:
                candidates = target.glob(expanded_pattern)
                for candidate in candidates:
                    resolved = candidate.resolve()
                    if (
                        resolved.is_relative_to(target_root)
                        and resolved.is_dir()
                        and (resolved / "package.json").is_file()
                    ):
                        matches.add(resolved)
            except ValueError as error:
                raise SystemExit(
                    f"Invalid Bun workspace glob {raw_pattern!r}: {error}",
                ) from error

    return included - excluded


def require_typescript_app(
    target: Path,
    app: str | None,
    package_name: str,
    workspaces: list[str],
) -> str:
    relative = require_relative_directory("--typescript-app", app, target)
    workspace_directories = workspace_package_directories(target, workspaces)
    if (target / relative).resolve() not in workspace_directories:
        raise SystemExit("TypeScript app is not included in root workspaces: " + relative)
    package_file = target / relative / "package.json"
    if not package_file.is_file():
        raise SystemExit("TypeScript app package.json not found: " + relative)
    package = json.loads(package_file.read_text(encoding="utf-8"))
    if package.get("name") != package_name:
        raise SystemExit("TypeScript app package name does not match --typescript-package")
    scripts = package.get("scripts")
    for name in ("build", "start"):
        if (
            not isinstance(scripts, dict)
            or not isinstance(scripts.get(name), str)
            or not scripts[name].strip()
        ):
            raise SystemExit(f"TypeScript app must define script: {name}")
    return relative


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
    source, destination = WORKFLOWS[kind]
    return Operation(
        ASSETS / source,
        target / ".github" / "workflows" / destination,
        replacements,
    )


def monorepo_release_operations(
    target: Path,
    replacements: dict[str, str],
) -> list[Operation]:
    monorepo = ASSETS / "monorepo"
    docker = monorepo / "docker"
    return [
        workflow_operation("monorepo-release", target, replacements),
        Operation(
            docker / "rust.Dockerfile",
            target / "deploy" / "docker" / "rust.Dockerfile",
            replacements,
        ),
        Operation(
            docker / "rust.Dockerfile.dockerignore",
            target / "deploy" / "docker" / "rust.Dockerfile.dockerignore",
        ),
        Operation(
            docker / "typescript.Dockerfile",
            target / "deploy" / "docker" / "typescript.Dockerfile",
            replacements,
        ),
        Operation(
            docker / "typescript.Dockerfile.dockerignore",
            target / "deploy" / "docker" / "typescript.Dockerfile.dockerignore",
        ),
        Operation(
            docker / "npmrc.example",
            target / "deploy" / "docker" / "npmrc.example",
        ),
        Operation(
            docker / "docker-compose.yaml",
            target / "docker-compose.yaml",
            replacements,
        ),
        Operation(
            docker / "docker-compose.release.yaml",
            target / "deploy" / "docker-compose.release.yaml",
        ),
        Operation(
            docker / "pingap.conf",
            target / "pingap" / "conf" / "example.conf",
        ),
        Operation(
            docker / "env.example",
            target / ".env.example",
            replacements,
        ),
    ]


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
    elif args.kind == "monorepo-ci":
        require_files(target, ["Cargo.toml", "package.json", "bun.lock"])
        require_monorepo(target)
    elif args.kind == "monorepo-release":
        require_files(
            target,
            ["Cargo.toml", "Cargo.lock", "package.json", "bun.lock", "CHANGELOG.md"],
        )
        bun_version, workspaces = require_monorepo(target)
        rust_package = require_binary_name("--rust-package", args.rust_package)
        rust_bin = require_binary_name("--rust-bin", args.rust_bin)
        typescript_package = require_typescript_package(args.typescript_package)
        typescript_app = require_typescript_app(
            target,
            args.typescript_app,
            typescript_package,
            workspaces,
        )
        replacements.update(
            {
                "__RUST_PACKAGE__": rust_package,
                "__RUST_BIN__": rust_bin,
                "__TYPESCRIPT_PACKAGE__": typescript_package,
                "__TYPESCRIPT_APP__": typescript_app,
                "__BUN_VERSION__": bun_version,
            },
        )
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

    if args.kind != "monorepo-release" and (
        args.rust_package
        or args.rust_bin
        or args.typescript_package
        or args.typescript_app
    ):
        raise SystemExit(
            "--rust-package, --rust-bin, --typescript-package and --typescript-app "
            "are only valid for monorepo-release assets",
        )

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

    if args.kind == "monorepo-release":
        operations = monorepo_release_operations(target, replacements)
    else:
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
    parser.add_argument("--rust-package")
    parser.add_argument("--rust-bin")
    parser.add_argument("--typescript-package")
    parser.add_argument("--typescript-app")
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
