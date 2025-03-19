# matchescu-base

This Python package includes common abstract data types (`adt` package),
utilities (`common` package) and generic data extraction algorithms for entity
resolution.
These abstractions are used in other packages such as:

* `matchescu-reference-extraction`: extracts entity references from data sources
* `matchescu-reference-stores`: stores entity references efficiently
* `matchescu-comparison-space-generation`: generates the comparison space used
for matching or clustering
* `matchescu-matching`: various methods of scoring the similarity of entity
references
* `matchescu-clustering`: various methods of scoring the colocation of entity
references
* `matchescu-profile-assembly`: algorithms used to build concrete entity
profiles from specific data structures (tuples, lists or graphs)

On its own, the package may be used to create other structured approaches
towards entity resolution, particularly based on the Resolvi reference
architecture.

## Set up dev environment

1. (_optional_) install pyenv
2. install Python 3.11
3. install [Poetry](https://python-poetry.org)
4. clone this repository
5. run a couple of shell commands
```shell
$ cd <REPO_ROOT>
$ poetry install
```

## Run tests

```shell
$ poetry run pytest
```

## Activate virtual environment

```shell
$ poetry shell
```
-or-
```shell
$ source .venv/bin/activate
```
