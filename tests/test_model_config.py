"""Test model configuration with Pydantic models."""

from pathlib import Path

from edify.model import LiteLLMModel
from edify.model.config import (
    filter_by_tier,
    load_litellm_config,
    parse_model_entry,
)


def test_litellm_model_creation() -> None:
    """LiteLLMModel can be instantiated with required fields."""
    model = LiteLLMModel(
        name="Claude 3.5 Sonnet",
        litellm_model="claude-3-5-sonnet-20241022",
        tiers=["plan", "api"],
        arena_rank=1,
        input_price=3.0,
        output_price=15.0,
        api_key_env="ANTHROPIC_API_KEY",
        api_base=None,
    )
    assert model.name == "Claude 3.5 Sonnet"
    assert model.litellm_model == "claude-3-5-sonnet-20241022"
    assert model.tiers == ["plan", "api"]
    assert model.arena_rank == 1
    assert model.input_price == 3.0
    assert model.output_price == 15.0
    assert model.api_key_env == "ANTHROPIC_API_KEY"
    assert model.api_base is None


def test_parse_model_entry_basic() -> None:
    """parse_model_entry() extracts name and litellm_model from YAML entry."""
    yaml_text = """
  - model_name: Claude 3.5 Sonnet
    litellm_params:
      model: claude-3-5-sonnet-20241022
"""
    model = parse_model_entry(yaml_text)
    assert model.name == "Claude 3.5 Sonnet"
    assert model.litellm_model == "claude-3-5-sonnet-20241022"


def test_parse_model_entry_tiers() -> None:
    """parse_model_entry() extracts tier tags from comment metadata."""
    yaml_text = """
  - model_name: Claude 3.5 Sonnet
    litellm_params:
      model: claude-3-5-sonnet-20241022
    # haiku,sonnet - arena:5
"""
    model = parse_model_entry(yaml_text)
    assert model.tiers == ["haiku", "sonnet"]


def test_parse_model_entry_metadata() -> None:
    """Extract arena rank and pricing from model config comment.

    Parses metadata from model config entry comment line including arena rank
    and pricing.
    """
    yaml_text = """
  - model_name: Test Model
    litellm_params:
      model: test-model-123
    # haiku,sonnet - arena:5 - $0.25/$1.25
"""
    model = parse_model_entry(yaml_text)
    assert model.arena_rank == 5
    assert model.input_price == 0.25
    assert model.output_price == 1.25


def test_load_litellm_config(tmp_path: Path) -> None:
    """load_litellm_config() reads YAML file and parses all model entries."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text("""
model_list:
  - model_name: Claude 3.5 Sonnet
    litellm_params:
      model: claude-3-5-sonnet-20241022
    # sonnet - arena:1 - $3.00/$15.00

  - model_name: Claude 3.5 Haiku
    litellm_params:
      model: claude-3-5-haiku-20241022
    # haiku - arena:2 - $0.80/$4.00
""")
    models = load_litellm_config(config_file)
    assert len(models) == 2
    assert models[0].name == "Claude 3.5 Sonnet"
    assert models[0].litellm_model == "claude-3-5-sonnet-20241022"
    assert models[0].arena_rank == 1
    assert models[1].name == "Claude 3.5 Haiku"
    assert models[1].litellm_model == "claude-3-5-haiku-20241022"
    assert models[1].arena_rank == 2


def test_filter_by_tier() -> None:
    """filter_by_tier() returns models matching specified tier."""
    models = [
        LiteLLMModel(
            name="Claude 3.5 Sonnet",
            litellm_model="claude-3-5-sonnet-20241022",
            tiers=["sonnet", "api"],
            arena_rank=1,
            input_price=3.0,
            output_price=15.0,
            api_key_env="ANTHROPIC_API_KEY",
            api_base=None,
        ),
        LiteLLMModel(
            name="Claude 3.5 Haiku",
            litellm_model="claude-3-5-haiku-20241022",
            tiers=["haiku"],
            arena_rank=2,
            input_price=0.8,
            output_price=4.0,
            api_key_env="ANTHROPIC_API_KEY",
            api_base=None,
        ),
    ]
    haiku_models = filter_by_tier(models, "haiku")
    assert len(haiku_models) == 1
    assert haiku_models[0].name == "Claude 3.5 Haiku"
