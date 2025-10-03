# Quickstart: OpenRouter Provider

**Feature**: Add OpenRouter Provider, Remove Mistral/Cohere
**Date**: 2025-10-03

## Prerequisites

```bash
# Install/upgrade gitcommit-ai
pip install --upgrade gitcommit-ai

# Get OpenRouter API key (free tier available)
# Visit: https://openrouter.ai/keys
export OPENROUTER_API_KEY="sk-or-v1-..."
```

## Basic Usage

### 1. Generate Commit Message with OpenRouter

```bash
# Stage your changes
git add src/api/auth.py

# Generate commit message using OpenRouter (GPT-4o-mini)
gitcommit-ai generate --provider openrouter --model openai/gpt-4o-mini
```

**Expected Output:**
```
feat(api): add JWT authentication endpoint

Implements secure token-based authentication with refresh tokens
and role-based access control.
```

### 2. Try Different Models Through OpenRouter

```bash
# Use Claude 3.5 Sonnet via OpenRouter
gitcommit-ai generate --provider openrouter --model anthropic/claude-3-5-sonnet

# Use Gemini 2.0 Flash via OpenRouter
gitcommit-ai generate --provider openrouter --model google/gemini-2.0-flash-exp

# Use Mistral Large via OpenRouter
gitcommit-ai generate --provider openrouter --model mistral/mistral-large

# Use Cohere Command R+ via OpenRouter
gitcommit-ai generate --provider openrouter --model cohere/command-r-plus
```

### 3. Check Available Providers

```bash
gitcommit-ai providers
```

**Expected Output:**
```
Available AI Providers:

✅ ollama (default)
   Status: Configured
   Models: qwen2.5:7b, llama3.2, codellama
   Setup: brew install ollama && ollama pull qwen2.5:7b

✅ openrouter
   Status: Configured (OPENROUTER_API_KEY found)
   Models: 100+ models including:
     - openai/gpt-4o, openai/gpt-4o-mini
     - anthropic/claude-3-5-sonnet, anthropic/claude-3-haiku
     - google/gemini-2.0-flash-exp
     - mistral/mistral-large, cohere/command-r-plus
   Setup: Get key at https://openrouter.ai/keys

✅ openai
   Status: Configured (OPENAI_API_KEY found)
   Models: gpt-4o, gpt-4o-mini

✅ anthropic
   Status: Configured (ANTHROPIC_API_KEY found)
   Models: claude-3-opus, claude-3-5-sonnet

... (other providers)
```

## Advanced Usage

### 4. JSON Output

```bash
gitcommit-ai generate --provider openrouter --model openai/gpt-4o-mini --json
```

**Expected Output:**
```json
{
  "type": "feat",
  "scope": "api",
  "description": "add JWT authentication endpoint",
  "body": "Implements secure token-based authentication with refresh tokens and role-based access control.",
  "breaking_change": false
}
```

### 5. Gitmoji Support

```bash
gitcommit-ai generate --provider openrouter --model anthropic/claude-3-haiku --gitmoji
```

**Expected Output:**
```
✨ feat(api): add JWT authentication endpoint
```

### 6. Multiple Suggestions

```bash
gitcommit-ai generate --provider openrouter --model openai/gpt-4o-mini --count 3
```

**Expected Output:**
```
1. feat(api): add JWT authentication endpoint
2. feat(auth): implement token-based user login
3. feat(security): add authentication middleware
Select (1-3):
```

## Migration from Mistral/Cohere

### If You Were Using Mistral

**Before (direct Mistral provider - will be removed):**
```bash
export MISTRAL_API_KEY="..."
gitcommit-ai generate --provider mistral --model mistral-tiny
```

**After (via OpenRouter):**
```bash
export OPENROUTER_API_KEY="sk-or-v1-..."
gitcommit-ai generate --provider openrouter --model mistral/mistral-tiny
```

### If You Were Using Cohere

**Before (direct Cohere provider - will be removed):**
```bash
export COHERE_API_KEY="..."
gitcommit-ai generate --provider cohere --model command-light
```

