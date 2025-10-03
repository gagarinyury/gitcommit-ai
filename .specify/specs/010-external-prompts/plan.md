# Implementation Plan: External Prompt Templates

## Architecture

### Directory Structure
```
src/gitcommit_ai/prompts/
├── __init__.py
├── loader.py                    # PromptLoader class
├── templates/                   # Default templates (bundled)
│   ├── openai.txt
│   ├── anthropic.txt
│   ├── deepseek.txt
│   ├── ollama.txt
│   ├── gemini.txt
│   ├── mistral.txt
│   └── cohere.txt
└── README.md

~/.gitcommit-ai/prompts/        # User overrides (optional)
├── openai.txt
└── deepseek.txt
```

### Template Format
```txt
# Simple text file with variable placeholders
You are an expert developer.

CHANGES:
{diff_content}

STATISTICS:
Total: {total_additions} additions, {total_deletions} deletions

Write a conventional commit message...
```

### Variables Available
- `{diff_content}` - Formatted diff with file changes
- `{file_list}` - Simple list of changed files
- `{total_additions}` - Number of added lines
- `{total_deletions}` - Number of deleted lines
- `{file_count}` - Number of files changed

## Components

### 1. PromptLoader Class (`prompts/loader.py`)

```python
class PromptLoader:
    """Loads and renders prompt templates."""

    def __init__(self):
        self.default_dir = Path(__file__).parent / "templates"
        self.user_dir = Path.home() / ".gitcommit-ai" / "prompts"
        self._cache = {}

    def load(self, provider: str) -> str:
        """Load template for provider (user override or default)."""

    def render(self, template: str, **variables) -> str:
        """Render template with variables."""
```

### 2. Update Providers

Each provider's `_build_prompt()` becomes:
```python
def _build_prompt(self, diff: GitDiff) -> str:
    from gitcommit_ai.prompts import PromptLoader

    loader = PromptLoader()
    template = loader.load("deepseek")

    return loader.render(
        template,
        diff_content=self._format_diff(diff),
        file_list=self._format_files(diff),
        total_additions=diff.total_additions,
        total_deletions=diff.total_deletions,
        file_count=len(diff.files)
    )
```

## Migration Strategy

### Phase 1: Create Infrastructure (TDD)
1. Write tests for PromptLoader
2. Implement PromptLoader class
3. Create default template files

### Phase 2: Migrate One Provider (DeepSeek)
1. Extract current DeepSeek prompt to template file
2. Update DeepSeek to use PromptLoader
3. Verify tests pass

### Phase 3: Migrate All Providers
1. Extract prompts for all providers
2. Update all providers to use PromptLoader
3. Verify all tests pass

### Phase 4: Documentation
1. Add README.md to prompts/templates/
2. Update main README with customization guide
3. Add examples of custom prompts

## Testing Strategy

### Unit Tests (`test_prompt_loader.py`)
- `test_loads_default_template` - Loads from templates/
- `test_loads_user_override` - Prefers ~/.gitcommit-ai/prompts/
- `test_renders_variables` - Substitutes {var} correctly
- `test_caches_templates` - Doesn't reload every time
- `test_handles_missing_template` - Falls back or errors

### Integration Tests
- `test_deepseek_uses_template` - DeepSeek loads external prompt
- `test_user_override_works` - Custom prompt actually used

## File Contents Preview

### `templates/deepseek.txt`
```txt
You are an expert developer writing a git commit message.

CHANGES:
{diff_content}

STATISTICS:
Total: +{total_additions} -{total_deletions} lines across {file_count} file(s)

TASK: Write a precise conventional commit message based on ACTUAL code changes above.

FORMAT:
type(scope): brief description

[Optional body explaining WHY]
```

### `templates/ollama.txt`
```txt
You are an expert software engineer writing git commit messages.

FILES CHANGED:
{file_list}

Total changes: +{total_additions} -{total_deletions} lines

TASK:
1. Determine type: feat, fix, test, docs, refactor, chore
2. Specify scope (module/component)
3. Write imperative description (<50 chars)
4. Add body (2-3 sentences) explaining WHY if significant

EXAMPLES:
feat(auth): implement JWT authentication

fix(parser): handle edge case in diff parsing
Fixes crash when diff contains binary files.

FORMAT:
type(scope): description

[body]
```

## Rollout Plan

1. **PR 1:** Infrastructure + DeepSeek migration
2. **PR 2:** Migrate all other providers
3. **PR 3:** Documentation + examples

## Risks & Mitigation

| Risk | Mitigation |
|------|------------|
| Breaking changes | Keep backward compat, fallback to hardcoded |
| Template syntax errors | Validate on load, clear error messages |
| Performance hit | Cache loaded templates |
| User confusion | Great docs + examples |
