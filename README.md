# Shared Flow Testing

![Build](https://github.com/NHSDigital/shared-flow-testing/workflows/Build/badge.svg?branch=master)

This is a RESTful HL7® FHIR® API specification for the *Template API*.

* `specification/` This [Open API Specification](https://swagger.io/docs/specification/about/) describes the endpoints, methods and messages exchanged by the API. Use it to generate interactive documentation; the contract between the API and its consumers.
* `sandbox/` This NodeJS application implements a mock implementation of the service. Use it as a back-end service to the interactive documentation to illustrate interactions and concepts. It is not intended to provide an exhaustive/faithful environment suitable for full development and testing.
* `scripts/` Utilities helpful to developers of this specification.
* `proxies/` Live (connecting to another service) and sandbox (using the sandbox container) Apigee API Proxy definitions.

Consumers of the API will find developer documentation on the [NHS Digital Developer Hub](https://developer.digital.nhs.uk/).

## Contributing
Contributions to this project are welcome from anyone, providing that they conform to the [guidelines for contribution](https://github.com/NHSDigital/shared-flow-testing/blob/master/CONTRIBUTING.md) and the [community code of conduct](https://github.com/NHSDigital/shared-flow-testing/blob/master/CODE_OF_CONDUCT.md).

### Licensing
This code is dual licensed under the MIT license and the OGL (Open Government License). Any new work added to this repository must conform to the conditions of these licenses. In particular this means that this project may not depend on GPL-licensed or AGPL-licensed libraries, as these would violate the terms of those libraries' licenses.

The contents of this repository are protected by Crown Copyright (C).

## Development

### Requirements
* make
* nodejs + npm/yarn
* [poetry](https://github.com/python-poetry/poetry)
* Java 8+

### Install
```
$ make install
```

#### Updating hooks
You can install some pre-commit hooks to ensure you can't commit invalid spec changes by accident. These are also run
in CI, but it's useful to run them locally too.

```
$ make install-hooks
```

### Environment Variables
Various scripts and commands rely on environment variables being set. These are documented with the commands.

:bulb: Consider using [direnv](https://direnv.net/) to manage your environment variables during development and maintaining your own `.envrc` file - the values of these variables will be specific to you and/or sensitive.

### Make commands
There are `make` commands that alias some of this functionality:
 * `lint` -- Lints the spec and code
 * `publish` -- Outputs the specification as a **single file** into the `build/` directory
 * `serve` -- Serves a preview of the specification in human-readable format

### Testing
Each API and team is unique. We encourage you to use a `test/` folder in the root of the project, and use whatever testing frameworks or apps your team feels comfortable with. It is important that the URL your test points to be configurable. We have included some stubs in the Makefile for running tests.

### VS Code Plugins

 * [openapi-lint](https://marketplace.visualstudio.com/items?itemName=mermade.openapi-lint) resolves links and validates entire spec with the 'OpenAPI Resolve and Validate' command
 * [OpenAPI (Swagger) Editor](https://marketplace.visualstudio.com/items?itemName=42Crunch.vscode-openapi) provides sidebar navigation


### Emacs Plugins

 * [**openapi-yaml-mode**](https://github.com/esc-emacs/openapi-yaml-mode) provides syntax highlighting, completion, and path help

### OpenAPI Generator

> [OpenAPI Generator](https://github.com/OpenAPITools/openapi-generator-cli) *OpenAPI Generator allows generation of API client libraries (SDK generation), server stubs, documentation and configuration automatically given an OpenAPI Spec*

OpenAPI Generator does the lifting for the following npm scripts:

 * `test` -- Lints the definition
 * `publish` -- Outputs the specification as a **single file** into the `build/` directory

(Workflow detailed in a [post](https://developerjack.com/blog/2018/maintaining-large-design-first-api-specs/) on the *developerjack* blog.)

:bulb: The `publish` command is useful when uploading to Apigee which requires the spec as a single file.

### Caveats

#### Swagger UI
Swagger UI unfortunately doesn't correctly render `$ref`s in examples, so use `openapi publish` instead.

#### Apigee Portal
The Apigee portal will not automatically pull examples from schemas, you must specify them manually.

### Platform setup

Successful deployment of the API Proxy requires:

 1. A *Target Server* named `shared-flow-testing-target`
 2. A *Key-Value Map* named `sft-variables`, containing any values you might need at proxy runtime
 3. A *Key-Value Map* named `sft-variables-encrypted`, containing any secrets you might need at proxy runtime

The Key-Value maps need to be specifed within the [api-management-infrasture](https://github.com/NHSDigital/api-management-infrastructure) repository to be able to be used with the API proxy.

:bulb: For Sandbox-running environments (`test`) these need to be present for successful deployment but can be set to empty/dummy values.
