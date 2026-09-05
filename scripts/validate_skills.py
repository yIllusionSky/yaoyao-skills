"""Validate skill structure and run deterministic smoke tests."""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_PATTERN = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
USES_PATTERN = re.compile(
    r"^\s*(?:-\s*)?uses:\s*([^@\s]+)@([^\s#]+)(?:\s+#\s*(\S+))?",
    re.MULTILINE,
)

ACTION_PINS = {
    "Swatinem/rust-cache": ("6323deb102c322ba6fcbdcafc7e3dddab59af2b6", "v2.9.2"),
    "actions/checkout": ("3d3c42e5aac5ba805825da76410c181273ba90b1", "v7.0.1"),
    "actions/setup-go": ("924ae3a1cded613372ab5595356fb5720e22ba16", "v6.5.0"),
    "docker/build-push-action": ("53b7df96c91f9c12dcc8a07bcb9ccacbed38856a", "v7.3.0"),
    "docker/setup-buildx-action": ("bb05f3f5519dd87d3ba754cc423b652a5edd6d2c", "v4.2.0"),
    "dtolnay/rust-toolchain": ("4be7066ada62dd38de10e7b70166bc74ed198c30", "stable"),
    "oven-sh/setup-bun": ("0c5077e51419868618aeaa5fe8019c62421857d6", "v2.2.0"),
    "softprops/action-gh-release": ("3d0d9888cb7fd7b750713d6e236d1fcb99157228", "v3.0.2"),
    "taiki-e/upload-rust-binary-action": (
        "f0d45ae91ee7b8ee928de7a9d04d893a08bcbec6",
        "v1.30.2",
    ),
    "tauri-apps/tauri-action": ("1deb371b0cd8bd54025b384f1cd735e725c4060f", "v1.0.0"),
}


def fail(message: str) -> None:
    raise AssertionError(message)


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        fail(f"missing frontmatter: {path}")
    try:
        raw, _ = text[4:].split("\n---\n", 1)
    except ValueError as error:
        raise AssertionError(f"unterminated frontmatter: {path}") from error

    values: dict[str, str] = {}
    for line in raw.splitlines():
        key, separator, value = line.partition(":")
        if not separator:
            fail(f"invalid frontmatter line in {path}: {line}")
        values[key.strip()] = value.strip().strip('"')
    return values


def validate_skills() -> None:
    skill_files = sorted(SKILLS.glob("*/SKILL.md"))
    if not skill_files:
        fail("no skills found")

    for skill_file in skill_files:
        metadata = parse_frontmatter(skill_file)
        if set(metadata) != {"name", "description"}:
            fail(f"frontmatter must contain only name and description: {skill_file}")
        name = metadata["name"]
        if not NAME_PATTERN.fullmatch(name):
            fail(f"invalid skill name: {name}")
        if skill_file.parent.name != name:
            fail(f"skill folder does not match name: {skill_file}")
        if not metadata["description"]:
            fail(f"empty skill description: {skill_file}")
        if len(skill_file.read_text(encoding="utf-8").splitlines()) >= 500:
            fail(f"SKILL.md must stay below 500 lines: {skill_file}")

        agent_file = skill_file.parent / "agents" / "openai.yaml"
        if not agent_file.is_file():
            fail(f"missing agents/openai.yaml: {skill_file.parent}")
        agent = agent_file.read_text(encoding="utf-8")
        for field in ("display_name:", "short_description:", "default_prompt:"):
            if field not in agent:
                fail(f"missing {field} in {agent_file}")
        if f"${name}" not in agent:
            fail(f"default_prompt must mention ${name}: {agent_file}")
        if name == "project-workflow":
            policy = re.search(r"(?m)^policy:\n((?:[ \t]+[^\n]*\n?)*)", agent)
            if policy is None or not re.search(
                r"(?m)^  allow_implicit_invocation: false[ \t]*$", policy.group(1),
            ):
                fail("project-workflow must require explicit invocation")


def validate_links() -> None:
    for markdown in sorted(ROOT.rglob("*.md")):
        for link in LINK_PATTERN.findall(markdown.read_text(encoding="utf-8")):
            if link.startswith(("http://", "https://", "#", "mailto:")):
                continue
            target = (markdown.parent / link.split("#", 1)[0]).resolve()
            if not target.exists():
                fail(f"broken link in {markdown}: {link}")


