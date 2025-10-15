## Input parameters for ci.yaml
### General & Checkout

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `checkout-ref` | string | `""` | The branch, tag or SHA to checkout. When empty defaults to default checkout branch |
| `command` | string | `"make ci"` | The primary command to run. Defaults to make ci (but it can also be a bash script) |
| `debug` | boolean | `false` | Dump context |

### Python

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `python` | boolean | `false` | Install python? |
| `python-version` | string | `"3.10"` | Version of python to install |

### Poetry

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `poetry` | boolean | `false` | Install and setup poetry |
| `poetry-install` | boolean | `true` | Install poetry dependencies (including dev) |
| `poetry-install-command` | string | `"poetry install"` | Specify a different command; defaults to (poetry install) |
| `poetry-version` | string | `"1.8.2"` | Poetry version to install |
| `s3pypi-publish` | boolean | `false` | Set to true if you want to build and publish to private s3pypi repo |
| `s3pypi-bucket` | string | `"s3pypi-610829907584-us-east-1"` | s3 bucket name for s3pypi |
| `pypi-dist` | string | `"dist/*"` | Build folder of the pypi package |

### uv (Python Package Manager)

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `uv` | boolean | `false` | Install and set up uv |
| `uv-cache` | boolean | `true` | Cache uv via github's cache |
| `uv-sync` | boolean | `true` | Sync uv dependencies |
| `uv-sync-command` | string | `"uv sync"` | Sync command. Defaults to uv sync. Add --all-extras or whatever here. |
| `uv-version` | string | `"0.5.0"` | Version of uv to install |
| `uv-directory` | string | `"."` | Path to run uv within |

### Node.js

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `node` | boolean | `false` | Install node? |
| `node-version` | string | `"16"` | Version of node to install |

### PNPM

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `pnpm` | boolean | `false` | Install and set up pnpm |
| `pnpm-install` | boolean | `true` | Install pnpm dependencies |
| `pnpm-build` | boolean | `true` | Run PNPM Build |

### Docker

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `docker-enabled` | boolean | `false` | if enabled, build + push a docker image |
| `docker-buildx-enabled` | boolean | `false` | if enabled, enables docker buildx |
| `docker-context` | string | `"."` | Where to find the Dockerfile |
| `docker-prefix` | string | `""` | Image tag to prefix. Eg: {subman}-aed1f13, where subman is the docker-prefix |
| `docker-tag-latest` | boolean | `false` | Tag the image as `latest` |
| `docker-tag` | string | `""` | Manual docker tag to include |
| `docker-repository` | string | `""` | Required if specifying docker-enabled. This is the ECR repository. EG:  305686791668.dkr.ecr.ap-southeast-2.amazonaws.com/uptick |
| `docker-image-platforms` | string | `"linux/amd64,linux/arm64"` | A comma separated list of platform to be used for building the docker image |
| `docker-push` | boolean | `true` | Whether or not to push docker images |
| `docker-build-args` | string | `"ARG1=value1,ARG2=value2"` | A comma separated list of Docker Build arguments |
| `ecr-type` | string | `"private"` | The type of AWS ECR repository to push to public or private |

### AWS

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `aws` | boolean | `false` | If enabled set up AWS Credentials |
| `aws-region` | string | `"ap-southeast-2"` | The AWS region to configure the AWS profile with |
| `aws-iam-role-arn` | string | `"arn:aws:iam::610829907584:role/default-github-actions-ci-role"` | AWS IAM Role to assume |

### mise

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `mise` | boolean | `false` | If enabled; installs mise |
| `mise-install` | boolean | `false` | If enabled; runs mise install to install tools |
| `mise-cache` | boolean | `true` | If enabled; caches mise via github's cache |

### Other

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `bump-app` | string | `""` | App to bump |

### Secrets

| Secret | Required | Description |
|--------|----------|-------------|
| `checkout-ssh-key` | false | The ssh key if provided; to checkout the repo with |
| `SECRET_ENV` | false | A secret environment variable to faciliate passing in secrets |
| `SLACK_TOKEN` | false | DEPRECATED |
| `SLACK_CHANNEL` | false | DEPRECATED |

### Deprecated Parameters

The following parameters are deprecated and should not be used:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `slack-on-error` | boolean | `false` | DEPRECATED |
| `shame-on-error` | boolean | `false` | DEPRECATED |
| `praise-on-fix` | boolean | `false` | DEPRECATED |
| `slack-channel` | string | `"devops-test-slack"` | DEPRECATED |