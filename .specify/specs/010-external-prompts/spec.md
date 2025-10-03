# External Prompt Templates System

**Status:** Draft
**Created:** 2025-10-03
**Priority:** Medium

## Problem

Currently, AI prompts are hardcoded inside each provider class, making it:
- Hard to modify prompts without changing code
- Impossible for users to customize prompts
- Difficult to A/B test different prompt versions
- No way to share/version prompts separately

## Solution

Implement external prompt template system where:
- Each provider has a `.txt` template file
- Templates support variable substitution (`{diff_content}`, `{stats}`)
- Users can override templates in `~/.gitcommit-ai/prompts/`
- Templates are version controlled and easy to edit

## User Stories

### As a developer
- I want to easily tweak prompts to get better commit messages
- I want to see prompt history in git
- I want to test different prompt variations

### As a power user
- I want to create custom prompts for specific providers
- I want to share my prompt templates with team
- I want to override default prompts without modifying code

## Requirements

### Functional
1. Load prompt templates from files (not hardcoded)
2. Support variable substitution in templates
3. Allow user overrides in `~/.gitcommit-ai/prompts/`
4. Fallback to default if custom template missing
5. Each provider has its own template file

### Non-Functional
1. No performance degradation (templates cached)
2. Clear error messages if template malformed
3. Backward compatible (existing code works)
4. Well documented for users

## Success Criteria

- [ ] All providers use external templates
- [ ] User can override any provider's prompt
- [ ] Templates are human-readable and well-commented
- [ ] Documentation explains customization
- [ ] All tests pass with new system

## Out of Scope

- GUI for editing prompts
- Prompt validation/linting
- Multi-language prompts
- AI-assisted prompt generation
