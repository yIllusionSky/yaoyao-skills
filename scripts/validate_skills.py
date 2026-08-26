#!/usr/bin/env python3
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
USES_PATTERN = re.compile(r"^\s*(?:-\s*)?uses:\s*([^@\s]+)@([^\s#]+)", re.MULTILINE)


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
        *sorted((SKILLS / "github-actions" / "assets").glob("*.yml")),
    ]
    for workflow in workflow_files:
        text = workflow.read_text(encoding="utf-8")
        for owner, reference in USES_PATTERN.findall(text):
            if owner.startswith("./"):
                continue
            if not re.fullmatch(r"[0-9a-f]{40}", reference):
                fail(f"action is not pinned to a full SHA in {workflow}: {owner}@{reference}")


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

        app = root / "app"
        write(app / "Cargo.toml")
        run_copy("app", "--target", str(app), "--app-bin", "demo")
        app_workflow = (app / ".github/workflows/app-release.yml").read_text(encoding="utf-8")
        if "APP_NAME: demo" not in app_workflow or "__APP_BIN__" in app_workflow:
            fail("app workflow placeholder was not replaced")

        tauri = root / "tauri"
        write(tauri / "package.json", "{}\n")
        write(tauri / "bun.lock")
        write(tauri / "src-tauri/Cargo.toml")
        run_copy("tauri", "--target", str(tauri))

        server = root / "server-only"
        write(server / "server/Cargo.toml")
        run_copy("docker", "--target", str(server), "--server-bin", "api")
        server_compose = (server / "docker-compose.yaml").read_text(encoding="utf-8")
        if "  client:" in server_compose or (server / "client/Dockerfile").exists():
            fail("server-only overlay unexpectedly contains client assets")
        if "__SERVER_BIN__" in (server / "server/Dockerfile").read_text(encoding="utf-8"):
            fail("server binary placeholder was not replaced")

        fullstack = root / "fullstack"
        write(fullstack / "server/Cargo.toml")
        write(fullstack / "client/package.json", '{"name":"client","version":"0.1.0"}\n')
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

        missing = root / "missing"
        missing.mkdir()
        run_copy("app", "--target", str(missing), "--app-bin", "demo", expect_success=False)
        if (missing / ".github").exists():
            fail("failed validation produced partial output")


def validate_protocols() -> None:
    project = (SKILLS / "project-workflow/references/main-agent-flow.md").read_text(encoding="utf-8")
    implementation = (
        SKILLS / "project-workflow/references/implementation-subagent-flow.md"
    ).read_text(encoding="utf-8")
    task_format = (SKILLS / "project-workflow/references/task-format.md").read_text(encoding="utf-8")
    if "switch --detach main" not in project:
        fail("project-workflow does not reset new tasks to main")
    if "git -C main merge --no-ff <task-id>" not in project:
        fail("project-workflow does not merge completed tasks to main")
    if "可用 agent slot" not in project:
        fail("project-workflow does not batch subagents by available slots")
    if "git merge --ff-only <task-id>" not in implementation:
        fail("project-workflow cannot refresh a project branch after review")
    if "依次追加 `-2`、`-3`" not in task_format:
        fail("project-workflow does not resolve project worktree name collisions")


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


def validate_git_protocols() -> None:
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


def main() -> None:
    validate_skills()
    validate_links()
    validate_action_pins()
    validate_copy_assets()
    validate_protocols()
    validate_git_protocols()
    print("all skill validations passed")


if __name__ == "__main__":
    main()
