"""Tests for continuation registry builder."""

import importlib.util
import json
import os
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any
from unittest.mock import patch

import pytest

if TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch

# Import the hook script as a module
hook_script_path = (
    Path(__file__).parent.parent
    / "agent-core"
    / "hooks"
    / "userpromptsubmit-shortcuts.py"
)
spec = importlib.util.spec_from_file_location(
    "userpromptsubmit_shortcuts", hook_script_path
)
assert spec is not None
assert spec.loader is not None
hook_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook_module)

extract_frontmatter = hook_module.extract_frontmatter
build_registry = hook_module.build_registry
get_cached_registry = hook_module.get_cached_registry
save_registry_cache = hook_module.save_registry_cache
get_cache_path = hook_module.get_cache_path
scan_skill_files = hook_module.scan_skill_files
get_enabled_plugins = hook_module.get_enabled_plugins
get_plugin_install_path = hook_module.get_plugin_install_path


# Common YAML frontmatter patterns
_COOP_WITH_EXIT = (
    "---\nname: {name}\ncontinuation:\n"
    "  cooperative: true\n  default-exit:\n"
    "    - /handoff\n    - /commit\n---\n"
)
_COOP_EMPTY_EXIT = (
    "---\nname: {name}\ncontinuation:\n  cooperative: true\n  default-exit: []\n---\n"
)
_NON_COOP = "---\nname: {name}\ncontinuation:\n  cooperative: false\n---\n"


def _write_skill(base: Path, name: str, frontmatter: str) -> Path:
    """Create a SKILL.md file under base/name/ and return its path."""
    skill_dir = base / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(frontmatter)
    return skill_file


def _skills_path(tmp_path: Path) -> Path:
    """Create and return .claude/skills directory."""
    p = tmp_path / ".claude" / "skills"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _build_with_env(tmp_path: Path, skill_files: list[Path]) -> dict[str, Any]:
    """Build registry with proper env and cleared cache."""
    with patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": str(tmp_path)}):
        cache = get_cache_path([str(f) for f in skill_files], str(tmp_path))
        if cache.exists():
            cache.unlink()
        result: dict[str, Any] = build_registry()
        return result


class TestExtractFrontmatter:
    """Tests for frontmatter extraction from SKILL.md files."""

    def test_extract_valid_frontmatter(self, tmp_path: Path) -> None:
        """Extract valid YAML frontmatter from SKILL.md."""
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text("""---
name: design
continuation:
  cooperative: true
  default-exit:
    - /handoff
    - /commit
---

# Design Skill
""")
        fm = extract_frontmatter(skill_file)
        assert fm is not None
        assert fm["name"] == "design"
        assert fm["continuation"]["cooperative"] is True
        assert len(fm["continuation"]["default-exit"]) == 2

    def test_extract_cooperative_false(self, tmp_path: Path) -> None:
        """Extract frontmatter with cooperative: false."""
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text(
            "---\nname: experimental\ncontinuation:\n  cooperative: false\n---\n"
        )
        fm = extract_frontmatter(skill_file)
        assert fm is not None
        assert fm["continuation"]["cooperative"] is False

    def test_extract_no_frontmatter(self, tmp_path: Path) -> None:
        """Return None when SKILL.md has no frontmatter."""
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text("# Design Skill\n\nNo frontmatter.\n")
        assert extract_frontmatter(skill_file) is None

    def test_extract_malformed_yaml(self, tmp_path: Path) -> None:
        """Return None when frontmatter is malformed YAML."""
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text(
            "---\nname: design\ncontinuation:\n"
            "  default-exit: [invalid yaml: content\n---\n"
        )
        assert extract_frontmatter(skill_file) is None

    def test_extract_empty_continuation_block(self, tmp_path: Path) -> None:
        """Extract frontmatter with empty continuation block."""
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text("---\nname: design\ncontinuation: {}\n---\n")
        fm = extract_frontmatter(skill_file)
        assert fm is not None
        assert fm["continuation"] == {}


