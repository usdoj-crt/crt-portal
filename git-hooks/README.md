# Git Hooks

This directory contains hooks to avoid pushing broken or unpolished code to CI/CD, which can cause some noisy notifications.

## Configuration

To use them, you'll need to set your [gitconfig](https://git-scm.com/docs/githooks#_description) to include this directory for hooks. To do that for this repo only, run:

```
echo '[core]' >> .git/config;
echo '  hooksPath="./git-hooks"' >> .git/config;
```

or edit the config appropriately, if you've already changed it in the past.

To disable, simply `rm .git/config`, or remove the relevant lines.

## Ignoring

For some reason or another, a hook might fail or you might want to skip it for a specific commit or push. To do that, add [--no-verify](https://git-scm.com/docs/git-commit#Documentation/git-commit.txt---no-verify) to your commit command.