def validate_action_pins() -> None:
    workflow_files = [
        *sorted((ROOT / ".github" / "workflows").glob("*.yml")),
        *sorted((SKILLS / "github-actions" / "assets").rglob("*.yml")),
    ]
    for workflow in workflow_files:
        text = workflow.read_text(encoding="utf-8")
        for owner, reference, annotation in USES_PATTERN.findall(text):
            if owner.startswith("./"):
                continue
            if not re.fullmatch(r"[0-9a-f]{40}", reference):
                fail(f"action is not pinned to a full SHA in {workflow}: {owner}@{reference}")
            expected = ACTION_PINS.get(owner)
            if expected is None:
                fail(f"action pin has not been audited in {workflow}: {owner}")
            if (reference, annotation) != expected:
                fail(
                    f"action pin or annotation does not match audited commit in {workflow}: "
                    f"{owner}@{reference} # {annotation}",
                )


def validate_release_lifecycle() -> None:
    release_workflows = (
        SKILLS / "github-actions" / "assets" / "app-release.yml",
        SKILLS / "github-actions" / "assets" / "tauri-release.yml",
        SKILLS / "github-actions" / "assets" / "monorepo" / "workflows" / "release.yml",
    )
    for workflow in release_workflows:
        text = workflow.read_text(encoding="utf-8")
        if "draft: true" not in text:
            fail(f"release must be created as a draft: {workflow}")
        if 'gh release edit "$GITHUB_REF_NAME" --draft=false' not in text:
            fail(f"release is not published after assets succeed: {workflow}")