**After (via OpenRouter):**
```bash
export OPENROUTER_API_KEY="sk-or-v1-..."
gitcommit-ai generate --provider openrouter --model cohere/command-light
```

## Error Handling

### Invalid API Key

```bash
export OPENROUTER_API_KEY="invalid-key"
gitcommit-ai generate --provider openrouter --model openai/gpt-4o-mini
```

**Expected Error:**
```
Error: Invalid OpenRouter API key

Get your API key at: https://openrouter.ai/keys
Then: export OPENROUTER_API_KEY="sk-or-v1-..."
```

### Invalid Model Format

```bash
gitcommit-ai generate --provider openrouter --model gpt-4o
```

**Expected Error:**
```
Error: Invalid model format 'gpt-4o'

OpenRouter models must be in format: vendor/model-name

Popular models:
  - openai/gpt-4o
  - anthropic/claude-3-5-sonnet
  - google/gemini-2.0-flash-exp
  - mistral/mistral-large
  - cohere/command-r-plus
```

### OpenRouter Service Unavailable

```bash
gitcommit-ai generate --provider openrouter --model openai/gpt-4o-mini
# (when OpenRouter is down)
```

**Expected Error:**
```
Error: OpenRouter service unavailable (503)

Try alternative providers:
  --provider openai        (if OPENAI_API_KEY configured)
  --provider anthropic     (if ANTHROPIC_API_KEY configured)
  --provider deepseek      (if DEEPSEEK_API_KEY configured)
  --provider ollama        (local, free - no key needed)
```

## Configuration via .env File

Create `.env` in your project root:

```bash
# OpenRouter (recommended - access to 100+ models)
OPENROUTER_API_KEY=sk-or-v1-...

# Fallback providers (optional)
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-...
DEEPSEEK_API_KEY=sk-...

# Ollama (default - local, free)
# No configuration needed if installed
```

## Validation Tests

### Test 1: Basic Generation

```bash
# Setup
git init test-repo && cd test-repo
echo "print('hello')" > main.py
git add main.py

# Test
gitcommit-ai generate --provider openrouter --model openai/gpt-4o-mini

# Expected: Valid commit message in conventional format
# Pass criteria: type(scope): description format, <72 chars
```

### Test 2: Provider Fallback on Error

```bash
# Setup
export OPENROUTER_API_KEY="invalid"
export OPENAI_API_KEY="valid-key"

# Test (OpenRouter fails)
gitcommit-ai generate --provider openrouter --model openai/gpt-4o-mini
# Expected: Clear error message

# Test (manual fallback)
gitcommit-ai generate --provider openai --model gpt-4o-mini
# Expected: Works with direct OpenAI

# Pass criteria: Error message suggests alternative providers
```

### Test 3: Backward Compatibility

```bash
# Test: Existing providers still work
gitcommit-ai generate --provider openai
gitcommit-ai generate --provider anthropic
gitcommit-ai generate --provider ollama

# Expected: All work as before
# Pass criteria: No breaking changes, 273 existing tests pass
```

### Test 4: Model Validation

```bash
# Test: Invalid model format caught
gitcommit-ai generate --provider openrouter --model invalid-format

# Expected: Error with format explanation + suggestions
# Pass criteria: Clear validation error, helpful message
```

## Performance Benchmarks

**Target**: <2 seconds for commit message generation

```bash
# Benchmark OpenRouter (GPT-4o-mini)
time gitcommit-ai generate --provider openrouter --model openai/gpt-4o-mini
# Expected: ~1-2s (mostly API latency)

# Benchmark Claude via OpenRouter
time gitcommit-ai generate --provider openrouter --model anthropic/claude-3-haiku
# Expected: ~1-3s (varies by model)

# Pass criteria: <2s for small diffs (<1000 lines)
```

## Next Steps

After completing this quickstart:

1. ✅ OpenRouter provider functional
2. ✅ Mistral/Cohere accessible via OpenRouter
3. ✅ Error handling tested
4. ✅ Backward compatibility verified
5. ✅ Performance acceptable

**Ready for**: Task execution (`/tasks` command)
