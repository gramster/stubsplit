stubsplit is a simple utility which can remove docstrings from
or insert docstrings into Python type stub files. It was originally
created for the pandas type stubs shipped with pylance, which 
had some docstrings added because they were not available in the
pandas package. It has since been replaced by a newer utility,
`docify`, which does not rely on static files containing docstrings
but can get the most up to date docstrings via reflection on the
imported module. That said, stubsplit can still be useful for
removing docstrings, e.g. from Python stubs generated by pyright.

The algorithm used is a blunt instrument (crude and kludgy parser)
but "good enough" for the use cases we have applied it to. It 
would be better to rewrite this at some point using libcst but
the effort is not currently merited.

```
Usage:
  stubsplit (split|merge) [--verbose] <stubpath> <docpath>
  stubsplit -h | --help
  stubsplit --version

Options:
  -h --help     Show this screen.
  --version     Show version.
```
