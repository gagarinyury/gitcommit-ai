"""Tests for git diff parser."""
import pytest

from gitcommit_ai.core.diff_parser import DiffParser
from gitcommit_ai.generator.message import FileDiff, GitDiff


class TestParseDiff:
    """Test unified diff parsing."""

    def test_parse_single_file_modification(self) -> None:
        """Parses diff for single modified file."""
        diff_text = """diff --git a/src/main.py b/src/main.py
index 1234567..abcdefg 100644
--- a/src/main.py
+++ b/src/main.py
@@ -10,6 +10,9 @@ def old_function():
     return True


+def new_function():
+    return False
+
 def another_function():
     pass
"""
        git_diff = DiffParser.parse(diff_text)
        assert isinstance(git_diff, GitDiff)
        assert len(git_diff.files) == 1

        file_diff = git_diff.files[0]
        assert file_diff.path == "src/main.py"
        assert file_diff.change_type == "modified"
        assert file_diff.additions == 3
        assert file_diff.deletions == 0

    def test_parse_added_file(self) -> None:
        """Parses diff for newly added file."""
        diff_text = """diff --git a/src/new.py b/src/new.py
new file mode 100644
index 0000000..1234567
--- /dev/null
+++ b/src/new.py
@@ -0,0 +1,5 @@
+def hello():
+    print("Hello, world!")
+
+if __name__ == "__main__":
+    hello()
"""
        git_diff = DiffParser.parse(diff_text)
        assert len(git_diff.files) == 1

        file_diff = git_diff.files[0]
        assert file_diff.path == "src/new.py"
        assert file_diff.change_type == "added"
        assert file_diff.additions == 5
        assert file_diff.deletions == 0

    def test_parse_deleted_file(self) -> None:
        """Parses diff for deleted file."""
        diff_text = """diff --git a/src/old.py b/src/old.py
deleted file mode 100644
index 1234567..0000000
--- a/src/old.py
+++ /dev/null
@@ -1,3 +0,0 @@
-def old_code():
-    pass
-
"""
        git_diff = DiffParser.parse(diff_text)
        assert len(git_diff.files) == 1

        file_diff = git_diff.files[0]
        assert file_diff.path == "src/old.py"
        assert file_diff.change_type == "deleted"
        assert file_diff.additions == 0
        assert file_diff.deletions == 3

    def test_parse_multiple_files(self) -> None:
        """Parses diff with multiple files."""
        diff_text = """diff --git a/src/a.py b/src/a.py
index 123..456 100644
--- a/src/a.py
+++ b/src/a.py
@@ -1,2 +1,3 @@
+import os
 def func_a():
     pass
diff --git a/src/b.py b/src/b.py
index 789..abc 100644
--- a/src/b.py
+++ b/src/b.py
@@ -1,3 +1,2 @@
-import sys
 def func_b():
     pass
"""
        git_diff = DiffParser.parse(diff_text)
        assert len(git_diff.files) == 2
        assert git_diff.files[0].path == "src/a.py"
        assert git_diff.files[1].path == "src/b.py"
        assert git_diff.total_additions == 1
        assert git_diff.total_deletions == 1

    def test_parse_empty_diff(self) -> None:
        """Returns empty GitDiff for empty string."""
        git_diff = DiffParser.parse("")
        assert isinstance(git_diff, GitDiff)
        assert len(git_diff.files) == 0
        assert git_diff.total_additions == 0
        assert git_diff.total_deletions == 0


class TestExtractStats:
    """Test diff statistics extraction."""

    def test_extract_additions_from_hunk(self) -> None:
        """Counts additions correctly from diff hunk."""
        hunk = """@@ -1,2 +1,4 @@
 existing line
+added line 1
+added line 2
 existing line 2
"""
        additions = DiffParser._count_additions(hunk)
        assert additions == 2

    def test_extract_deletions_from_hunk(self) -> None:
        """Counts deletions correctly from diff hunk."""
        hunk = """@@ -1,4 +1,2 @@
 existing line
-deleted line 1
-deleted line 2
 existing line 2
"""
        deletions = DiffParser._count_deletions(hunk)
        assert deletions == 2

    def test_extract_mixed_changes(self) -> None:
        """Counts additions and deletions in mixed hunk."""
        hunk = """@@ -1,3 +1,3 @@
 existing line
-old line
+new line
 existing line 2
"""
        additions = DiffParser._count_additions(hunk)
        deletions = DiffParser._count_deletions(hunk)
        assert additions == 1
        assert deletions == 1
