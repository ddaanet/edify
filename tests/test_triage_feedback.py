"""Tests for triage-feedback script."""

import subprocess
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parent.parent / "agent-core" / "bin" / "triage-feedback.sh"
)


def _run_git(repo_path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    """Run git command in repo, assert success, return result."""
    result = subprocess.run(
        ["git", *args],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )
    cmd = " ".join(args)
    assert result.returncode == 0, f"git {cmd} failed: {result.stderr}"
    return result


def _init_repo(tmp_path: Path) -> tuple[Path, str]:
    """Initialize git repo with initial commit."""
    repo_path = tmp_path / "test-repo"
    repo_path.mkdir()
    _run_git(repo_path, "init")
    _run_git(repo_path, "config", "user.email", "test@example.com")
    _run_git(repo_path, "config", "user.name", "Test User")
    (repo_path / "dummy.txt").write_text("initial content")
    _run_git(repo_path, "add", "dummy.txt")
    _run_git(repo_path, "commit", "-m", "initial")
    result = _run_git(repo_path, "rev-parse", "HEAD")
    return repo_path, result.stdout.strip()


def _git_add_commit(repo_path: Path, filename: str, content: str, message: str) -> None:
    """Stage a file and create a commit in the given repo."""
    (repo_path / filename).write_text(content)
    _run_git(repo_path, "add", filename)
    _run_git(repo_path, "commit", "-m", message)


def _run_script(
    repo_path: Path,
    job: str,
    baseline: str,
) -> subprocess.CompletedProcess[str]:
    """Run triage-feedback.sh and return result."""
    return subprocess.run(
        [str(SCRIPT), job, baseline],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )


def test_script_exists_and_executable() -> None:
    """Script exists and has executable permission."""
    assert SCRIPT.exists(), f"Script not found at {SCRIPT}"
    assert SCRIPT.stat().st_mode & 0o111, f"Script is not executable: {SCRIPT}"


def test_no_args_shows_usage() -> None:
    """Running without args shows usage to stderr and exits 1."""
    result = subprocess.run(
        [str(SCRIPT)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1, (
        f"Expected exit 1, got {result.returncode}: {result.stderr}"
    )
    assert "Usage" in result.stderr, f"Usage not in stderr: {result.stderr}"


def test_basic_invocation_produces_output(tmp_path: Path) -> None:
    """Invocation with args produces both Evidence and Verdict sections."""
    repo_path, baseline_sha = _init_repo(tmp_path)

    result = _run_script(repo_path, "testjob", baseline_sha)
    assert result.returncode == 0, (
        f"Expected exit 0, got {result.returncode}: {result.stderr}"
    )
    assert "## Evidence" in result.stdout, f"Evidence section missing: {result.stdout}"
    assert "## Verdict" in result.stdout, f"Verdict section missing: {result.stdout}"


def test_files_changed_count(tmp_path: Path) -> None:
    """Script counts files changed since baseline commit."""
    repo_path, baseline_sha = _init_repo(tmp_path)

    _git_add_commit(repo_path, "newfile.txt", "new content", "add new file")

    result = _run_script(repo_path, "testjob", baseline_sha)
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

    result = _run_script(repo_path, "testjob", baseline_sha)
    assert result.returncode == 0, (
        f"Expected exit 0, got {result.returncode}: {result.stderr}"
    )
    assert "Reports: 2" in result.stdout, f"Expected 'Reports: 2', got: {result.stdout}"


def test_behavioral_code_detected(tmp_path: Path) -> None:
    """Script detects behavioral code (functions and classes)."""
    repo_path, baseline_sha = _init_repo(tmp_path)

    _git_add_commit(
        repo_path,
        "newcode.py",
        "def new_function():\n    pass\n\nclass NewClass:\n    pass\n",
        "add code",
    )

    result = _run_script(repo_path, "testjob", baseline_sha)
    assert result.returncode == 0, (
        f"Expected exit 0, got {result.returncode}: {result.stderr}"
    )
    assert "Behavioral code: yes" in result.stdout, (
        f"Expected 'Behavioral code: yes', got: {result.stdout}"
    )


def test_no_behavioral_code_for_prose(tmp_path: Path) -> None:
    """Script reports no behavioral code for prose-only files."""
    repo_path, baseline_sha = _init_repo(tmp_path)

    _git_add_commit(
        repo_path,
        "README.md",
        "# My Project\n\nThis is a readme file with only prose.\n",
        "add readme",
    )

    result = _run_script(repo_path, "testjob", baseline_sha)
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

    _git_add_commit(repo_path, "code.py", "def foo():\n    pass\n", "add code")

    result = _run_script(repo_path, "testjob", baseline_sha)
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

    _git_add_commit(
        repo_path, "README.md", "# Documentation\n\nJust prose.\n", "add readme"
    )

    result = _run_script(repo_path, "testjob", baseline_sha)
    assert result.returncode == 0, (
        f"Expected exit 0, got {result.returncode}: {result.stderr}"
    )
    assert "overclassified" in result.stdout, (
        f"Expected 'overclassified' in: {result.stdout}"
    )
    assert "Triage: predicted Complex" in result.stdout, (
        f"Expected 'Triage: predicted Complex' in: {result.stdout}"
    )


def test_underclassified_simple_with_reports(tmp_path: Path) -> None:
    """Underclassified when Simple has reports but no behavioral code."""
    repo_path, baseline_sha = _init_repo(tmp_path)

    classification_dir = repo_path / "plans" / "testjob"
    classification_dir.mkdir(parents=True)
    (classification_dir / "classification.md").write_text(
        "**Classification:** Simple\n"
    )

    reports_dir = classification_dir / "reports"
    reports_dir.mkdir(parents=True)
    (reports_dir / "review.md").write_text("review content")

    _git_add_commit(repo_path, "README.md", "# Prose only\n", "add readme")

    result = _run_script(repo_path, "testjob", baseline_sha)
    assert result.returncode == 0, (
        f"Expected exit 0, got {result.returncode}: {result.stderr}"
    )
    assert "underclassified" in result.stdout, (
        f"Expected 'underclassified' in: {result.stdout}"
    )
    assert "Triage: predicted Simple" in result.stdout, (
        f"Expected 'Triage: predicted Simple' in: {result.stdout}"
    )


def test_list_marker_classification_format(tmp_path: Path) -> None:
    """Script parses classification from list-marker format."""
    repo_path, baseline_sha = _init_repo(tmp_path)

    classification_dir = repo_path / "plans" / "testjob"
    classification_dir.mkdir(parents=True)
    (classification_dir / "classification.md").write_text(
        "- **Classification:** Simple\n- **Implementation certainty:** High\n"
    )

    _git_add_commit(repo_path, "code.py", "def foo():\n    pass\n", "add code")

    result = _run_script(repo_path, "testjob", baseline_sha)
    assert result.returncode == 0, (
        f"Expected exit 0, got {result.returncode}: {result.stderr}"
    )
    assert "underclassified" in result.stdout, (
        f"Expected 'underclassified' for list-marker Simple: {result.stdout}"
    )


def test_match_moderate(tmp_path: Path) -> None:
    """Script reports match for Moderate classification with behavioral code."""
    repo_path, baseline_sha = _init_repo(tmp_path)

    classification_dir = repo_path / "plans" / "testjob"
    classification_dir.mkdir(parents=True)
    (classification_dir / "classification.md").write_text(
        "**Classification:** Moderate\n"
    )

    _git_add_commit(repo_path, "code.py", "def bar():\n    pass\n", "add code")

    result = _run_script(repo_path, "testjob", baseline_sha)
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

    _git_add_commit(repo_path, "code.py", "def foo():\n    pass\n", "add code")
    (repo_path / "plans" / "reports").mkdir(parents=True, exist_ok=True)

    result = _run_script(repo_path, "testjob", baseline_sha)
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

    _git_add_commit(repo_path, "code.py", "def foo():\n    pass\n", "add code")

    result = _run_script(repo_path, "testjob", baseline_sha)
    assert result.returncode == 0, f"First script run failed: {result.stderr}"

    _git_add_commit(repo_path, "code2.py", "def bar():\n    pass\n", "add code2")

    result = _run_script(repo_path, "testjob", baseline_sha)
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

    _git_add_commit(repo_path, "file.txt", "some content", "add file")

    result = _run_script(repo_path, "testjob", baseline_sha)
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
