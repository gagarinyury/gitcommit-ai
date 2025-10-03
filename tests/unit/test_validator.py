"""Tests for CommitValidator."""

from gitcommit_ai.action.validator import CommitValidator


class TestCommitValidator:
    """Test suite for CommitValidator."""

    def test_validate_conventional_valid_feat(self) -> None:
        """Validates feat commit."""
        validator = CommitValidator()
        is_valid, issues = validator.validate_conventional("feat: add new feature")

        assert is_valid is True
        assert len(issues) == 0

    def test_validate_conventional_valid_with_scope(self) -> None:
        """Validates commit with scope."""
        validator = CommitValidator()
        is_valid, issues = validator.validate_conventional("fix(auth): resolve login bug")

        assert is_valid is True
        assert len(issues) == 0

    def test_validate_conventional_valid_with_breaking_change(self) -> None:
        """Validates commit with breaking change marker."""
        validator = CommitValidator()
        is_valid, issues = validator.validate_conventional("feat!: breaking API change")

        assert is_valid is True
        assert len(issues) == 0

    def test_validate_conventional_invalid_no_type(self) -> None:
        """Rejects commit without type."""
        validator = CommitValidator()
        is_valid, issues = validator.validate_conventional("add new feature")

        assert is_valid is False
        assert "Missing commit type" in issues[0]

    def test_validate_conventional_invalid_type(self) -> None:
        """Rejects commit with invalid type."""
        validator = CommitValidator()
        is_valid, issues = validator.validate_conventional("invalid: wrong type")

        assert is_valid is False
        assert "Invalid commit type" in issues[0]

    def test_validate_conventional_empty_message(self) -> None:
        """Rejects empty commit message."""
        validator = CommitValidator()
        is_valid, issues = validator.validate_conventional("")

        assert is_valid is False
        assert "Empty commit message" in issues[0]

    def test_validate_conventional_no_description(self) -> None:
        """Rejects commit without description."""
        validator = CommitValidator()
        is_valid, issues = validator.validate_conventional("feat:")

        assert is_valid is False
        assert "Missing description" in issues[0]
