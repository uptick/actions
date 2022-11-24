# Uptick Github Actions

Our resuable actions

## Pipelines

### God CI Pipeline

Use this pipeline for 90% of our workflows.

Features:

- Best practice selection of python version / node / poetry
- Caching for Poetry/PNPM
- Signing into AWS via OIDC
- Slack Shaming / Praising

TODO Features:

- Building docker image
- Metric recording on CI step durations

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
      slack-channel: workforce
      command: make ci
```

# TODO

- [ ] Add pre-commit hooks
- [ ] Add tests
- [ ] Add developer instructions
- [ ] Generate documentation from workflow inputs
- [ ] Fetch previous error for workflow job that is failed not resolved.
