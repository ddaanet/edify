"""/build's prose ``git log`` commands print hashes on signed history.

The orchestrator runs these commands straight from the prose and reads the
output as a hash list. A reader's ``log.showSignature`` puts verification lines
ahead of each hash (D-88), so every command is extracted from its file and run
against a repo with signed commits and ``log.showSignature=true``.
"""

import os
import re
import shlex
import shutil
import subprocess
from pathlib import Path

import pytest


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    """Parametrize over every extracted command, ids ``<file>:<n>``.

    A scanned file whose extraction finds no command, or fewer commands than
    the file has ``--format=%H`` flags, adds a failing ``<file>:missed`` case,
    so a command in a shape the extractor misses is never dropped silently.
    """
    if "case" not in metafunc.fixturenames:
        return
    cases: list[tuple[str, str | None]] = []
    ids: list[str] = []
    for rel in SCANNED:
        commands = _extract(REPO_ROOT / rel)
        if not commands or len(commands) != _flag_count(rel):
            cases.append((rel, None))
            ids.append(f"{Path(rel).name}:missed")
        for n, command in enumerate(commands, 1):
            cases.append((rel, command))
            ids.append(f"{Path(rel).name}:{n}")
    metafunc.parametrize("case", cases, ids=ids)


REPO_ROOT = Path(__file__).resolve().parents[1]
SCANNED = (
    "plugin/skills/build/references/phase-boundary.md",
    "plugin/skills/build/references/tdd-slice.md",
    "plugin/skills/build/references/escalation.md",
    "plugin/agents/tdd-auditor.md",
    "docs/references/build-run-state.md",
    "docs/references/pipeline-contracts.md",
    "plugin/skills/build/references/finishing.md",
)


