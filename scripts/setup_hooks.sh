#!/bin/bash
#
# Setup git hooks for the MongoDB Labs repository
#

echo "Setting up git hooks..."

# Set git hooks path to .githooks directory
git config core.hooksPath .githooks

# Make hooks executable
chmod +x .githooks/pre-commit 2>/dev/null || true

echo "Git hooks configured!"
echo ""
echo "The following hooks are now active:"
echo "  - pre-commit: Checks if lab index is up-to-date"
echo ""
echo "To disable hooks, run:"
echo "  git config --unset core.hooksPath"