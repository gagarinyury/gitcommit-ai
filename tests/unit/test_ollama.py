"""Tests for Ollama provider."""
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from gitcommit_ai.generator.message import CommitMessage, FileDiff, GitDiff
from gitcommit_ai.providers.ollama import (
    ModelInfo,
    OllamaConfig,
    OllamaProvider,
)


class TestOllamaConfig:
    """Tests for OllamaConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = OllamaConfig()
        assert config.host == "http://localhost:11434"
        assert config.default_model == "qwen2.5"
        assert config.timeout_seconds == 60
        assert config.stream is True

    def test_from_env_with_custom_values(self, monkeypatch):
        """Test loading config from environment variables."""
        monkeypatch.setenv("OLLAMA_HOST", "http://custom:8080")
        monkeypatch.setenv("OLLAMA_DEFAULT_MODEL", "codellama")
        monkeypatch.setenv("OLLAMA_TIMEOUT", "120")

        config = OllamaConfig.from_env()
        assert config.host == "http://custom:8080"
        assert config.default_model == "codellama"
        assert config.timeout_seconds == 120

    def test_from_env_with_defaults(self, monkeypatch):
        """Test loading config with no env vars (defaults)."""
        monkeypatch.delenv("OLLAMA_HOST", raising=False)
        monkeypatch.delenv("OLLAMA_DEFAULT_MODEL", raising=False)
        monkeypatch.delenv("OLLAMA_TIMEOUT", raising=False)

        config = OllamaConfig.from_env()
        assert config.host == "http://localhost:11434"
        assert config.default_model == "qwen2.5"
        assert config.timeout_seconds == 60


class TestModelInfo:
    """Tests for ModelInfo parsing."""

    def test_parse_ollama_list_row(self):
        """Test parsing a row from 'ollama list' output."""
        row = "llama3.2:latest         a80c4f17acd5    2.0 GB    2 days ago"
        model = ModelInfo.from_list_row(row)
        assert model.name == "llama3.2:latest"
        assert model.size == "2.0 GB"
        assert model.modified == "2 days ago"

    def test_parse_with_longer_modified_date(self):
        """Test parsing with multi-word modified date."""
        row = "codellama:latest        8fdf8f752f6e    3.8 GB    1 week ago"
        model = ModelInfo.from_list_row(row)
        assert model.name == "codellama:latest"
        assert model.size == "3.8 GB"
        assert model.modified == "1 week ago"

    def test_parse_invalid_row_raises_error(self):
        """Test that invalid row raises ValueError."""
        with pytest.raises(ValueError, match="Invalid ollama list row"):
            ModelInfo.from_list_row("invalid")


class TestOllamaDetection:
    """Tests for Ollama installation detection."""

    @patch("subprocess.run")
    def test_is_installed_when_ollama_exists(self, mock_run):
        """Test is_installed returns True when ollama CLI exists."""
        mock_run.return_value = MagicMock(returncode=0)
        assert OllamaProvider.is_installed() is True
        mock_run.assert_called_once_with(
            ["ollama", "--version"],
            capture_output=True,
            text=True,
            check=False,
        )

    @patch("subprocess.run")
    def test_is_not_installed_when_command_not_found(self, mock_run):
        """Test is_installed returns False when ollama not found."""
        mock_run.side_effect = FileNotFoundError()
        assert OllamaProvider.is_installed() is False

    @patch("subprocess.run")
    def test_list_models_success(self, mock_run):
        """Test list_models parses output correctly."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="NAME                    ID              SIZE      MODIFIED\n"
            "llama3.2:latest         a80c4f17acd5    2.0 GB    2 days ago\n"
            "codellama:latest        8fdf8f752f6e    3.8 GB    1 week ago\n",
        )
        models = OllamaProvider.list_models()
        assert len(models) == 2
        assert models[0].name == "llama3.2:latest"
        assert models[1].name == "codellama:latest"

    @patch("subprocess.run")
    def test_list_models_empty(self, mock_run):
        """Test list_models with no models."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="NAME                    ID              SIZE      MODIFIED\n",
        )
        models = OllamaProvider.list_models()
        assert models == []

    @patch("subprocess.run")
    def test_list_models_raises_on_error(self, mock_run):
        """Test list_models raises RuntimeError on command failure."""
        mock_run.side_effect = FileNotFoundError()
        with pytest.raises(RuntimeError, match="Ollama not installed"):
            OllamaProvider.list_models()


class TestOllamaProvider:
    """Tests for OllamaProvider."""

    def test_init_with_defaults(self):
        """Test provider initialization with default config."""
        provider = OllamaProvider()
        assert provider.config.host == "http://localhost:11434"
        assert provider.model == "qwen2.5"

    def test_init_with_custom_model(self):
        """Test provider initialization with custom model."""
        provider = OllamaProvider(model="codellama")
        assert provider.model == "codellama"

    def test_init_with_custom_config(self):
        """Test provider initialization with custom config."""
        config = OllamaConfig(host="http://custom:9999", default_model="mistral")
        provider = OllamaProvider(config=config)
        assert provider.config.host == "http://custom:9999"
        assert provider.model == "mistral"

    @patch("gitcommit_ai.providers.ollama.OllamaProvider.is_installed")
    def test_validate_config_fails_when_not_installed(self, mock_installed):
        """Test validate_config returns error when Ollama not installed."""
        mock_installed.return_value = False
        provider = OllamaProvider()
        errors = provider.validate_config()
        assert len(errors) == 1
        assert "not installed" in errors[0]
        assert "https://ollama.ai" in errors[0]

    @patch("gitcommit_ai.providers.ollama.OllamaProvider.list_models")
    @patch("gitcommit_ai.providers.ollama.OllamaProvider.is_installed")
    def test_validate_config_fails_when_model_not_found(
        self, mock_installed, mock_list
    ):
        """Test validate_config returns error when model not found."""
        mock_installed.return_value = True
        mock_list.return_value = [
            ModelInfo(name="mistral:latest", size="4.1 GB", modified="1 day ago")
        ]
        provider = OllamaProvider(model="llama3.2")
        errors = provider.validate_config()
        assert len(errors) == 1
        assert "Model 'llama3.2' not found" in errors[0]
        assert "ollama pull" in errors[0]

    @patch("gitcommit_ai.providers.ollama.OllamaProvider.list_models")
    @patch("gitcommit_ai.providers.ollama.OllamaProvider.is_installed")
    def test_validate_config_success(self, mock_installed, mock_list):
        """Test validate_config returns no errors when everything OK."""
        mock_installed.return_value = True
        mock_list.return_value = [
            ModelInfo(name="llama3.2:latest", size="2.0 GB", modified="1 day ago")
        ]
        provider = OllamaProvider(model="llama3.2")
        errors = provider.validate_config()
        assert errors == []

    @pytest.mark.asyncio
    async def test_check_service_running_success(self):
        """Test check_service_running returns True when service responds."""
        provider = OllamaProvider()
        mock_response = AsyncMock(status_code=200)
        provider.client.get = AsyncMock(return_value=mock_response)

        result = await provider.check_service_running()
        assert result is True

    @pytest.mark.asyncio
    async def test_check_service_running_fails_on_connection_error(self):
        """Test check_service_running returns False on connection error."""
        import httpx

        provider = OllamaProvider()
        provider.client.get = AsyncMock(side_effect=httpx.ConnectError("timeout"))

        result = await provider.check_service_running()
        assert result is False


class TestOllamaStreamingParser:
    """Tests for Ollama streaming response parsing."""

    @pytest.mark.asyncio
    async def test_stream_response_accumulates_chunks(self):
        """Test _stream_response accumulates response chunks."""
        from unittest.mock import MagicMock

        provider = OllamaProvider()

        # Mock streaming response
        async def mock_aiter_lines():
            yield '{"model":"llama3.2","response":"feat","done":false}'
            yield '{"model":"llama3.2","response":": add","done":false}'
            yield '{"model":"llama3.2","response":" test","done":false}'
            yield '{"model":"llama3.2","response":"","done":true}'

        mock_response = MagicMock()
        mock_response.aiter_lines = mock_aiter_lines
        mock_response.raise_for_status = MagicMock()
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        provider.client.stream = MagicMock(return_value=mock_response)

        chunks = []
        async for chunk in provider._stream_response("test prompt"):
            chunks.append(chunk)

        # Empty response on done=true is included
        assert chunks == ["feat", ": add", " test", ""]

    @pytest.mark.asyncio
    async def test_stream_response_handles_malformed_json(self):
        """Test _stream_response skips malformed JSON lines."""
        from unittest.mock import MagicMock

        provider = OllamaProvider()

        async def mock_aiter_lines():
            yield '{"response":"valid","done":false}'
            yield "invalid json"
            yield '{"response":" chunk","done":false}'
            yield '{"done":true}'

        mock_response = MagicMock()
        mock_response.aiter_lines = mock_aiter_lines
        mock_response.raise_for_status = MagicMock()
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        provider.client.stream = MagicMock(return_value=mock_response)

        chunks = []
        async for chunk in provider._stream_response("test"):
            chunks.append(chunk)

        assert chunks == ["valid", " chunk"]


class TestOllamaMessageGeneration:
    """Tests for commit message generation."""

    @pytest.mark.asyncio
    @patch("gitcommit_ai.providers.ollama.OllamaProvider.check_service_running")
    @patch("gitcommit_ai.providers.ollama.OllamaProvider.validate_config")
    async def test_generate_commit_message_success(
        self, mock_validate, mock_service
    ):
        """Test successful commit message generation."""
        mock_validate.return_value = []
        mock_service.return_value = True

        provider = OllamaProvider()

        # Mock streaming response
        async def mock_stream(prompt):
            yield "feat"
            yield "(core)"
            yield ": add"
            yield " ollama"
            yield " support"

        provider._stream_response = mock_stream

        diff = GitDiff(
            files=[
                FileDiff(
                    path="src/providers/ollama.py",
                    change_type="added",
                    additions=100,
                    deletions=0,
                    diff_content="",
                )
            ],
            total_additions=100,
            total_deletions=0,
        )

        message = await provider.generate_commit_message(diff)
        assert isinstance(message, CommitMessage)
        assert message.type == "feat"
        assert message.scope == "core"
        assert message.description == "add ollama support"

    @pytest.mark.asyncio
    @patch("gitcommit_ai.providers.ollama.OllamaProvider.validate_config")
    async def test_generate_raises_on_validation_error(self, mock_validate):
        """Test generate raises RuntimeError on validation failure."""
        mock_validate.return_value = ["Ollama not installed"]
        provider = OllamaProvider()

        diff = GitDiff(files=[], total_additions=0, total_deletions=0)

        with pytest.raises(RuntimeError, match="Ollama validation failed"):
            await provider.generate_commit_message(diff)

    @pytest.mark.asyncio
    @patch("gitcommit_ai.providers.ollama.OllamaProvider.check_service_running")
    @patch("gitcommit_ai.providers.ollama.OllamaProvider.validate_config")
    async def test_generate_raises_when_service_not_running(
        self, mock_validate, mock_service
    ):
        """Test generate raises RuntimeError when service not running."""
        mock_validate.return_value = []
        mock_service.return_value = False

        provider = OllamaProvider()
        diff = GitDiff(files=[], total_additions=0, total_deletions=0)

        with pytest.raises(RuntimeError, match="Cannot connect to Ollama"):
            await provider.generate_commit_message(diff)

    def test_parse_response_valid(self):
        """Test _parse_response with valid conventional commit."""
        provider = OllamaProvider()
        message = provider._parse_response("feat(api): add user endpoint")
        assert message.type == "feat"
        assert message.scope == "api"
        assert message.description == "add user endpoint"

    def test_parse_response_no_scope(self):
        """Test _parse_response without scope."""
        provider = OllamaProvider()
        message = provider._parse_response("fix: correct validation logic")
        assert message.type == "fix"
        assert message.scope is None
        assert message.description == "correct validation logic"

    def test_parse_response_invalid_format(self):
        """Test _parse_response raises on invalid format."""
        provider = OllamaProvider()
        with pytest.raises(ValueError, match="Invalid commit message format"):
            provider._parse_response("no colon here")


class TestOllamaPromptImprovements:
    """Tests for improved Ollama prompt quality (Feature 009)."""

    @pytest.fixture
    def sample_diff(self) -> GitDiff:
        """Create a sample GitDiff with multiple files."""
        return GitDiff(
            files=[
                FileDiff(
                    path="src/auth.py",
                    change_type="modified",
                    additions=15,
                    deletions=3,
                    diff_content="",
                ),
                FileDiff(
                    path="tests/test_auth.py",
                    change_type="modified",
                    additions=25,
                    deletions=5,
                    diff_content="",
                ),
            ],
            total_additions=40,
            total_deletions=8,
        )

    def test_prompt_contains_expert_role(self, sample_diff: GitDiff) -> None:
        """T120: Improved prompt includes 'expert software engineer' role."""
        provider = OllamaProvider()
        prompt = provider._build_prompt(sample_diff)

        assert "expert software engineer" in prompt.lower()

    def test_prompt_includes_examples(self, sample_diff: GitDiff) -> None:
        """T121: Improved prompt includes 2+ commit examples."""
        provider = OllamaProvider()
        prompt = provider._build_prompt(sample_diff)

        # Check for EXAMPLES section
        assert "EXAMPLES" in prompt or "examples" in prompt.lower()

        # Check for at least 2 example commits
        example_count = sum(
            1
            for line in prompt.split("\n")
            if line.strip().startswith(("feat(", "fix(", "test(", "docs("))
        )
        assert example_count >= 2, f"Expected 2+ examples, found {example_count}"

    def test_prompt_mentions_why_vs_what(self, sample_diff: GitDiff) -> None:
        """T122: Improved prompt mentions WHY vs WHAT principle."""
        provider = OllamaProvider()
        prompt = provider._build_prompt(sample_diff)

        # Check for WHY or "reasoning" or "context" keywords
        assert any(
            keyword in prompt for keyword in ["WHY", "why", "reasoning", "context"]
        )

    def test_prompt_requests_body_for_significant_changes(
        self, sample_diff: GitDiff
    ) -> None:
        """T123: Improved prompt requests body for significant changes."""
        provider = OllamaProvider()
        prompt = provider._build_prompt(sample_diff)

        # Check for body instructions
        assert any(
            keyword in prompt.lower()
            for keyword in ["body", "paragraph", "explaining"]
        )

    def test_prompt_enforces_imperative_mood(self, sample_diff: GitDiff) -> None:
        """T124: Improved prompt enforces imperative mood."""
        provider = OllamaProvider()
        prompt = provider._build_prompt(sample_diff)

        # Check for imperative instructions
        assert "imperative" in prompt.lower() or any(
            word in prompt for word in ['"add"', '"fix"', '"update"']
        )

    def test_prompt_shows_diff_statistics(self, sample_diff: GitDiff) -> None:
        """T125: Improved prompt shows diff statistics."""
        provider = OllamaProvider()
        prompt = provider._build_prompt(sample_diff)

        # Check for additions and deletions count
        assert "+40" in prompt or "40" in prompt  # total_additions
        assert "-8" in prompt or "8" in prompt  # total_deletions

    def test_prompt_limits_file_list_to_10(self) -> None:
        """T126: Prompt limits file list to 10 files max."""
        # Create diff with 15 files
        files = [
            FileDiff(
                path=f"src/file{i}.py",
                change_type="modified",
                additions=i,
                deletions=1,
                diff_content="",
            )
            for i in range(15)
        ]
        diff = GitDiff(files=files, total_additions=105, total_deletions=15)

        provider = OllamaProvider()
        prompt = provider._build_prompt(diff)

        # Count file references in prompt
        file_count = sum(1 for line in prompt.split("\n") if "src/file" in line)
        assert file_count <= 10, f"Expected ≤10 files in prompt, found {file_count}"


class TestOllamaGenerationParameters:
    """Tests for Ollama generation parameters (Feature 009)."""

    def test_stream_response_builds_payload_with_options(self) -> None:
        """T127-T130: _stream_response builds payload with all generation options."""
        import inspect
        from gitcommit_ai.providers.ollama import OllamaProvider

        provider = OllamaProvider()

        # Read the _stream_response source code to verify payload structure
        source = inspect.getsource(provider._stream_response)

        # Verify all required options are in the source code
        assert '"temperature": 0.3' in source, "temperature=0.3 not found in payload"
        assert '"top_p": 0.9' in source, "top_p=0.9 not found in payload"
        assert '"top_k": 40' in source, "top_k=40 not found in payload"
        assert '"num_predict": 256' in source, "num_predict=256 not found in payload"
        assert '"options"' in source, "options dict not found in payload"
