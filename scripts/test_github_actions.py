"""Exercise the release templates' metadata and publication boundaries offline."""

from __future__ import annotations

import contextlib
import json
import os
import re
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest.mock import patch

ASSETS = Path(__file__).resolve().parents[1] / "skills/github-actions/assets"


def steps(workflow: Path) -> list[str]:
    # Only split the regular step indentation used by these templates; actionlint
    # validates the complete YAML and GitHub expression syntax separately.
    return re.findall(r"(?ms)^      - .*?(?=^      - |^  \S|\Z)", workflow.read_text())


def named_step(workflow: Path, name: str) -> str:
    return next(step for step in steps(workflow) if step.startswith(f"      - name: {name}\n"))


def command(step: str) -> str:
    raw = step.split("        run: ", 1)[1]
    if raw.startswith("|\n"):
        return textwrap.dedent(raw[2:]).rstrip() + "\n"
    return raw.splitlines()[0] + "\n"


class ReleaseTemplates(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.runner = self.root / "runner"
        self.runner.mkdir()
        self.env = {
            "GITHUB_REF_TYPE": "tag",
            "GITHUB_REF_NAME": "v1.2.3",
            "VERSION": "1.2.3",
            "GITHUB_REPOSITORY": "Example/Project",
            "GITHUB_ENV": str(self.runner / "env"),
            "GITHUB_OUTPUT": str(self.runner / "output"),
            "RUNNER_TEMP": str(self.runner),
            "SERVER_BIN": "api",
            "WITH_CLIENT": "false",
            "RUST_PACKAGE": "api",
            "RUST_BIN": "api",
            "TYPESCRIPT_PACKAGE": "web",
            "TYPESCRIPT_APP": "apps/web",
        }
        for app in ("client", "apps/web"):
            (self.root / app).mkdir(parents=True)
            (self.root / app / "package.json").write_text(
                json.dumps({"name": "web", "version": "1.2.3"}),
            )
        self.cargo = {
            "packages": [{
                "name": "api",
                "version": "1.2.3",
                "manifest_path": str(self.root / "server/Cargo.toml"),
            }],
        }
        (self.root / "CHANGELOG.md").write_text(
            "# Changelog\n\n## [1.2.3] - 2026-09-05\n\nRelease notes.\n",
        )

    def metadata(self, monorepo: bool) -> dict:
        workflow = ASSETS / ("monorepo/workflows/release.yml" if monorepo else "docker-release.yml")
        name = "Prepare release metadata" if monorepo else "Resolve image metadata"
        env = {**self.env}
        with (
            contextlib.chdir(self.root),
            patch.dict(os.environ, env, clear=True),
            patch("subprocess.check_output", return_value=json.dumps(self.cargo).encode()),
        ):
            # Execute the trusted template itself so this checks its actual output.
            exec(compile(command(named_step(workflow, name)), str(workflow), "exec"), {})  # noqa: S102
        return json.loads((self.runner / "docker-bake.json").read_text())

    def test_ci_only_checks_main_prs_and_release_only_builds_tags(self) -> None:
        for relative, release in (
            ("ci.yml", False),
            ("monorepo/workflows/ci.yml", False),
            ("app-release.yml", True),
            ("tauri-release.yml", True),
            ("docker-release.yml", True),
            ("monorepo/workflows/release.yml", True),
        ):
            text = (ASSETS / relative).read_text()
            triggers = re.search(r"(?ms)^on:\n(.*?)(?=^\S)", text).group(1)
            events = re.findall(r"(?m)^  (\w+):", triggers)
            with self.subTest(workflow=relative):
                self.assertNotIn("default_branch", text)
                self.assertNotIn("Warm release dependencies", text)
                self.assertNotIn("type=cacheonly", text)
                if release:
                    self.assertEqual(events, ["push"])
                    self.assertNotIn("branches:", triggers)
                    self.assertIn('    tags:\n      - "v*.*.*"', triggers)
                else:
                    self.assertEqual(events, ["pull_request"])
                    self.assertNotIn("tags:", triggers)
                    for event in events:
                        block = re.search(rf"(?ms)^  {event}:\n(.*?)(?=^  \S|\Z)", triggers).group(1)
                        branches = re.findall(r"(?m)^      - (.+)$", block)
                        self.assertIn("    branches:", block)
                        self.assertEqual(branches, ["main"])

    def test_server_only_does_not_access_client(self) -> None:
        (self.root / "client/package.json").unlink()
        bake = self.metadata(False)
        self.assertEqual(bake["group"]["default"]["targets"], ["server"])
        self.assertEqual(bake["target"]["server"]["args"], {"APP_BIN": "api"})

    def test_bake_targets_use_release_tags_and_separate_image_caches(self) -> None:
        self.env["WITH_CLIENT"] = "true"
        for monorepo in (False, True):
            with self.subTest(monorepo=monorepo):
                bake = self.metadata(monorepo)
                self.assertEqual(len(bake["target"]), 2)
                scopes = []
                for target in bake["target"].values():
                    self.assertTrue(target["tags"][0].endswith(":1.2.3"))
                    scopes.append(target["cache-from"])
                self.assertNotEqual(*scopes)
                if monorepo:
                    self.assertEqual(bake["target"]["typescript"]["secret"], ["id=npmrc,env=NPMRC"])

    def test_version_mismatch_stops_metadata_generation(self) -> None:
        self.cargo["packages"][0]["version"] = "9.0.0"
        for monorepo in (False, True):
            with self.subTest(monorepo=monorepo), self.assertRaisesRegex(SystemExit, "version must match"):
                self.metadata(monorepo)
        self.assertFalse((self.runner / "docker-bake.json").exists())

    def test_invalid_tags_and_missing_notes_fail_before_docker_build(self) -> None:
        (self.root / "CHANGELOG.md").unlink()
        workflow = ASSETS / "docker-release.yml"
        script = command(named_step(workflow, "Prepare release metadata"))
        for tag in ("v1.2.3-rc.1", "v1.2.3.extra", "v1.2.3"):
            with self.subTest(tag=tag):
                result = subprocess.run(
                    ["bash", "-e", "-c", script], cwd=self.root,
                    env={**os.environ, **self.env, "GITHUB_REF_NAME": tag},
                    capture_output=True, text=True, check=False,
                )
                self.assertNotEqual(result.returncode, 0)
        for tag in ("v1.2.3-rc.1", "v1.2.3.extra"):
            self.env.update(GITHUB_REF_TYPE="tag", GITHUB_REF_NAME=tag)
            with self.subTest(tag=tag), self.assertRaisesRegex(SystemExit, "Release tag must match"):
                self.metadata(True)

    def test_release_writes_are_tag_guarded_and_require_success(self) -> None:
        workflows = [ASSETS / name for name in (
            "app-release.yml", "tauri-release.yml", "docker-release.yml", "monorepo/workflows/release.yml",
        )]
        for workflow in workflows:
            with self.subTest(workflow=workflow):
                text = workflow.read_text()
                self.assertIn("cancel-in-progress: false", text)
                for step in steps(workflow):
                    if any(action in step for action in (
                        "softprops/action-gh-release@", "taiki-e/upload-rust-binary-action@",
                        "tauri-apps/tauri-action@",
                    )):
                        self.assertIn("if: github.ref_type == 'tag'", step)
                    if "softprops/action-gh-release@" in step:
                        self.assertIn("draft: true", step)
                publish = named_step(workflow, "Publish release")
                self.assertNotIn("always()", text)
                self.assertNotIn("continue-on-error:", text)
                # Guard either the standalone publication job or its inline step.
                guard = "  publish-release:\n    if: github.ref_type == 'tag'"
                self.assertTrue(guard in text or "if: github.ref_type == 'tag'" in publish)
                args = command(publish)
                self.assertIn('--repo "$GITHUB_REPOSITORY"', args)
                self.assertIn("--draft=false", args)

    def test_publish_resolves_repository_without_a_checkout(self) -> None:
        # A shell function records the command; this test never calls GitHub.
        for name in ("app-release.yml", "tauri-release.yml"):
            script = command(named_step(ASSETS / name, "Publish release"))
            result = subprocess.run(
                ["bash", "-e", "-c", 'gh() { printf "%s\\n" "$@"; };\n' + script],
                cwd=self.root, env={**os.environ, **self.env, "GITHUB_REF_NAME": "v1.2.3"},
                capture_output=True, text=True, check=True,
            )
            self.assertEqual(result.stdout.splitlines(), [
                "release", "edit", "v1.2.3", "--repo", "Example/Project", "--draft=false",
            ])

    def test_archive_configuration_uses_release_images_without_source_builds(self) -> None:
        (self.root / ".env.example").write_text(
            "SERVER_IMAGE=app\nSERVER_TAG=0.1.0\nCLIENT_IMAGE=app-client\nCLIENT_TAG=0.1.0\nCUSTOM=keep\n",
        )
        compose = {"services": {
            "server": {"image": "${SERVER_IMAGE}:${SERVER_TAG}", "build": {"context": "./server"}},
            "client": {"image": "${CLIENT_IMAGE}:${CLIENT_TAG}", "build": {"context": "./client"}},
        }}
        env = {**self.env, "SERVER_IMAGE": "api", "SERVER_TAG": "1.2.3", "CLIENT_IMAGE": "web", "CLIENT_TAG": "1.2.3"}
        script = command(named_step(ASSETS / "docker-release.yml", "Prepare deploy configuration"))
        with (
            contextlib.chdir(self.root),
            patch.dict(os.environ, env, clear=True),
            patch("subprocess.check_output", return_value=json.dumps(compose).encode()),
        ):
            exec(compile(script, "deploy configuration", "exec"), {})  # noqa: S102
        deploy = self.root / "release/deploy"
        runtime = json.loads((deploy / "docker-compose.yaml").read_text())
        self.assertTrue(all("build" not in service for service in runtime["services"].values()))
        self.assertEqual(runtime["services"]["server"]["image"], "${SERVER_IMAGE}:${SERVER_TAG}")
        self.assertEqual((deploy / ".env.example").read_text(),
                         "SERVER_IMAGE=api\nSERVER_TAG=1.2.3\nCLIENT_IMAGE=web\nCLIENT_TAG=1.2.3\nCUSTOM=keep\n")
        self.assertFalse((deploy / ".env").exists())


if __name__ == "__main__":
    unittest.main()
