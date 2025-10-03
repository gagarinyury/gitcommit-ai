# GitCommit AI

AI-powered git commit message generator using OpenAI, Anthropic, or **Ollama (local, free!)**.

## Features

- 🤖 **7 AI Providers**: OpenAI, Anthropic, Gemini, Mistral, Cohere, DeepSeek, Ollama (local)
- 🔄 **Git Hooks**: Auto-generate messages on every commit
- 📝 **Conventional Commits**: Follows type(scope): description format
- ⚡ **Fast**: <3s generation with cloud APIs, <10s with local models
- 🔒 **Privacy**: Run 100% offline with Ollama
- 📊 **Statistics**: Track usage, success rate, and provider performance

## Installation

```bash
pip install gitcommit-ai
```

**🎉 Works out-of-the-box with Ollama (FREE, no API keys needed!)** or configure cloud providers for premium quality.

## Configuration

### Quick Setup (3 ways):

**Option 1: Environment Variables (Recommended)**
```bash
# Add to ~/.zshrc or ~/.bashrc
export OPENAI_API_KEY="sk-proj-your-key-here"
source ~/.zshrc
```

**Option 2: .env File (Per-Project)**
```bash
# Create .env in your git repo
echo "OPENAI_API_KEY=sk-proj-..." > .env
echo ".env" >> .gitignore
```

**Option 3: DeepSeek (CHEAPEST Cloud Option!)**
```bash
# Add to ~/.zshrc or ~/.bashrc
export DEEPSEEK_API_KEY="sk-..."
gitcommit-ai generate --provider deepseek
```

**Option 4: Ollama (FREE, No API Key!) - Default** ⭐
```bash
# Quick setup wizard (recommended)
pip install gitcommit-ai
gitcommit-ai setup-ollama  # Interactive setup with auto-detection

# Or manual installation
brew install ollama  # macOS
# curl https://ollama.ai/install.sh | sh  # Linux
ollama pull qwen2.5:7b  # Best quality model (4.7GB)
gitcommit-ai generate  # Uses Ollama automatically!
```

💡 **Tip**: Use `gitcommit-ai providers` to see all available providers and their configuration status

### Where to get API keys:
- **OpenAI**: https://platform.openai.com/api-keys
- **Anthropic**: https://console.anthropic.com/settings/keys
- **Gemini**: https://aistudio.google.com/apikey
- **DeepSeek**: https://platform.deepseek.com (💰 **$0.27/1M tokens - cheapest!**)
- **Ollama**: No key needed (local AI)

## Quick Start

### 1. Generate Your First Commit Message

```bash
# Stage your changes
git add .

# Generate commit message (uses Ollama by default - FREE!)
gitcommit-ai generate
```

**Example Output:**
```
feat(auth): implement JWT-based authentication system

Adds secure token-based authentication with refresh tokens and
role-based access control to protect API endpoints.
```

### 2. Generate with Ollama (local, free!)

```bash
# Install Ollama: https://ollama.ai
ollama pull qwen2.5:7b  # Recommended for best quality

# Generate message
gitcommit-ai generate --provider ollama
```

### 3. Install Git Hooks (automation!)

```bash
# Install hook once
gitcommit-ai install-hooks

# Now every `git commit` auto-generates AI message!
git commit  # Opens editor with AI-generated message
```

**How it works:**
1. You run `git commit` (without `-m` flag)
2. GitCommit AI analyzes your staged changes
3. Opens your editor with a pre-filled, AI-generated commit message
4. You can edit or accept it as-is

### 4. Multiple Suggestions (Pick the Best One!)

```bash
# Generate 3 suggestions and pick interactively
gitcommit-ai generate --count 3

# Output:
# 1. feat(api): add user authentication endpoint
# 2. feat(auth): implement JWT login functionality
# 3. feat(backend): create secure user login system
# Select (1-3): _
```

## Commands

### Generate

```bash
gitcommit-ai generate [OPTIONS]
```

Options:
- `--provider`: `openai`, `anthropic`, `gemini`, `mistral`, `cohere`, `deepseek`, `ollama` (default: auto-detect)
- `--model`: Model name (provider-specific, e.g., `qwen2.5:7b` for Ollama)
- `--json`: Output in JSON format
- `--verbose`: Show detailed logs
- `--gitmoji`: Add emoji prefix (e.g., `✨ feat: add feature`)
- `--no-gitmoji`: Disable emoji prefix
- `--count N`: Generate N suggestions (1-10) and pick interactively

