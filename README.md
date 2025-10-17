# Uptick Github Actions

Our resuable actions. The goal of this repo is to define resuable CICD workflows.
Each pipeline should encompass the best practices for 90% of our usecases.
It should be easy to do the right thing and it should be easy to update
all our pipelines across the organisation.

- Installing a version of python
- Logging into AWS using OICD
- Building a docker image and pushing to ECR

## Pipelines

### God CI Pipeline

Use this pipeline for 90% of our workflows.

Features:

- Best practice selection of python version / node / poetry
- Caching for Poetry/PNPM
- Signing into AWS via OIDC

**Usage:**

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

**[Reference input parameters to ci.yaml](./ci_command_usage.md)**



### Claude Code PR Review pipeline

Automated PR code review using Claude Code. This workflow performs comprehensive code reviews focusing on code quality, security, performance, and testing and leaves inline comments (instead of a larger overall comment)

**Features:**

- Automated code review on pull requests
- Inline comments on specific code issues
- Customizable review instructions via `AGENTS_CODEREVIEW.md`
- Follows patterns from `CLAUDE.md` and `AGENTS.md` if present
- Reviews only the latest commit to avoid duplicate comments
- Security-focused analysis
- Performance optimization suggestions

**Usage:**

Add this workflow to your repository at `.github/workflows/claude-review.yml`:

```yaml
name: Claude Code Review

on:
  pull_request:
    types: [opened, synchronize, reopened]

permissions:
  id-token: write
  contents: read
  pull-requests: write
  issues: write

jobs:
  claude-review:
    uses: uptick/actions/.github/workflows/claude_review.yaml@main
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
      # OR use OAuth token instead:
      # CLAUDE_CODE_OAUTH_TOKEN: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
```

**Required Secrets:**

You must configure ONE of the following secrets in your repository:

| Secret | Description |
|--------|-------------|
| `ANTHROPIC_API_KEY` | Anthropic API key for API-based billing (recommended) |
| `CLAUDE_CODE_OAUTH_TOKEN` | OAuth token for Claude Code (alternative to API key) |

**Customization:**

Create an `AGENTS_CODEREVIEW.md` file in your repository root to customize the review instructions. If this file doesn't exist, Claude will use the default review criteria focusing on:
- Code Quality (clean code, error handling, readability)
- Security (vulnerabilities, input validation, auth/authz)
- Performance (bottlenecks, query efficiency, resource management)
- Testing (coverage, test quality, edge cases)


### Claude Code @mention pipeline

Interactive Claude Code integration that responds to @claude mentions in issues, pull requests, and comments. This workflow enables team members to ask Claude Code questions or request assistance directly in GitHub conversations.

**Features:**

- Responds to @claude mentions in issue comments
- Responds to @claude mentions in pull request review comments
- Responds to @claude mentions in pull request reviews
- Responds to @claude mentions in new issues
- Progress tracking with automated status comments
- Full repository context awareness

**Usage:**

Add this workflow to your repository at `.github/workflows/claude-mention.yml`:

```yaml
name: Claude Code Mention

on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]
  issues:
    types: [opened, assigned]
  pull_request_review:
    types: [submitted]

permissions:
  id-token: write
  contents: read
  pull-requests: write
  issues: write
  actions: read

jobs:
  claude:
    uses: uptick/actions/.github/workflows/claude_mention.yaml@main
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
      # OR use OAuth token instead:
      # CLAUDE_CODE_OAUTH_TOKEN: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
```

**Required Secrets:**

You must configure ONE of the following secrets in your repository:

| Secret | Description |
|--------|-------------|
| `ANTHROPIC_API_KEY` | Anthropic API key for API-based billing (recommended) |
| `CLAUDE_CODE_OAUTH_TOKEN` | OAuth token for Claude Code (alternative to API key) |

**How to Use:**

Simply mention @claude in any:
- Issue comment
- Pull request comment
- Pull request review comment
- New issue (in title or body)



# Security

- We avoid adding external dependencies where possible.

- External actions are security risks that can easily steal credentials or perform malicious actions on our AWS account.

- Pin dependencies via ratchet `ratchet pin .github/*/*.yaml`

Please implement functionality via pythons / bash scripts and please rely only on built in libraries.

