"""Tests for bin/edify-count-tokens, run as a subprocess against a fake API."""

# ruff: noqa: D102, D103, D107

import ast
import json
import os
import subprocess
import threading
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any

import pytest

from tests.markdown_script import REPO_ROOT

SCRIPT = REPO_ROOT / "bin" / "edify-count-tokens"

MODELS = [
    {"id": "claude-sonnet-4-20250514", "created_at": "2025-05-14T00:00:00Z"},
    {"id": "claude-sonnet-5-5", "created_at": "2026-09-01T00:00:00Z"},
    {"id": "claude-opus-5-5", "created_at": "2026-10-01T00:00:00Z"},
]


class FakeApi(HTTPServer):
    """Records requests and answers with canned replies."""

    def __init__(self) -> None:
        super().__init__(("127.0.0.1", 0), Handler)
        self.requests: list[dict[str, Any]] = []
        self.status = 200

    @property
    def url(self) -> str:
        return f"http://127.0.0.1:{self.server_port}"


class Handler(BaseHTTPRequestHandler):
    """Serve /v1/models and /v1/messages/count_tokens."""

    def _reply(self, status: int, payload: dict[str, Any]) -> None:
        data = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _record(self, body: dict[str, Any] | None) -> None:
        self.server.requests.append(  # type: ignore[attr-defined]
            {
                "method": self.command,
                "path": self.path,
                "headers": {k.lower(): v for k, v in self.headers.items()},
                "body": body,
            }
        )

    def do_GET(self) -> None:
        self._record(None)
        self._reply(200, {"data": MODELS})

    def do_POST(self) -> None:
        length = int(self.headers["content-length"])
        body = json.loads(self.rfile.read(length))
        self._record(body)
        status = self.server.status  # type: ignore[attr-defined]
        if status != 200:
            self._reply(status, {"error": {"message": "refused"}})
            return
        self._reply(200, {"input_tokens": len(body["messages"][0]["content"]) + 7})

    def log_message(self, *args: object) -> None:
        """Keep test output quiet."""


@pytest.fixture
def api() -> Iterator[FakeApi]:
    server = FakeApi()
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield server
    server.shutdown()
    server.server_close()


