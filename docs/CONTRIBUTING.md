# Contribution Guidelines

As all source{d} projects, this project follows the
[source{d} Contributing Guidelines](https://github.com/src-d/guide/blob/master/engineering/documents/CONTRIBUTING.md).

# Additional Contribution Guidelines

In addition to the [source{d} Contributing Guidelines](https://github.com/src-d/guide/blob/master/engineering/documents/CONTRIBUTING.md),
this project follows the following guidelines.

## Generated Code

Before submitting a pull request make sure all the generated code changes are also committed.

### gRPC services

To generate the code for the gRPC services run:

```bash
$ make protogen
```

## Release Process

 1. Make sure all the [auto-generated code](#generated-code) is up to date and committed.
 1. Update `__version__` in `python/lookout/sdk/__init__.py` with the same version that you will use for the tag (manual step required until [#2](https://github.com/src-d/lookout-sdk/issues/2) is implemented).
 1. Create the release tag.
