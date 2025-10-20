# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository contains reusable GitHub Actions workflows for Uptick's CI/CD pipelines. The goal is to define best practices for 90% of use cases and make it easy to update all pipelines across the organization. It emphasizes security by minimizing external dependencies - functionality is implemented via Python/bash scripts using only built-in libraries.

## Core Workflow Architecture

### Main CI Workflow (`.github/workflows/ci.yaml`)

The "God CI Pipeline" is the central reusable workflow that handles most CI/CD needs. It's designed as a single workflow with extensive configurability through inputs:

**Key Design Principles:**

- All-in-one workflow with opt-in features via boolean flags
- Standardized caching for Poetry, PNPM, uv, and mise
- AWS authentication via OIDC (no long-lived credentials)
- Docker multi-platform builds (amd64/arm64)
- Smart tagging based on git hashes and custom tags

**Major Feature Groups:**

1. **Language Runtime Setup**: Python, Node.js with version control
2. **Package Managers**: Poetry, uv, PNPM with dependency caching
3. **Cloud Integration**: AWS OIDC authentication, ECR login
4. **Build Tools**: mise, Docker Buildx
5. **Deployment**: Docker image building/pushing to ECR

**Environment Variables Set Automatically:**

- `BRANCH_NAME`: Current branch or PR head ref
- `GIT_SHORT_HASH`: 7-character git hash
- `GITHUB_EVENT`: Either "push" or "pull_request"
- `AWS_SESSION_NAME`: Repository name (slashes converted to hyphens)

### Test Workflows

Test workflows in `.github/workflows/test-*.y*ml` demonstrate usage patterns and serve as integration tests for the main CI workflow. Each tests a specific feature combination.

## Working with This Repository

### Testing Changes

When modifying the main `ci.yaml` workflow:

1. Review existing test workflows to understand feature interactions
2. Add new test cases in `.github/workflows/test-*.yaml` for new features
3. Test workflows run on pull requests automatically

### Docker Image Tagging Logic

The workflow uses complex conditional tagging (lines 456-458 in ci.yaml):

- Default: `<repository>:<git-short-hash>`
- With `docker-prefix`: `<repository>:<prefix>-<git-short-hash>`
- With `docker-tag-latest`: Also tags as `latest`
- With `docker-tag`: Also tags with custom tag
- Dual-repository support: Can push to both main account and deployments account (610829907584)

### Security Constraints

**IMPORTANT**: This repository follows strict security practices:

- Avoid adding external GitHub Actions dependencies where possible
- Implement functionality via Python/bash scripts
- Use only built-in libraries (no pip installs in workflows, except Poetry itself)
- External actions are pinned with SHA hashes (ratchet comments show original version)

### Python Helper Scripts

`scripts/uptick_github.py` provides GitHub API utilities:

- Fetches workflow run and job information
- Determines previous build status for the same branch
- Calculates time taken for jobs
- Uses only built-in Python libraries (urllib, json)

### Example Usage

Basic usage pattern from README:

```yaml
permissions:
  id-token: write # Required for federated aws oidc
  contents: read
  actions: read
  pull-requests: write

jobs:
  ci:
    uses: uptick/actions/.github/workflows/ci.yaml@main
    secrets: inherit
    with:
      aws: true
      python: true
      poetry: true
      command: make ci
```

### Renovation Configuration

The repository uses Renovate for dependency updates (`renovate.json`). GitHub Actions are pinned and managed through dependency updates.

## Documentation

ALWAYS update README.md instructions whenever input parameters to ci.yaml has changed.
