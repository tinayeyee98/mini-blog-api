Boilerplate scripts with normalized names simplify process for contributing and CI.

> Inspired by [github/scripts-to-rule-them-all](https://github.com/github/scripts-to-rule-them-all).

Run the scripts from the project root directory.

Usage:

```console
$ cd path/to/project
$ . ./scripts/<script-name>
```

**Project Setup**

```console
$ . ./scripts/setup
```

**Tests and Coverage Report**

```console
$ . ./scripts/test
```

**Syntax Formatting and Code Style**

```console
$ . ./scripts/codestyle
```

**OpenAPI Schema**

```console
$ poetry run python scripts/openapi.py
```

Artifacts

 - openapi schema in project root: `openapi.yaml`


**Build Package**

```console
$ . ./scripts/build
```

Artifacts

 - `<package>.tar.gz` (source distribution package)
 - `<package>-py3-none-any.whl` (built distribution package in wheel format)
 - `<package>_openapi.yaml`, `<package>_openapi.json` (openapi schemas)
