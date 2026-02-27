"""Tests for triage-feedback script."""

import subprocess
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parent.parent / "agent-core" / "bin" / "triage-feedback.sh"
)


def _init_repo(tmp_path: Path) -> tuple[Path, str]:
    """Initialize git repo with initial commit.

    Returns (repo_path, commit_sha).
    """
    repo_path = tmp_path / "test-repo"
    repo_path.mkdir()

    result = subprocess.run(
        ["git", "init"],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"git init failed: {result.stderr}"

    result = subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"git config email failed: {result.stderr}"

    result = subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"git config name failed: {result.stderr}"

    (repo_path / "dummy.txt").write_text("initial content")

    result = subprocess.run(
        ["git", "add", "dummy.txt"],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"git add failed: {result.stderr}"

    result = subprocess.run(
        ["git", "commit", "-m", "initial"],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"git commit failed: {result.stderr}"

    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"git rev-parse failed: {result.stderr}"
    commit_sha = result.stdout.strip()

    return repo_path, commit_sha


def test_script_exists_and_executable() -> None:
    """Script exists and has executable permission."""
    assert SCRIPT.exists(), f"Script not found at {SCRIPT}"
    assert SCRIPT.stat().st_mode & 0o111, f"Script is not executable: {SCRIPT}"


def test_no_args_shows_usage() -> None:
    """Running without args shows usage to stderr and exits 0."""
    result = subprocess.run(
        [str(SCRIPT)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Expected exit 0, got {result.returncode}: {result.stderr}"
    )
    assert "Usage" in result.stderr, f"Usage not in stderr: {result.stderr}"


def test_basic_invocation_produces_output(tmp_path: Path) -> None:
    """Invocation with args produces both Evidence and Verdict sections."""
    repo_path, baseline_sha = _init_repo(tmp_path)

    result = subprocess.run(
        [str(SCRIPT), "testjob", baseline_sha],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Expected exit 0, got {result.returncode}: {result.stderr}"
    )
    assert "## Evidence" in result.stdout, f"Evidence section missing: {result.stdout}"
    assert "## Verdict" in result.stdout, f"Verdict section missing: {result.stdout}"


def test_files_changed_count(tmp_path: Path) -> None:
    """Script counts files changed since baseline commit."""
    repo_path, baseline_sha = _init_repo(tmp_path)

    (repo_path / "newfile.txt").write_text("new content")

    result = subprocess.run(
        ["git", "add", "newfile.txt"],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"git add failed: {result.stderr}"

    result = subprocess.run(
        ["git", "commit", "-m", "add new file"],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"git commit failed: {result.stderr}"

    result = subprocess.run(
        [str(SCRIPT), "testjob", baseline_sha],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Expected exit 0, got {result.returncode}: {result.stderr}"
    )
    assert "Files changed: 1" in result.stdout, (
        f"Expected 'Files changed: 1', got: {result.stdout}"
    )


def test_report_count_excludes_preexecution(tmp_path: Path) -> None:
    """Script counts report files, excluding pre-execution artifacts."""
    repo_path, baseline_sha = _init_repo(tmp_path)

    reports_dir = repo_path / "plans" / "testjob" / "reports"
    reports_dir.mkdir(parents=True)

    (reports_dir / "review.md").write_text("review content")
    (reports_dir / "check.md").write_text("check content")
    (reports_dir / "outline-review.md").write_text("outline review")
    (reports_dir / "design-review.md").write_text("design review")
    (reports_dir / "recall-artifact.md").write_text("recall artifact")

    result = subprocess.run(
        [str(SCRIPT), "testjob", baseline_sha],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Expected exit 0, got {result.returncode}: {result.stderr}"
    )
    assert "Reports: 2" in result.stdout, f"Expected 'Reports: 2', got: {result.stdout}"


def test_behavioral_code_detected(tmp_path: Path) -> None:
    """Script detects behavioral code (functions and classes)."""
    repo_path, baseline_sha = _init_repo(tmp_path)

    (repo_path / "newcode.py").write_text(
        "def new_function():\n    pass\n\nclass NewClass:\n    pass\n"
    )

    result = subprocess.run(
        ["git", "add", "newcode.py"],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"git add failed: {result.stderr}"

    result = subprocess.run(
        ["git", "commit", "-m", "add code"],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"git commit failed: {result.stderr}"

    result = subprocess.run(
        [str(SCRIPT), "testjob", baseline_sha],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Expected exit 0, got {result.returncode}: {result.stderr}"
    )
    assert "Behavioral code: yes" in result.stdout, (
        f"Expected 'Behavioral code: yes', got: {result.stdout}"
    )


def test_no_behavioral_code_for_prose(tmp_path: Path) -> None:
    """Script reports no behavioral code for prose-only files."""
    repo_path, baseline_sha = _init_repo(tmp_path)

    (repo_path / "README.md").write_text(
        "# My Project\n\nThis is a readme file with only prose.\n"
    )

    result = subprocess.run(
        ["git", "add", "README.md"],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"git add failed: {result.stderr}"

    result = subprocess.run(
        ["git", "commit", "-m", "add readme"],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"git commit failed: {result.stderr}"

    result = subprocess.run(
        [str(SCRIPT), "testjob", baseline_sha],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Expected exit 0, got {result.returncode}: {result.stderr}"
    )
    assert "Behavioral code: no" in result.stdout, (
        f"Expected 'Behavioral code: no', got: {result.stdout}"
    )


def test_underclassified_simple_with_behavioral_code(tmp_path: Path) -> None:
    """Script detects underclassification when Simple has behavioral code."""
    repo_path, baseline_sha = _init_repo(tmp_path)

    classification_dir = repo_path / "plans" / "testjob"
    classification_dir.mkdir(parents=True)
    (classification_dir / "classification.md").write_text(
        "**Classification:** Simple\n"
    )

    (repo_path / "code.py").write_text("def foo():\n    pass\n")

    result = subprocess.run(
        ["git", "add", "code.py"],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"git add failed: {result.stderr}"

    result = subprocess.run(
        ["git", "commit", "-m", "add code"],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"git commit failed: {result.stderr}"

    result = subprocess.run(
        [str(SCRIPT), "testjob", baseline_sha],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Expected exit 0, got {result.returncode}: {result.stderr}"
    )
    assert "underclassified" in result.stdout, (
        f"Expected 'underclassified' in: {result.stdout}"
    )
    assert "Triage: predicted Simple" in result.stdout, (
        f"Expected 'Triage: predicted Simple' in: {result.stdout}"
    )


def test_overclassified_complex_minimal_changes(tmp_path: Path) -> None:
    """Script detects overclassification when Complex has minimal changes."""
    repo_path, baseline_sha = _init_repo(tmp_path)

    classification_dir = repo_path / "plans" / "testjob"
    classification_dir.mkdir(parents=True)
    (classification_dir / "classification.md").write_text(
        "**Classification:** Complex\n"
    )

    (repo_path / "README.md").write_text("# Documentation\n\nJust prose.\n")

    result = subprocess.run(
        ["git", "add", "README.md"],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"git add failed: {result.stderr}"

    result = subprocess.run(
        ["git", "commit", "-m", "add readme"],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"git commit failed: {result.stderr}"

    result = subprocess.run(
        [str(SCRIPT), "testjob", baseline_sha],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Expected exit 0, got {result.returncode}: {result.stderr}"
    )
    assert "overclassified" in result.stdout, (
        f"Expected 'overclassified' in: {result.stdout}"
    )


def test_match_moderate(tmp_path: Path) -> None:
    """Script reports match for Moderate classification with behavioral code."""
    repo_path, baseline_sha = _init_repo(tmp_path)

    classification_dir = repo_path / "plans" / "testjob"
    classification_dir.mkdir(parents=True)
    (classification_dir / "classification.md").write_text(
        "**Classification:** Moderate\n"
    )

    (repo_path / "code.py").write_text("def bar():\n    pass\n")

    result = subprocess.run(
        ["git", "add", "code.py"],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"git add failed: {result.stderr}"

    result = subprocess.run(
        ["git", "commit", "-m", "add code"],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"git commit failed: {result.stderr}"

    result = subprocess.run(
        [str(SCRIPT), "testjob", baseline_sha],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Expected exit 0, got {result.returncode}: {result.stderr}"
    )
    assert "match" in result.stdout, f"Expected 'match' in: {result.stdout}"


def test_log_created_with_entry(tmp_path: Path) -> None:
    """Script creates and appends to triage-feedback-log.md."""
    repo_path, baseline_sha = _init_repo(tmp_path)

    classification_dir = repo_path / "plans" / "testjob"
    classification_dir.mkdir(parents=True)
    (classification_dir / "classification.md").write_text(
        "**Classification:** Simple\n"
    )

    (repo_path / "code.py").write_text("def foo():\n    pass\n")

    result = subprocess.run(
        ["git", "add", "code.py"],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"git add failed: {result.stderr}"

    result = subprocess.run(
        ["git", "commit", "-m", "add code"],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"git commit failed: {result.stderr}"

    (repo_path / "plans" / "reports").mkdir(parents=True, exist_ok=True)

    result = subprocess.run(
        [str(SCRIPT), "testjob", baseline_sha],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Expected exit 0, got {result.returncode}: {result.stderr}"
    )

    log_file = repo_path / "plans" / "reports" / "triage-feedback-log.md"
    assert log_file.exists(), f"Log file not created at {log_file}"

    log_content = log_file.read_text()
    assert "| Date |" in log_content, f"Header missing in log: {log_content}"
    assert "testjob" in log_content, f"Job name missing in log: {log_content}"
    assert "underclassified" in log_content, f"Verdict missing in log: {log_content}"


def test_log_appends_multiple_entries(tmp_path: Path) -> None:
    """Script appends multiple entries to triage-feedback-log.md."""
    repo_path, baseline_sha = _init_repo(tmp_path)

    classification_dir = repo_path / "plans" / "testjob"
    classification_dir.mkdir(parents=True)
    (classification_dir / "classification.md").write_text(
        "**Classification:** Simple\n"
    )

    (repo_path / "plans" / "reports").mkdir(parents=True, exist_ok=True)

    (repo_path / "code.py").write_text("def foo():\n    pass\n")

    result = subprocess.run(
        ["git", "add", "code.py"],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"git add failed: {result.stderr}"

    result = subprocess.run(
        ["git", "commit", "-m", "add code"],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"git commit failed: {result.stderr}"

    first_baseline = baseline_sha

    result = subprocess.run(
        [str(SCRIPT), "testjob", first_baseline],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"First script run failed: {result.stderr}"

    (repo_path / "code2.py").write_text("def bar():\n    pass\n")

    result = subprocess.run(
        ["git", "add", "code2.py"],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"git add code2 failed: {result.stderr}"

    result = subprocess.run(
        ["git", "commit", "-m", "add code2"],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"git commit code2 failed: {result.stderr}"

    second_baseline = baseline_sha

    result = subprocess.run(
        [str(SCRIPT), "testjob", second_baseline],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Second script run failed: {result.stderr}"

    log_file = repo_path / "plans" / "reports" / "triage-feedback-log.md"
    assert log_file.exists(), f"Log file not created at {log_file}"

    log_content = log_file.read_text()
    lines = log_content.strip().split("\n")

    data_rows = [line for line in lines if line.startswith("|") and "testjob" in line]
    assert len(data_rows) == 2, (
        f"Expected 2 data rows, got {len(data_rows)}: {log_content}"
    )


def test_no_classification_skips_log(tmp_path: Path) -> None:
    """Script silently skips log when no classification.md exists."""
    repo_path, baseline_sha = _init_repo(tmp_path)

    (repo_path / "file.txt").write_text("some content")

    result = subprocess.run(
        ["git", "add", "file.txt"],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"git add failed: {result.stderr}"

    result = subprocess.run(
        ["git", "commit", "-m", "add file"],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"git commit failed: {result.stderr}"

    result = subprocess.run(
        [str(SCRIPT), "testjob", baseline_sha],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Expected exit 0, got {result.returncode}: {result.stderr}"
    )

    assert "no-classification" in result.stdout, (
        f"Expected 'no-classification' in: {result.stdout}"
    )

    log_file = repo_path / "plans" / "reports" / "triage-feedback-log.md"
    assert not log_file.exists(), (
        f"Log file should not exist when no classification, but found: {log_file}"
    )
