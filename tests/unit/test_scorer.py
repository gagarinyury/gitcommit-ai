"""Tests for CommitScorer."""

from gitcommit_ai.action.scorer import CommitScorer


class TestCommitScorer:
    """Test suite for CommitScorer."""

    def test_score_high_quality_commit(self) -> None:
        """Scores high-quality commit 80-100."""
        scorer = CommitScorer()
        score = scorer.score("feat(api): implement user authentication endpoint")

        assert 80 <= score <= 100

    def test_score_medium_quality_commit(self) -> None:
        """Scores medium-quality commit 50-79."""
        scorer = CommitScorer()
        score = scorer.score("fix: bug fix")

        assert 50 <= score <= 79

    def test_score_low_quality_commit(self) -> None:
        """Scores low-quality commit 0-49."""
        scorer = CommitScorer()
        score = scorer.score("fix stuff")

        assert 0 <= score <= 49

    def test_score_perfect_commit(self) -> None:
        """Scores perfect commit close to 100."""
        scorer = CommitScorer()
        score = scorer.score(
            "feat(auth): implement JWT token-based authentication"
        )

        assert score >= 90

    def test_score_no_type(self) -> None:
        """Penalizes missing type heavily."""
        scorer = CommitScorer()
        score = scorer.score("add new feature")

        assert score < 40  # Missing type = -40 points

    def test_get_issues_identifies_problems(self) -> None:
        """Identifies issues in commit message."""
        scorer = CommitScorer()
        issues = scorer.get_issues("fix stuff")

        assert len(issues) > 0
        assert any("generic" in issue.lower() for issue in issues)

    def test_get_issues_no_problems(self) -> None:
        """Returns empty list for good commit."""
        scorer = CommitScorer()
        issues = scorer.get_issues("feat(api): add user endpoint")

        assert len(issues) == 0

    def test_score_too_short_description(self) -> None:
        """Penalizes very short descriptions."""
        scorer = CommitScorer()
        score = scorer.score("feat: add")

        assert score < 70  # Too short

    def test_score_too_long_description(self) -> None:
        """Penalizes very long descriptions."""
        scorer = CommitScorer()
        long_msg = "feat: " + "a" * 100
        score = scorer.score(long_msg)

        assert score < 90  # Too long