def run(
    api_url: str,
    home: Path,
    *args: str,
    key_env: str | None = None,
    extra_env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    env = {
        "PATH": os.environ["PATH"],
        "HOME": str(home),
        "ANTHROPIC_BASE_URL": api_url,
        **(extra_env or {}),
    }
    if key_env is not None:
        env["ANTHROPIC_API_KEY"] = key_env
    return subprocess.run(
        [str(SCRIPT), *args],
        env=env,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )


def write_config(home: Path, text: str) -> None:
    config = home / ".config" / "edify" / "config.toml"
    config.parent.mkdir(parents=True)
    config.write_text(text)


def test_script_is_executable() -> None:
    assert os.access(SCRIPT, os.X_OK)


def test_script_parses_as_python_3_9() -> None:
    """Test: macOS /usr/bin/python3 is 3.9, so no newer grammar appears."""
    text = SCRIPT.read_text()
    ast.parse(text, filename=str(SCRIPT), feature_version=(3, 9))
    assert "from __future__ import annotations" in text


def no_tomllib_env(tmp_path: Path) -> dict[str, str]:
    """Shadow tomllib with a failing module, as on Python before 3.11."""
    shadow = tmp_path / "shadow"
    shadow.mkdir()
    (shadow / "tomllib.py").write_text("raise ImportError('no tomllib')\n")
    return {"PYTHONPATH": str(shadow)}


def test_config_without_tomllib_names_python_version(
    api: FakeApi, tmp_path: Path
) -> None:
    write_config(tmp_path, '[anthropic]\napi_key = "sk-ant-api03-fake"\n')
    doc = tmp_path / "d.md"
    doc.write_text("x")

    result = run(api.url, tmp_path, str(doc), extra_env=no_tomllib_env(tmp_path))

    assert result.returncode == 1
    assert result.stdout == ""
    assert "needs Python 3.11 or later" in result.stderr
    assert len(result.stderr.splitlines()) == 1
    assert api.requests == []


def test_env_key_works_without_tomllib(api: FakeApi, tmp_path: Path) -> None:
    write_config(tmp_path, '[anthropic]\napi_key = "sk-ant-api03-fake"\n')
    doc = tmp_path / "d.md"
    doc.write_text("x")

    result = run(
        api.url,
        tmp_path,
        str(doc),
        key_env="sk-ant-api03-env",
        extra_env=no_tomllib_env(tmp_path),
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.endswith(f"{doc}: 8 tokens\n")


def test_counts_one_file_with_config_key(api: FakeApi, tmp_path: Path) -> None:
    write_config(tmp_path, '[anthropic]\napi_key = "sk-ant-api03-fake"\n')
    doc = tmp_path / "doc.md"
    doc.write_text("hello world")

    result = run(api.url, tmp_path, str(doc))

    assert result.returncode == 0, result.stderr
    assert result.stdout == f"Using model: claude-sonnet-5-5\n{doc}: 18 tokens\n"
    models_req, count_req = api.requests
    assert models_req["method"] == "GET"
    assert models_req["path"].startswith("/v1/models")
    assert count_req["method"] == "POST"
    assert count_req["path"] == "/v1/messages/count_tokens"
    assert count_req["headers"]["x-api-key"] == "sk-ant-api03-fake"
    assert "authorization" not in count_req["headers"]
    assert count_req["headers"]["anthropic-version"] == "2023-06-01"
    assert count_req["body"] == {
        "model": "claude-sonnet-5-5",
        "messages": [{"role": "user", "content": "hello world"}],
    }


def test_json_output_with_two_files_and_model_alias(
    api: FakeApi, tmp_path: Path
) -> None:
    a = tmp_path / "a.md"
    b = tmp_path / "b.md"
    a.write_text("abc")
    b.write_text("abcdef")

    result = run(
        api.url, tmp_path, "--model", "opus", "--json", str(a), str(b), key_env="k"
    )

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {
        "model": "claude-opus-5-5",
        "files": [{"path": str(a), "count": 10}, {"path": str(b), "count": 13}],
        "total": 23,
    }
    assert [r["body"]["model"] for r in api.requests if r["body"]] == [
        "claude-opus-5-5"
    ] * 2


def test_text_output_totals_multiple_files(api: FakeApi, tmp_path: Path) -> None:
    a = tmp_path / "a.md"
    b = tmp_path / "b.md"
    a.write_text("abc")
    b.write_text("")

    result = run(api.url, tmp_path, str(a), str(b), key_env="k")

    assert result.stdout.splitlines() == [
        "Using model: claude-sonnet-5-5",
        f"{a}: 10 tokens",
        f"{b}: 0 tokens",
        "Total: 10 tokens",
    ]
    assert len([r for r in api.requests if r["body"]]) == 1


def test_full_model_id_skips_alias_lookup(api: FakeApi, tmp_path: Path) -> None:
    doc = tmp_path / "d.md"
    doc.write_text("x")

    result = run(
        api.url, tmp_path, "--model", "claude-opus-4-20250514", str(doc), key_env="k"
    )

    assert result.returncode == 0, result.stderr
    assert [r["method"] for r in api.requests] == ["POST"]
    assert api.requests[0]["body"]["model"] == "claude-opus-4-20250514"


def test_oauth_token_authenticates_as_bearer(api: FakeApi, tmp_path: Path) -> None:
    doc = tmp_path / "d.md"
    doc.write_text("x")

    run(api.url, tmp_path, str(doc), key_env="sk-ant-oat01-fake")

    headers = api.requests[-1]["headers"]
    assert headers["authorization"] == "Bearer sk-ant-oat01-fake"
    assert "x-api-key" not in headers


def test_env_key_wins_over_config(api: FakeApi, tmp_path: Path) -> None:
    write_config(tmp_path, '[anthropic]\napi_key = "from-config"\n')
    doc = tmp_path / "d.md"
    doc.write_text("x")

    run(api.url, tmp_path, str(doc), key_env="from-env")

    assert api.requests[-1]["headers"]["x-api-key"] == "from-env"


@pytest.mark.parametrize(
    "config", [None, '[anthropic]\napi_key = "  "\n', "not toml ["]
)
def test_missing_key_errors_without_calling_api(
    api: FakeApi, tmp_path: Path, config: str | None
) -> None:
    if config is not None:
        write_config(tmp_path, config)
    doc = tmp_path / "d.md"
    doc.write_text("x")

    result = run(api.url, tmp_path, str(doc))

    assert result.returncode == 1
    assert result.stdout == ""
    assert "Error: Authentication failed" in result.stderr
    assert "ANTHROPIC_API_KEY" in result.stderr
    assert "~/.config/edify/config.toml" in result.stderr
    assert api.requests == []


def test_rejected_key_reports_auth_failure(api: FakeApi, tmp_path: Path) -> None:
    api.status = 401
    doc = tmp_path / "d.md"
    doc.write_text("x")

    result = run(
        api.url, tmp_path, "--model", "claude-opus-4-20250514", str(doc), key_env="bad"
    )

    assert result.returncode == 1
    assert "Error: Authentication failed (" in result.stderr


def test_unreadable_file_errors(api: FakeApi, tmp_path: Path) -> None:
    result = run(
        api.url,
        tmp_path,
        "--model",
        "claude-opus-4-20250514",
        str(tmp_path / "missing.md"),
        key_env="k",
    )

    assert result.returncode == 1
    assert "Error: Failed to read" in result.stderr