#### Multiple Suggestions

```bash
# Generate 3 suggestions and pick interactively
gitcommit-ai generate --count 3

# Generate 5 suggestions as JSON
gitcommit-ai generate --count 5 --json
```

#### Gitmoji Examples

```bash
# With emoji
gitcommit-ai generate --gitmoji
# Output: ✨ feat(auth): add JWT support

# Without emoji (default)
gitcommit-ai generate
# Output: feat(auth): add JWT support
```

**Supported Emojis:**
- ✨ feat - New feature
- 🐛 fix - Bug fix
- 📝 docs - Documentation
- 🎨 style - Formatting
- ♻️ refactor - Code refactoring
- ✅ test - Tests
- 🔧 chore - Maintenance
- 🚀 perf - Performance
- 🔒 security - Security
- 💥 breaking - Breaking changes

### Hooks

```bash
# Install
gitcommit-ai install-hooks [--force]

# Uninstall
gitcommit-ai uninstall-hooks [--force]

# Debug
gitcommit-ai debug-hooks
```

### Setup

```bash
# Interactive Ollama setup wizard (recommended for first-time users)
gitcommit-ai setup-ollama
```

Automatically detects your OS, checks Ollama installation, and downloads the recommended model with size confirmation.

### Providers

```bash
# List all available providers
gitcommit-ai providers
```

Shows configured status, models, and setup instructions for each provider.

### Statistics

```bash
# Show all stats
gitcommit-ai stats

# Filter by provider
gitcommit-ai stats --provider ollama

# Filter by time period
gitcommit-ai stats --days 7

# Export to file
gitcommit-ai stats --export csv
gitcommit-ai stats --export json
```

Track commit generation history, success rates, response times, and provider usage.

### Validate PR (GitHub Actions)

```bash
gitcommit-ai validate-pr [--json] [--strict] [--provider PROVIDER]
```

Validates conventional commit format in pull requests. See [GitHub Action setup](.github/workflows/validate-commits.yml).

## Supported Models

### OpenAI
- gpt-4o ✅ (recommended)
- gpt-4o-mini (faster, cheaper)

### Anthropic
- claude-3-5-sonnet ✅ (recommended)
- claude-3-opus
- claude-3-haiku

### Google Gemini
- gemini-2.0-flash-001 ✅ (recommended)
- gemini-2.5-flash

### Mistral
- mistral-small ✅ (recommended)
- mistral-tiny

### Cohere
- command ✅ (recommended)
- command-light

### DeepSeek (Cheapest!)
- deepseek-chat ✅ (recommended, $0.27/1M tokens)
- deepseek-coder (code-focused)

### Ollama (Local & Free!)
- **qwen2.5:7b** ✅ (recommended, 4.7GB, best quality)
- qwen2.5:3b (faster, 1.9GB, good quality)
- llama3.2 (alternative, 2GB)
- codellama (code-focused, 4GB)

### Quality Improvements: Before/After

**Recent Ollama improvements** (prompt engineering + generation parameters):

**Before** (generic, no context):
```
feat: add user authentication
```

**After** (with improved prompt):
```
feat(auth): implement JWT-based authentication system

Adds secure token-based authentication with refresh tokens and
role-based access control to protect API endpoints.
```

**Key improvements:**
- ✅ More specific scope identification (`auth` vs generic)
- ✅ Body paragraphs for significant changes (explains WHY)
- ✅ Imperative mood enforcement ("implement" not "implemented")
- ✅ Technical accuracy (qwen2.5:7b understands code context)

**Generation parameters optimized for quality:**
- `temperature=0.3` - More consistent, less random
- `top_p=0.9` - Quality sampling
- `num_predict=256` - Allows body generation

## Configuration

### Environment Variables

```bash
# Cloud providers
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."

# Ollama (optional)
export OLLAMA_HOST="http://localhost:11434"  # default
export OLLAMA_DEFAULT_MODEL="llama3.2"       # default
```

## Exit Codes

- `0`: Success
- `1`: Git error (not a repo, no staged changes)
- `2`: API error (network, rate limit)
- `3`: Configuration error (missing API key)
- `4`: Ollama not installed
- `5`: Ollama model not found
- `6`: Hooks error

## Development

### Run tests

```bash
pytest tests/ -v
```

### Type checking

```bash
mypy src/
```

### Linting

```bash
ruff check src/ tests/
```

## License

MIT
test change