class TestScanSkillFiles:
    """Tests for skill file discovery."""

    def test_scan_finds_nested_skills(self, tmp_path: Path) -> None:
        """Scan finds SKILL.md files in nested directories."""
        _write_skill(tmp_path / "design", "nested", "---\n---")
        _write_skill(tmp_path, "plan", "---\n---")
        files = scan_skill_files(tmp_path)
        assert len(files) == 2

    def test_scan_empty_directory(self, tmp_path: Path) -> None:
        """Empty directory returns empty list."""
        assert scan_skill_files(tmp_path) == []

    def test_scan_nonexistent_directory(self, tmp_path: Path) -> None:
        """Nonexistent directory returns empty list."""
        assert scan_skill_files(tmp_path / "does_not_exist") == []


class TestCachePath:
    """Tests for cache path generation."""

    def test_cache_path_deterministic(self, tmp_path: Path) -> None:
        """Same inputs produce same cache path."""
        paths = ["/skill/design/SKILL.md", "/skill/plan/SKILL.md"]
        project = str(tmp_path)
        assert get_cache_path(paths, project) == get_cache_path(paths, project)

    def test_cache_path_order_invariant(self, tmp_path: Path) -> None:
        """Different order of paths produces same cache path."""
        p1 = ["/skill/design/SKILL.md", "/skill/plan/SKILL.md"]
        p2 = ["/skill/plan/SKILL.md", "/skill/design/SKILL.md"]
        project = str(tmp_path)
        assert get_cache_path(p1, project) == get_cache_path(p2, project)

    def test_cache_path_includes_hash(self, tmp_path: Path) -> None:
        """Cache path includes hash component."""
        path = get_cache_path(["/skill/design/SKILL.md"], str(tmp_path))
        assert "continuation-registry" in str(path)


class TestRegistryCaching:
    """Tests for registry caching mechanism."""

    def test_save_and_load_cache(self, tmp_path: Path) -> None:
        """Save and load cache round-trip."""
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text("---\nname: design\n---")

        cache_path = tmp_path / "test_cache.json"
        registry = {
            "design": {
                "cooperative": True,
                "default-exit": ["/handoff", "/commit"],
            }
        }
        save_registry_cache(registry, [str(skill_file)], cache_path)
        assert get_cached_registry(cache_path) == registry

    def test_cache_invalidation_on_mtime(self, tmp_path: Path) -> None:
        """Cache invalidates when source file modified."""
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text("---\nname: test\n---")
        cache_path = tmp_path / "cache.json"
        save_registry_cache(
            {"test": {"cooperative": True, "default-exit": []}},
            [str(skill_file)],
            cache_path,
        )
        assert get_cached_registry(cache_path) is not None

        time.sleep(0.01)
        skill_file.write_text("---\nname: test\nversion: 2\n---")
        assert get_cached_registry(cache_path) is None

    def test_cache_invalidation_on_deletion(self, tmp_path: Path) -> None:
        """Cache invalidates when source file deleted."""
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text("---\nname: test\n---")
        cache_path = tmp_path / "cache.json"
        save_registry_cache(
            {"test": {"cooperative": True, "default-exit": []}},
            [str(skill_file)],
            cache_path,
        )
        skill_file.unlink()
        assert get_cached_registry(cache_path) is None

    @pytest.mark.parametrize(
        "content",
        [None, "{ invalid json }", json.dumps({"registry": {}})],
        ids=["missing", "malformed", "missing-fields"],
    )
    def test_cache_returns_none_for_invalid(
        self, tmp_path: Path, content: str | None
    ) -> None:
        """Return None for missing, malformed, or incomplete cache files."""
        cache_path = tmp_path / "cache.json"
        if content is not None:
            cache_path.write_text(content)
        assert get_cached_registry(cache_path) is None