def test_read_git_log_commands_print_hashes_only_on_signed_history(
    case: tuple[str, str | None], signed_repo: tuple[Path, dict[str, str]]
) -> None:
    """Each extracted command prints 40-hex hash lines and nothing else."""
    rel, command = case
    assert command is not None, (
        f"{rel}: extracted {len(_extract(REPO_ROOT / rel))} git log commands,"
        f" but the file has {_flag_count(rel)} --format=%H; a scanned file"
        " needs at least one, and the extractor must find every one"
    )
    repo, values = signed_repo
    text = command
    for placeholder, value in values.items():
        text = text.replace(placeholder, value)
    leftover = re.findall(r"<[^>]*>", text)
    assert not leftover, f"{rel}: unsubstituted {leftover} in {text!r}"
    result = subprocess.run(
        shlex.split(text),
        cwd=repo,
        env=_git_env(),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, f"{text!r}: {result.stdout}{result.stderr}"
    lines = result.stdout.splitlines()
    assert lines, f"{text!r}: empty stdout"
    stray = [line for line in lines if not SHA.fullmatch(line)]
    assert not stray, f"{text!r}: non-hash stdout lines {stray}"


SHA = re.compile(r"[0-9a-f]{40}")


@pytest.fixture(scope="module")
def signed_repo(
    tmp_path_factory: pytest.TempPathFactory,
) -> tuple[Path, dict[str, str]]:
    """Build a repo of SSH-signed commits and its placeholder table.

    The fixture asserts its own discriminating state: every commit carries a
    good signature, and a bare ``git log --format=%H`` prints a non-hash line.
    Without that, a command could pass because nothing printed a signature.
    """
    if shutil.which("ssh-keygen") is None:
        pytest.skip("ssh-keygen is absent: no SSH signing key can be made")
    version = subprocess.run(
        ["git", "--version"], capture_output=True, text=True, check=True
    ).stdout
    found = re.search(r"(\d+)\.(\d+)", version)
    assert found, f"unparseable git version: {version!r}"
    if (int(found[1]), int(found[2])) < (2, 34):
        pytest.skip(f"git lacks SSH signing before 2.34: {version.strip()}")

    root = tmp_path_factory.mktemp("signed")
    repo = root / "repo"
    repo.mkdir()
    key = root / "key"
    keygen = subprocess.run(
        ["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(key)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert keygen.returncode == 0, keygen.stdout + keygen.stderr
    signers = root / "allowed_signers"
    pubkey = key.with_suffix(".pub").read_text(encoding="utf-8").strip()
    signers.write_text(f"test@example.com {pubkey}\n", encoding="utf-8")

    _git(repo, "init", "-q", "-b", "main")
    for name, value in (
        ("user.name", "Test User"),
        ("user.email", "test@example.com"),
        ("gpg.format", "ssh"),
        ("user.signingkey", str(key)),
        ("gpg.ssh.allowedSignersFile", str(signers)),
        ("commit.gpgSign", "true"),
        ("log.showSignature", "true"),
    ):
        _git(repo, "config", name, value)

    reports = "plans/j/reports"
    steps = (
        "plans/j/outline.md",
        f"{reports}/item-1-1.md",
        f"{reports}/item-1-1-s1-green.md",
        f"{reports}/phase-1-corrector.md",
        f"{reports}/review-code.md",
        f"{reports}/final-review.md",
        f"{reports}/tdd-audit.md",
    )
    for step in steps:
        path = repo / step
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("x\n", encoding="utf-8")
        _git(repo, "add", "--", step)
        _git(repo, "commit", "-q", "-m", step)

    statuses = _git(repo, "log", "--no-show-signature", "--format=%G?").split()
    assert statuses == ["G"] * len(steps), f"not all good-signed: {statuses}"
    shown = _git(repo, "log", "-1", "--format=%H").splitlines()
    assert any(not SHA.fullmatch(line) for line in shown), (
        f"log.showSignature printed no signature line: {shown}"
    )

    item_commit = _git(
        repo,
        *("log", "-1", "--no-show-signature", "--format=%H"),
        *("--", f"{reports}/item-1-1.md"),
    ).strip()
    base = _git(repo, "rev-parse", f"{item_commit}^").strip()
    values = {
        "<job>": "j",
        "N-M": "1-1",
        "<k>": "1",
        "<P>": "1",
        "<name>": "item-1-1",
        "<hosting file>": "outline.md",
        "<run base>": base,
        "<L>": item_commit,
    }
    return repo, values


def _git_env() -> dict[str, str]:
    """Environment insulated from the user's git config and ssh agent.

    Every inherited ``GIT_CONFIG*`` variable goes: ``GIT_CONFIG_PARAMETERS``
    and ``GIT_CONFIG_COUNT`` inject config over the repo's own, which could
    turn ``log.showSignature`` off. ``SSH_AUTH_SOCK`` goes too; the signing
    key is a file, which git hands to ``ssh-keygen -Y sign -f``.
    """
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_CONFIG")}
    env.pop("SSH_AUTH_SOCK", None)
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_CONFIG_SYSTEM"] = os.devnull
    return env


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        env=_git_env(),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, f"git {args}: {result.stdout}{result.stderr}"
    return result.stdout


def _flag_count(rel: str) -> int:
    return (REPO_ROOT / rel).read_text(encoding="utf-8").count("--format=%H")


def _extract(path: Path) -> list[str]:
    """Return each ``git log`` command carrying ``--format=%H`` in ``path``.

    Commands come from fenced blocks, with backslash continuations joined, and
    from inline code spans, paired within a blank-line-delimited paragraph so a
    span wrapped across a line break is still found.
    """
    commands: list[str] = []
    block: list[str] = []
    prose: list[str] = []
    in_fence = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if FENCE.match(line):
            if in_fence:
                commands.extend(_join_block(block))
                block = []
            else:
                commands.extend(_spans(prose))
                prose = []
            in_fence = not in_fence
        elif in_fence:
            block.append(line)
        elif line.strip():
            prose.append(line)
        else:
            commands.extend(_spans(prose))
            prose = []
    commands.extend(_spans(prose))
    return [c for c in commands if c.startswith("git log") and "--format=%H" in c]


FENCE = re.compile(r"^\s*(```|~~~)")


def _spans(paragraph: list[str]) -> list[str]:
    return [" ".join(m[1].split()) for m in SPAN.finditer("\n".join(paragraph))]


SPAN = re.compile(r"`([^`]*)`")


def _join_block(lines: list[str]) -> list[str]:
    joined: list[str] = []
    pending = ""
    for line in lines:
        stripped = line.strip()
        if stripped.endswith("\\"):
            pending += stripped[:-1].strip() + " "
        else:
            joined.append(pending + stripped)
            pending = ""
    if pending:
        joined.append(pending.strip())
    return joined