def write(path: Path, content: str = "placeholder\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def run_copy(*args: str, expect_success: bool = True) -> subprocess.CompletedProcess[str]:
    script = SKILLS / "github-actions" / "scripts" / "copy_assets.py"
    result = subprocess.run(
        [sys.executable, str(script), *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if expect_success and result.returncode != 0:
        fail(f"copy_assets failed: {result.stderr or result.stdout}")
    if not expect_success and result.returncode == 0:
        fail("copy_assets unexpectedly succeeded")
    return result


MONOREPO_PACKAGE = (
    '{"private":true,"packageManager":"bun@1.3.14",'
    '"workspaces":["apps/*/*","packages/*"],'
    '"scripts":{"lint":"bun --version","typecheck":"bun --version",'
    '"test":"bun --version","build":"bun --version"}}\n'
)


def write_monorepo(root: Path, package: str = MONOREPO_PACKAGE) -> None:
    write(
        root / "Cargo.toml",
        '[workspace]\nmembers = ["apps/learning/api"]\nresolver = "3"\n',
    )
    write(root / "Cargo.lock")
    write(
        root / "apps/learning/api/Cargo.toml",
        '[package]\nname = "learning-api"\nversion = "0.1.0"\nedition = "2024"\n',
    )
    write(root / "package.json", package)
    write(root / "bun.lock")
    write(
        root / "apps/learning/web/package.json",
        '{"name":"learning-web","version":"0.1.0",'
        '"scripts":{"build":"bun build ./src/index.ts --outdir ./dist",'
        '"start":"bun ./dist/index.js"}}\n',
    )
    write(
        root / "packages/shared/package.json",
        '{"name":"@example/shared","version":"0.1.0"}\n',
    )
    write(root / "CHANGELOG.md", "# Changelog\n\n## [0.1.0] - 2026-08-26\n")


def assert_no_github(root: Path, message: str) -> None:
    if (root / ".github").exists():
        fail(message)


def assert_no_monorepo_release(root: Path, message: str) -> None:
    generated = (
        root / ".github",
        root / "deploy",
        root / "docker-compose.yaml",
        root / "pingap",
        root / ".env.example",
    )
    if any(path.exists() for path in generated):
        fail(message)


def validate_copy_assets() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)

        ci = root / "ci"
        write(ci / "Cargo.toml")
        run_copy("ci", "--target", str(ci))
        if not (ci / ".github/workflows/ci.yml").is_file():
            fail("ci workflow was not copied")
        run_copy("ci", "--target", str(ci), expect_success=False)
        (ci / ".github/workflows/ci.yml").write_text("stale\n", encoding="utf-8")
        run_copy("ci", "--target", str(ci), "--force")
        if (ci / ".github/workflows/ci.yml").read_text(encoding="utf-8") == "stale\n":
            fail("--force did not replace an existing asset")

        monorepo = root / "monorepo"
        write_monorepo(monorepo)
        existing_toolchain = '[toolchain]\nchannel = "1.86.0"\n'
        write(monorepo / "rust-toolchain.toml", existing_toolchain)
        run_copy("monorepo-ci", "--target", str(monorepo))
        if (monorepo / "rust-toolchain.toml").read_text() != existing_toolchain:
            fail("copying CI changed the project's existing toolchain configuration")
        monorepo_workflow = (
            monorepo / ".github/workflows/monorepo-ci.yml"
        ).read_text(encoding="utf-8")
        if "toolchain: stable" not in monorepo_workflow:
            fail("monorepo CI did not use the default Rust toolchain")
        if "rust-toolchain.toml" in monorepo_workflow or "bun ci" not in monorepo_workflow:
            fail("monorepo CI asset was not fully rendered")
        run_copy("monorepo-ci", "--target", str(monorepo), expect_success=False)
        (monorepo / ".github/workflows/monorepo-ci.yml").write_text(
            "stale\n",
            encoding="utf-8",
        )
        run_copy("monorepo-ci", "--target", str(monorepo), "--force")
        if (
            monorepo / ".github/workflows/monorepo-ci.yml"
        ).read_text(encoding="utf-8") == "stale\n":
            fail("monorepo CI --force did not replace an existing asset")

        removed_toolchain_option = root / "monorepo-removed-toolchain-option"
        write_monorepo(removed_toolchain_option)
        run_copy(
            "monorepo-ci",
            "--target",
            str(removed_toolchain_option),
            "--rust-toolchain",
            "stable",
            expect_success=False,
        )
        assert_no_github(
            removed_toolchain_option,
            "removed Rust toolchain option produced monorepo CI output",
        )

        release = root / "monorepo-release"
        write_monorepo(release)
        run_copy(
            "monorepo-release",
            "--target", str(release),
            "--rust-package", "learning-api",
            "--rust-bin", "learning-api",
            "--typescript-package", "learning-web",
            "--typescript-app", "apps/learning/web",
        )
        release_outputs = (
            release / ".github/workflows/monorepo-release.yml",
            release / "deploy/docker/rust.Dockerfile",
            release / "deploy/docker/rust.Dockerfile.dockerignore",
            release / "deploy/docker/typescript.Dockerfile",
            release / "deploy/docker/typescript.Dockerfile.dockerignore",
            release / "deploy/docker/npmrc.example",
            release / "deploy/docker-compose.release.yaml",
            release / "docker-compose.yaml",
            release / "pingap/conf/example.conf",
            release / ".env.example",
        )
        if not all(path.is_file() for path in release_outputs):
            fail("monorepo release assets were not all copied")
        rendered = "\n".join(path.read_text(encoding="utf-8") for path in release_outputs)
        for placeholder in (
            "__RUST_PACKAGE__",
            "__RUST_BIN__",
            "__TYPESCRIPT_PACKAGE__",
            "__TYPESCRIPT_APP__",
            "__BUN_VERSION__",
        ):
            if placeholder in rendered:
                fail(f"monorepo release placeholder was not replaced: {placeholder}")
        if "oven/bun:1.3.14" not in rendered or "toolchain: stable" not in rendered:
            fail("monorepo release did not pin its CI and container toolchains")
        release_workflow = (
            release / ".github/workflows/monorepo-release.yml"
        ).read_text(encoding="utf-8")
        if (
            "scope=monorepo-rust" not in release_workflow
            or "scope=monorepo-typescript" not in release_workflow
        ):
            fail("monorepo release must keep Rust and TypeScript build caches separate")
        if "npmrc=${{ secrets.NPMRC }}" not in release_workflow:
            fail("monorepo TypeScript build does not mount the optional npmrc secret")
        if "release/deploy/.env\n" not in release_workflow:
            fail("monorepo release package is missing a Compose-ready .env")
        rust_dockerfile = (
            release / "deploy/docker/rust.Dockerfile"
        ).read_text(encoding="utf-8")
        if '--package "$RUST_PACKAGE" --bin "$RUST_BIN"' not in rust_dockerfile:
            fail("cargo-chef cache is not scoped to the selected Rust target")
        typescript_dockerfile = (
            release / "deploy/docker/typescript.Dockerfile"
        ).read_text(encoding="utf-8")
        dependency_markers = (
            "COPY bun.lock bunfig.tom[l] ./",
            "COPY --parents ./**/package.json ./",
            'bun ci --filter "$TYPESCRIPT_PACKAGE" --ignore-scripts',
            "COPY . .",
            'bun ci --filter "$TYPESCRIPT_PACKAGE"\n',
        )
        try:
            dependency_positions = [
                typescript_dockerfile.index(marker) for marker in dependency_markers
            ]
        except ValueError as error:
            fail(f"TypeScript dependency cache layer is incomplete: {error}")
        if dependency_positions != sorted(dependency_positions):
            fail("TypeScript source is copied before its reusable dependency layer")
        if typescript_dockerfile.count("id=npmrc") != 2:
            fail("TypeScript installs do not use optional BuildKit npmrc secrets")
        if "apps/learning/web/package.json" in typescript_dockerfile:
            fail("TypeScript Dockerfile froze the workspace inventory at copy time")
        if (
            "COPY --from=builder /app /app" in typescript_dockerfile
            or "/app/${TYPESCRIPT_APP}/dist ./dist" not in typescript_dockerfile
        ):
            fail("TypeScript runtime image contains the builder workspace")
        for name in (
            "rust.Dockerfile.dockerignore",
            "typescript.Dockerfile.dockerignore",
        ):
            dockerignore = (release / "deploy/docker" / name).read_text(encoding="utf-8")
            for pattern in (
                ".env",
                ".env.*",
                ".npmrc",
                "*.key",
                "*.pem",
                "*.p12",
                "*.crt",
            ):
                if pattern not in dockerignore.splitlines():
                    fail(f"monorepo Docker context does not exclude {pattern}: {name}")
        compose = (release / "docker-compose.yaml").read_text(encoding="utf-8")
        if compose.count("ports:") != 1 or compose.count("expose:") != 2:
            fail("monorepo compose must expose only Pingap publicly")
        if '"443:443"' in compose:
            fail("monorepo compose unexpectedly configures TLS")
        if "secrets:\n  npmrc:" not in compose or "file: ${NPMRC_PATH}" not in compose:
            fail("monorepo Compose does not provide the npmrc build secret")
        env_example = (release / ".env.example").read_text(encoding="utf-8")
        if "NPMRC_PATH=deploy/docker/npmrc.example" not in env_example:
            fail("monorepo environment example does not configure the npmrc placeholder")
        release_compose = (
            release / "deploy/docker-compose.release.yaml"
        ).read_text(encoding="utf-8")
        if "build:" in release_compose:
            fail("monorepo release compose must not depend on source builds")
        pingap = (release / "pingap/conf/example.conf").read_text(encoding="utf-8")
        if 'path = "/api"' not in pingap or 'path = "/"' not in pingap:
            fail("monorepo Pingap routes are incomplete")
        run_copy(
            "monorepo-release",
            "--target", str(release),
            "--rust-package", "learning-api",
            "--rust-bin", "learning-api",
            "--typescript-package", "learning-web",
            "--typescript-app", "apps/learning/web",
            expect_success=False,
        )

        invalid_app = root / "monorepo-invalid-app"
        write_monorepo(invalid_app)
        run_copy(
            "monorepo-release",
            "--target", str(invalid_app),
            "--rust-package", "learning-api",
            "--rust-bin", "learning-api",
            "--typescript-package", "learning-web",
            "--typescript-app", "../outside",
            expect_success=False,
        )
        assert_no_monorepo_release(
            invalid_app,
            "invalid TypeScript app path produced partial monorepo release output",
        )

        non_workspace_app = root / "monorepo-non-workspace-app"
        write_monorepo(
            non_workspace_app,
            MONOREPO_PACKAGE.replace(
                '"workspaces":["apps/*/*","packages/*"]',
                '"workspaces":["packages/*"]',
            ),
        )
        run_copy(
            "monorepo-release",
            "--target", str(non_workspace_app),
            "--rust-package", "learning-api",
            "--rust-bin", "learning-api",
            "--typescript-package", "learning-web",
            "--typescript-app", "apps/learning/web",
            expect_success=False,
        )
        assert_no_monorepo_release(
            non_workspace_app,
            "TypeScript app outside root workspaces produced release output",
        )

        excluded_workspace_app = root / "monorepo-excluded-workspace-app"
        write_monorepo(
            excluded_workspace_app,
            MONOREPO_PACKAGE.replace(
                '"workspaces":["apps/*/*","packages/*"]',
                '"workspaces":["apps/*/*","!apps/learning/*","packages/*"]',
            ),
        )
        run_copy(
            "monorepo-release",
            "--target", str(excluded_workspace_app),
            "--rust-package", "learning-api",
            "--rust-bin", "learning-api",
            "--typescript-package", "learning-web",
            "--typescript-app", "apps/learning/web",
            expect_success=False,
        )
        assert_no_monorepo_release(
            excluded_workspace_app,
            "excluded TypeScript workspace produced release output",
        )

        compatible_workspace_patterns = {
            "recursive-workspace": '["apps/**","packages/*"]',
            "brace-workspace": '["{apps,packages}/**"]',
        }
        for name, workspaces in compatible_workspace_patterns.items():
            compatible = root / name
            write_monorepo(
                compatible,
                MONOREPO_PACKAGE.replace(
                    '["apps/*/*","packages/*"]',
                    workspaces,
                ),
            )
            run_copy(
                "monorepo-release",
                "--target", str(compatible),
                "--rust-package", "learning-api",
                "--rust-bin", "learning-api",
                "--typescript-package", "learning-web",
                "--typescript-app", "apps/learning/web",
            )
            if not (compatible / "deploy/docker/typescript.Dockerfile").is_file():
                fail(f"valid Bun {name} glob did not produce release output")

        invalid_monorepos = {
            "cargo-package": (
                '[package]\nname = "demo"\nversion = "0.1.0"\n',
                MONOREPO_PACKAGE,
                True,
            ),
            "missing-workspaces": (
                '[workspace]\nmembers = []\n',
                MONOREPO_PACKAGE.replace(
                    ',"workspaces":["apps/*/*","packages/*"]',
                    "",
                ),
                True,
            ),
            "missing-package-manager": (
                '[workspace]\nmembers = []\n',
                MONOREPO_PACKAGE.replace(',"packageManager":"bun@1.3.14"', ""),
                True,
            ),
            "non-private-package": (
                '[workspace]\nmembers = []\n',
                MONOREPO_PACKAGE.replace('"private":true', '"private":false'),
                True,
            ),
            "ranged-bun-version": (
                '[workspace]\nmembers = []\n',
                MONOREPO_PACKAGE.replace("bun@1.3.14", "bun@^1.3.14"),
                True,
            ),
            "build-metadata-bun-version": (
                '[workspace]\nmembers = []\n',
                MONOREPO_PACKAGE.replace("bun@1.3.14", "bun@1.3.14+local"),
                True,
            ),
            "missing-script": (
                '[workspace]\nmembers = []\n',
                MONOREPO_PACKAGE.replace(',"build":"bun --version"', ""),
                True,
            ),
            "missing-lock": (
                '[workspace]\nmembers = []\n',
                MONOREPO_PACKAGE,
                False,
            ),
        }
        for name, (cargo, package, has_lock) in invalid_monorepos.items():
            invalid = root / name
            write(invalid / "Cargo.toml", cargo)
            write(invalid / "package.json", package)
            if has_lock:
                write(invalid / "bun.lock")
            run_copy("monorepo-ci", "--target", str(invalid), expect_success=False)
            assert_no_github(invalid, f"invalid monorepo produced output: {name}")

        app = root / "app"
        write(app / "Cargo.toml")
        run_copy("app", "--target", str(app), "--app-bin", "demo")
        app_workflow = (app / ".github/workflows/app-release.yml").read_text(encoding="utf-8")
        if "APP_NAME: demo" not in app_workflow or "__APP_BIN__" in app_workflow:
            fail("app workflow placeholder was not replaced")

        tauri = root / "tauri"
        write(
            tauri / "package.json",
            '{"devDependencies":{"@tauri-apps/cli":"^2.0.0"}}\n',
        )
        write(tauri / "bun.lock")
        write(
            tauri / "src-tauri/Cargo.toml",
            '[package]\nname = "demo"\nversion = "0.1.0"\n\n'
            '[dependencies]\ntauri = "2"\n',
        )
        run_copy("tauri", "--target", str(tauri))

        server = root / "server-only"
        write(
            server / "server/Cargo.toml",
            '[package]\nname = "api"\nversion = "0.1.0"\n',
        )
        write(server / "server/Cargo.lock")
        run_copy("docker", "--target", str(server), "--server-bin", "api")
        server_compose = (server / "docker-compose.yaml").read_text(encoding="utf-8")
        if "  client:" in server_compose or (server / "client/Dockerfile").exists():
            fail("server-only overlay unexpectedly contains client assets")
        if "__SERVER_BIN__" in (server / "server/Dockerfile").read_text(encoding="utf-8"):
            fail("server binary placeholder was not replaced")
        if not (server / "server/.dockerignore").is_file():
            fail("server Docker overlay is missing .dockerignore")
        server_env = (server / ".env.example").read_text(encoding="utf-8")
        if "SERVER_BIN=api" not in server_env or "__SERVER_BIN__" in server_env:
            fail("server binary was not written to .env.example")

        fullstack = root / "fullstack"
        write(
            fullstack / "server/Cargo.toml",
            '[package]\nname = "api"\nversion = "0.1.0"\n',
        )
        write(fullstack / "server/Cargo.lock")
        write(
            fullstack / "client/package.json",
            '{"name":"client","version":"0.1.0","scripts":{"build":"vite build"},'
            '"devDependencies":{"@sveltejs/adapter-node":"^5.0.0"}}\n',
        )
        write(fullstack / "client/bun.lock")
        run_copy(
            "docker",
            "--target",
            str(fullstack),
            "--server-bin",
            "api",
            "--with-client",
        )
        if not (fullstack / "client/Dockerfile").is_file():
            fail("fullstack overlay is missing client Dockerfile")
        if not (fullstack / "client/.dockerignore").is_file():
            fail("fullstack Docker overlay is missing client .dockerignore")

        invalid_bin = root / "invalid-bin"
        write(invalid_bin / "Cargo.toml")
        run_copy(
            "app",
            "--target",
            str(invalid_bin),
            "--app-bin",
            "bad\nname",
            expect_success=False,
        )
        if (invalid_bin / ".github").exists():
            fail("invalid binary name produced partial output")

        tauri_one = root / "tauri-one"
        write(
            tauri_one / "package.json",
            '{"devDependencies":{"@tauri-apps/cli":"^1.0.0"}}\n',
        )
        write(tauri_one / "bun.lock")
        write(
            tauri_one / "src-tauri/Cargo.toml",
            '[package]\nname = "demo"\nversion = "0.1.0"\n\n'
            '[dependencies]\ntauri = "1"\n',
        )
        run_copy("tauri", "--target", str(tauri_one), expect_success=False)
        if (tauri_one / ".github").exists():
            fail("unsupported Tauri version produced partial output")

        workspace_server = root / "workspace-server"
        write(
            workspace_server / "server/Cargo.toml",
            '[package]\nname = "api"\nversion.workspace = true\n',
        )
        write(workspace_server / "server/Cargo.lock")
        run_copy(
            "docker",
            "--target",
            str(workspace_server),
            "--server-bin",
            "api",
            expect_success=False,
        )
        if (workspace_server / ".github").exists():
            fail("workspace-inherited server produced partial output")

        unsupported_client = root / "unsupported-client"
        write(
            unsupported_client / "server/Cargo.toml",
            '[package]\nname = "api"\nversion = "0.1.0"\n',
        )
        write(unsupported_client / "server/Cargo.lock")
        write(
            unsupported_client / "client/package.json",
            '{"scripts":{"build":"vite build"}}\n',
        )
        write(unsupported_client / "client/bun.lock")
        run_copy(
            "docker",
            "--target",
            str(unsupported_client),
            "--server-bin",
            "api",
            "--with-client",
            expect_success=False,
        )
        if (unsupported_client / ".github").exists():
            fail("unsupported client produced partial output")

        symlink_target = root / "symlink-target"
        symlink_destination = root / "symlink-destination"
        symlink_target.mkdir()
        symlink_destination.mkdir()
        write(symlink_target / "Cargo.toml")
        (symlink_target / ".github").symlink_to(symlink_destination, target_is_directory=True)
        run_copy(
            "app",
            "--target",
            str(symlink_target),
            "--app-bin",
            "demo",
            expect_success=False,
        )
        if (symlink_destination / "workflows/app-release.yml").exists():
            fail("symbolic link allowed copy outside the target")

        missing = root / "missing"
        missing.mkdir()
        run_copy("app", "--target", str(missing), "--app-bin", "demo", expect_success=False)
        if (missing / ".github").exists():
            fail("failed validation produced partial output")


def git(repository: Path, *args: str, expect_success: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", "-C", str(repository), *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if expect_success and result.returncode != 0:
        fail(f"git {' '.join(args)} failed: {result.stderr or result.stdout}")
    if not expect_success and result.returncode == 0:
        fail(f"git {' '.join(args)} unexpectedly succeeded")
    return result


def initialize_repository(repository: Path) -> None:
    repository.mkdir()
    git(repository, "init", "--initial-branch=main")
    git(repository, "config", "user.name", "Skill Validator")
    git(repository, "config", "user.email", "validator@example.invalid")
    write(repository / "README.md", "fixture\n")
    git(repository, "add", "README.md")
    git(repository, "commit", "-m", "initial")


def commit_files(repository: Path, message: str, *paths: str) -> str:
    git(repository, "add", "--", *paths)
    git(repository, "commit", "-m", message)
    return git(repository, "rev-parse", "HEAD").stdout.strip()


def validate_git_protocols() -> None:
    """Exercise Git behavior used by the prompts, not model instruction following."""
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)

        project = root / "project"
        integration = root / "project-develop"
        project_worktree = root / "project-app"
        initialize_repository(project)
        git(project, "worktree", "add", "--detach", str(integration), "main")
        git(integration, "switch", "-c", "task-a")

        write(integration / ".gitignore", ".skills\n")
        git(integration, "add", ".gitignore")
        git(integration, "commit", "-m", "prepare task a")
        git(integration, "worktree", "add", "--detach", str(project_worktree), "task-a")
        write(project_worktree / ".skills", "project-docs\n")
        if git(project_worktree, "status", "--porcelain").stdout:
            fail("project-workflow .skills file is not ignored")

        git(project_worktree, "switch", "-c", "workflow/task-a/app")
        write(project_worktree / "apps/app.txt")
        git(project_worktree, "add", "apps/app.txt")
        git(project_worktree, "commit", "-m", "implement app")
        git(integration, "merge", "workflow/task-a/app")

        write(integration / "root.txt")
        git(integration, "add", "root.txt")
        git(integration, "commit", "-m", "integrate task a")
        git(project_worktree, "merge-base", "--is-ancestor", "HEAD", "task-a")
        git(project_worktree, "merge", "--ff-only", "task-a")
        git(project_worktree, "merge-base", "--is-ancestor", "task-a", "HEAD")

        write(project_worktree / "apps/fix.txt")
        git(project_worktree, "add", "apps/fix.txt")
        git(project_worktree, "commit", "-m", "fix app review")
        git(integration, "merge", "workflow/task-a/app")

        git(project, "merge", "--no-ff", "task-a", "-m", "merge task a")
        git(project, "merge-base", "--is-ancestor", "task-a", "main")

        git(integration, "switch", "--detach", "main")
        git(integration, "switch", "-c", "task-b")
        git(integration, "merge-base", "--is-ancestor", "task-a", "task-b")


def validate_parallel_worktrees() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        project, integration = root / "main", root / "develop"
        agent_a, agent_b = root / "apps-a", root / "apps-b"
        initialize_repository(project)
        git(project, "worktree", "add", "--detach", str(integration), "main")
        git(integration, "switch", "-c", "task-a")
        write(integration / "Cargo.lock", "baseline Rust resolution\n")
        write(integration / "bun.lock", "baseline Bun resolution\n")
        base = commit_files(integration, "prepare task", "Cargo.lock", "bun.lock")

        for worktree, name in ((agent_a, "a"), (agent_b, "b")):
            record = f".workflow/task-a/apps-{name}/task.md"
            write(integration / record, f"Status: in-progress\nBase Commit: {base}\n")
            commit_files(integration, f"dispatch {name}", record)
            git(integration, "worktree", "add", "--detach", str(worktree), "task-a")
            git(worktree, "switch", "-c", f"workflow/task-a/apps-{name}")
            write(worktree / f"apps/{name}/source.txt", f"implement {name}\n")
            # Simulate installation output; package-manager resolution is not under test.
            write(worktree / "Cargo.lock", f"local Rust resolution {name}\n")
            write(worktree / "bun.lock", f"local Bun resolution {name}\n")
            commit_files(worktree, f"implement {name}", f"apps/{name}/source.txt")
            changed = set(git(worktree, "diff", "--name-only", base, "HEAD").stdout.splitlines())
            if changed & {"Cargo.lock", "bun.lock"}:
                fail("project commit includes locally generated root lockfiles")

        git(integration, "merge", "--no-edit", "workflow/task-a/apps-a")
        write(integration / "root.txt", "integrated a\n")
        commit_files(integration, "integrate a", "root.txt")

        # B has legitimate unmerged commits while the integration branch moves ahead.
        git(agent_b, "merge-base", "--is-ancestor", "task-a", "HEAD", expect_success=False)
        git(agent_b, "merge-base", "--is-ancestor", "HEAD", "task-a", expect_success=False)
        git(agent_b, "merge-base", "--is-ancestor", base, "HEAD")
        write(agent_b / "apps/b/source.txt", "finish interrupted b\n")
        commit_files(agent_b, "resume b", "apps/b/source.txt")
        git(integration, "merge", "--no-edit", "workflow/task-a/apps-b")
        if git(integration, "status", "--porcelain").stdout:
            fail("local changes in project worktrees leaked into integration")

        for name in ("a", "b"):
            if not (integration / f"apps/{name}/source.txt").is_file():
                fail(f"parallel project {name} was not integrated")
        write(integration / "Cargo.lock", "combined Rust resolution\n")
        write(integration / "bun.lock", "combined Bun resolution\n")
        sync_base = commit_files(integration, "integrate dependencies", "Cargo.lock", "bun.lock")
        record = ".workflow/task-a/apps-b/task.md"
        write(integration / record, f"Status: in-progress\nBase Commit: {sync_base}\n")
        commit_files(integration, "dispatch review fix", record)

        # Local generated locks may block a later sync, not merging into develop.
        write(agent_b / "unrelated-notes.txt", "preserve this work\n")
        git(agent_b, "merge", "--ff-only", "task-a", expect_success=False)
        git(agent_b, "restore", "--source=HEAD", "--", "Cargo.lock", "bun.lock")
        git(agent_b, "merge", "--ff-only", "task-a")
        git(agent_b, "merge-base", "--is-ancestor", sync_base, "HEAD")
        if (agent_b / "unrelated-notes.txt").read_text() != "preserve this work\n":
            fail("lockfile synchronization discarded unrelated work")
        if (agent_b / "apps/b/source.txt").read_text() != "finish interrupted b\n":
            fail("baseline synchronization lost the resumed implementation")
        if (agent_a / "Cargo.lock").read_text() != "local Rust resolution a\n":
            fail("synchronization changed another project's local lockfile")


def validate_review_snapshots() -> None:
    with tempfile.TemporaryDirectory() as directory:
        repository = Path(directory) / "project"
        initialize_repository(repository)
        write(repository / "root.conf", "old configuration\n")
        task = ".workflow/task-a/task.md"
        log = ".workflow/task-a/log.md"
        write(repository / task, "Status: in-progress\n")
        base = commit_files(repository, "baseline", "root.conf", task)
        git(repository, "switch", "-c", "task-a")
        write(repository / "source.txt", "implemented\n")
        incomplete = commit_files(repository, "implementation", "source.txt")
        write(repository / "root.conf", "integrated configuration\n")
        write(repository / "operations.md", "integrated documentation\n")
        committed_paths = set(git(repository, "diff", "--name-only", base, incomplete).stdout.splitlines())
        if committed_paths != {"source.txt"} or not git(repository, "status", "--porcelain").stdout:
            fail("review fixture must expose changes omitted by a commit-only diff")

        reviewed = commit_files(repository, "prepare review", "root.conf", "operations.md")
        if git(repository, "status", "--porcelain").stdout:
            fail("review candidate is not clean")
        git(repository, "merge-base", "--is-ancestor", base, reviewed)
        reviewed_paths = set(git(repository, "diff", "--name-only", base, reviewed).stdout.splitlines())
        if reviewed_paths != {"source.txt", "root.conf", "operations.md"}:
            fail("review candidate does not include all integration changes")
        snapshot = git(repository, "diff", base, reviewed).stdout

        write(repository / task, "Status: completed\n")
        write(repository / log, f"Base Commit: {base}\nReviewed Commit: {reviewed}\nStatus: passed\n")
        commit_files(repository, "record review result", task, log)
        after_review = set(git(repository, "diff", "--name-only", reviewed, "HEAD").stdout.splitlines())
        if after_review != {task, log}:
            fail("record-only completion unexpectedly changes implementation")
        if git(repository, "diff", base, reviewed).stdout != snapshot:
            fail("completion metadata changed the recorded review snapshot")

        # A code change under the same task branch is a new review candidate.
        write(repository / "source.txt", "changed after review\n")
        commit_files(repository, "change after review", "source.txt")
        if "source.txt" not in git(repository, "diff", "--name-only", reviewed, "HEAD").stdout.splitlines():
            fail("post-review code changes are missing from the completion diff")

        # A moving main ref must not silently change the scope of a previous review.
        git(repository, "switch", "main")
        write(repository / "README.md", "advanced main\n")
        new_base = commit_files(repository, "advance main", "README.md")
        if new_base == base or git(repository, "diff", base, reviewed).stdout != snapshot:
            fail("review snapshot is not stable when main advances")
        git(repository, "switch", "task-a")
        git(repository, "merge-base", "--is-ancestor", "main", "HEAD", expect_success=False)
        git(repository, "merge", "--no-edit", "main")
        git(repository, "merge-base", "--is-ancestor", new_base, "HEAD")


def main() -> None:
    validate_skills()
    validate_links()
    validate_action_pins()
    validate_release_lifecycle()
    validate_copy_assets()
    validate_git_protocols()
    validate_parallel_worktrees()
    validate_review_snapshots()
    print("all skill validations passed")


if __name__ == "__main__":
    main()