class TestBuildRegistry:
    """Tests for registry building (integration)."""

    def test_build_registry_cooperative_only(self, tmp_path: Path) -> None:
        """Registry includes only cooperative skills."""
        sp = _skills_path(tmp_path)
        f1 = _write_skill(sp, "design", _COOP_WITH_EXIT.format(name="design"))
        f2 = _write_skill(sp, "experimental", _NON_COOP.format(name="experimental"))
        registry = _build_with_env(tmp_path, [f1, f2])
        assert "design" in registry
        assert registry["design"]["cooperative"] is True
        assert "experimental" not in registry

    def test_build_registry_missing_continuation_block(self, tmp_path: Path) -> None:
        """Skills without continuation block are excluded."""
        sp = _skills_path(tmp_path)
        f = _write_skill(sp, "legacy", "---\nname: legacy\n---\n")
        registry = _build_with_env(tmp_path, [f])
        assert "legacy" not in registry

    def test_build_registry_empty_default_exit(self, tmp_path: Path) -> None:
        """Registry includes skills with empty default-exit."""
        sp = _skills_path(tmp_path)
        f = _write_skill(sp, "commit", _COOP_EMPTY_EXIT.format(name="commit"))
        registry = _build_with_env(tmp_path, [f])
        assert "commit" in registry
        assert registry["commit"]["default-exit"] == []

    def test_build_registry_no_project_dir(self) -> None:
        """Empty dict when CLAUDE_PROJECT_DIR not set."""
        with patch.dict(os.environ, {}, clear=True):
            if "CLAUDE_PROJECT_DIR" in os.environ:
                del os.environ["CLAUDE_PROJECT_DIR"]
            assert build_registry() == {}

    def test_build_registry_uses_cache(
        self, tmp_path: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """Registry uses cache on second call when files unchanged."""
        sp = _skills_path(tmp_path)
        _write_skill(sp, "design", _COOP_EMPTY_EXIT.format(name="design"))
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
        monkeypatch.setenv("TMPDIR", str(cache_dir))

        r1 = build_registry()
        assert "design" in r1
        r2 = build_registry()
        assert r2 == r1

    def test_build_registry_extracts_name_from_directory(self, tmp_path: Path) -> None:
        """Uses directory name when 'name' field missing."""
        sp = _skills_path(tmp_path)
        f = _write_skill(
            sp,
            "myskill",
            "---\ncontinuation:\n  cooperative: true\n  default-exit: []\n---\n",
        )
        registry = _build_with_env(tmp_path, [f])
        assert "myskill" in registry


class TestPluginSkillDiscovery:
    """Tests for plugin skill discovery."""

    def test_get_enabled_plugins_no_settings(self, tmp_path: Path) -> None:
        """Empty list when settings don't exist."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            assert get_enabled_plugins() == []

    def test_get_enabled_plugins_from_settings(self, tmp_path: Path) -> None:
        """Reads enabled plugins from settings.json."""
        settings = tmp_path / ".claude" / "settings.json"
        settings.parent.mkdir(parents=True)
        settings.write_text(json.dumps({"enabledPlugins": ["plugin1", "plugin2"]}))
        with patch("pathlib.Path.home", return_value=tmp_path):
            plugins = get_enabled_plugins()
        assert "plugin1" in plugins
        assert "plugin2" in plugins

    def test_get_plugin_install_path_not_found(self, tmp_path: Path) -> None:
        """Returns None if plugin not in installed_plugins.json."""
        installed = tmp_path / ".claude" / "plugins" / "installed_plugins.json"
        installed.parent.mkdir(parents=True)
        installed.write_text(json.dumps({}))
        with patch("pathlib.Path.home", return_value=tmp_path):
            assert get_plugin_install_path("nonexistent", "/project") is None

    def test_get_plugin_install_path_scope_filtering(self, tmp_path: Path) -> None:
        """Returns None when project scope doesn't match."""
        installed = tmp_path / ".claude" / "plugins" / "installed_plugins.json"
        installed.parent.mkdir(parents=True)
        installed.write_text(
            json.dumps(
                {
                    "myplugin": {
                        "installPath": "/install/path",
                        "scope": "project",
                        "projectPath": "/other/project",
                    }
                }
            )
        )
        with patch("pathlib.Path.home", return_value=tmp_path):
            assert get_plugin_install_path("myplugin", "/my/project") is None

    def test_get_plugin_install_path_user_scope(self, tmp_path: Path) -> None:
        """Returns install path for user-scoped plugin."""
        installed = tmp_path / ".claude" / "plugins" / "installed_plugins.json"
        installed.parent.mkdir(parents=True)
        installed.write_text(
            json.dumps({"myplugin": {"installPath": "/install/path", "scope": "user"}})
        )
        with patch("pathlib.Path.home", return_value=tmp_path):
            assert (
                get_plugin_install_path("myplugin", "/any/project") == "/install/path"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
