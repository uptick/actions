# Uptick Github Actions

Our resuable actions. The goal of this repo is to define resuable CICD workflows.
Each pipeline should encompass the best practices for 90% of our usecases.
It should be easy to do the right thing and it should be easy to update
all our pipelines across the organisation.

- Installing a version of python
- Notifing slack on an error
- Logging into AWS using OICD
- Building a docker image and pushing to ECR

## Pipelines

### God CI Pipeline

Use this pipeline for 90% of our workflows.

Features:

- Best practice selection of python version / node / poetry
- Caching for Poetry/PNPM
- Signing into AWS via OIDC
- Slack Shaming / Praising

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
      shame-on-error: false
      command: make ci
```

## Security

We avoid adding external dependencies where possible.

External actions are security risks that can easily steal credentials or perform malicious actions on our AWS account.

Please implement functionality via pythons / bash scripts and please rely only on built in libraries.

# TODO

- [ ] Add pre-commit hooks
- [ ] Generate documentation from workflow inputs
- [ ] CI: Build/push docker image to ECR
- [ ] CI: Yarn
- [ ] Instrumentation
