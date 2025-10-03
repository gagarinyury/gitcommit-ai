#!/bin/bash
set -e

echo "GitCommit AI Action - Validating commit messages..."

# Run the action
python -m gitcommit_ai.action.runner

# Exit with appropriate code
exit $?
