# Feature Specification: GitHub Action for CI/CD

**Feature Branch**: `007-github-action`
**Created**: 2025-10-02
**Status**: Draft
**Priority**: Medium (automation for teams)

## User Scenarios & Testing

### Primary User Story
A development team wants to automatically validate commit messages in PRs using AI. They add GitCommit AI GitHub Action to their workflow, which checks if commit messages follow conventions and suggests improvements.

### Acceptance Scenarios

1. **Given** action configured, **When** PR opened, **Then** action validates all commit messages in PR

2. **Given** commits have poor messages, **When** action runs, **Then** bot comments with AI-generated suggestions

3. **Given** all commits follow conventions, **When** action runs, **Then** green checkmark (no comments)

4. **Given** action configured with `auto-fix: true`, **When** bad commit detected, **Then** bot auto-amends with AI message

5. **Given** action fails, **When** error occurs, **Then** workflow continues (doesn't block merge)

### Edge Cases
- 100+ commits in PR? → Batch validation, sample analysis
- API rate limits in action? → Use GitHub-provided API quotas
- Fork PRs (no secrets)? → Skip validation or use public models
- Multiple workflows? → De-duplicate comments

## Requirements

### Functional Requirements

**Action Configuration**
- **FR-114**: Action MUST be distributable via GitHub Marketplace
- **FR-115**: Action MUST support configuration via `with:` parameters
- **FR-116**: Action MUST read API keys from repository secrets
- **FR-117**: Action MUST support multiple providers (OpenAI, Anthropic, Ollama)

**Validation Mode**
- **FR-118**: Action MUST validate commit messages against conventional commits
- **FR-119**: Action MUST score each commit (0-100) based on quality
- **FR-120**: Action MUST post PR comment with validation results
- **FR-121**: Action MUST support `strict-mode: true` to fail workflow on bad commits

**Suggestion Mode**
- **FR-122**: Action MUST generate AI suggestions for poor commits
- **FR-123**: Action MUST format suggestions as PR review comments
- **FR-124**: Action MUST link to original commit SHA
- **FR-125**: Action MUST avoid duplicate comments (track commented commits)

**Auto-Fix Mode**
- **FR-126**: Action MUST support `auto-fix: true` to amend commits automatically
- **FR-127**: Action MUST create fixup commits with AI messages
- **FR-128**: Action MUST require write permissions for auto-fix
- **FR-129**: Action MUST preserve commit authorship (Co-authored-by)

**Performance**
- **FR-130**: Action MUST complete in <2 minutes for typical PRs (<20 commits)
- **FR-131**: Action MUST cache AI responses to avoid redundant API calls
- **FR-132**: Action MUST run in parallel for multiple commits

**Output**
- **FR-133**: Action MUST output summary table in job logs
- **FR-134**: Action MUST set output variables: `total_commits`, `valid_commits`, `invalid_commits`
- **FR-135**: Action MUST support JSON output for downstream actions

### Key Entities

- **ActionRunner**: Main entrypoint for GitHub Action
- **CommitValidator**: Validates commit message quality
- **PRCommentPoster**: Posts suggestions to PR
- **CommitAmender**: Auto-fixes commits in auto-fix mode

---

## Workflow Configuration Example

```yaml
name: Validate Commit Messages

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  validate-commits:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for commit analysis

      - uses: gitcommit-ai/action@v1
        with:
          provider: openai
          mode: suggest  # validate | suggest | auto-fix
          strict-mode: false
          gitmoji: true
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

---

## Example PR Comment

```markdown
## 🤖 GitCommit AI Analysis

Analyzed **3 commits** in this PR:

| Commit | Score | Status | Suggestion |
|--------|-------|--------|-----------|
| `abc123` | 95 | ✅ Pass | - |
| `def456` | 60 | ⚠️ Needs Improvement | `fix(api): resolve timeout in user endpoint` |
| `ghi789` | 30 | ❌ Fail | `feat(auth): implement JWT token refresh mechanism` |

### Recommendations:
- Commit `def456`: Current message too vague ("fix stuff")
- Commit `ghi789`: Missing conventional commit type

[View full analysis](https://github.com/owner/repo/actions/runs/123456)
```

---

## Action Inputs

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `provider` | No | `openai` | AI provider (openai, anthropic, ollama) |
| `model` | No | `gpt-4o-mini` | Model to use |
| `mode` | No | `suggest` | Action mode: validate \| suggest \| auto-fix |
| `strict-mode` | No | `false` | Fail workflow on bad commits |
| `gitmoji` | No | `false` | Use gitmoji in suggestions |
| `min-score` | No | `70` | Minimum quality score (0-100) |

---

## Action Outputs

| Output | Description |
|--------|-------------|
| `total_commits` | Total commits analyzed |
| `valid_commits` | Commits passing quality check |
| `invalid_commits` | Commits failing quality check |
| `average_score` | Average quality score |
| `json_results` | Full results in JSON format |

---

## Technical Constraints

- GitHub Actions run on Linux (Ubuntu)
- Action timeout: 360 minutes max (use <2 min)
- Secrets available only in non-fork PRs
- Rate limits: 1000 API requests/hour per repo
- Docker-based actions are slower (use Node.js action)

---

## Out of Scope (for MVP)

- GitLab CI/CD integration
- Bitbucket Pipelines support
- Custom quality rules configuration
- ML-based commit classification
- Slack/Discord notifications

---

## Success Criteria

- ✅ Action published to GitHub Marketplace
- ✅ Works in public and private repos
- ✅ Validates commits correctly
- ✅ Suggestions are helpful and accurate
- ✅ Doesn't block legitimate PRs
- ✅ Documentation with examples
