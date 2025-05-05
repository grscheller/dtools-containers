# Developer Tools - Container based data structures

Python package of modules implementing container-like data structures.

- **Repositories**
  - [dtools.tuples][1] project on *PyPI*
  - [Source code][2] on *GitHub*
- **Detailed documentation**
  - [Detailed API documentation][3] on *GH-Pages*

This project is part of the
[Developer Tools for Python][4] **dtools.** namespace project.

## Overview

Tuple-based data structures.

### Boxes

- *module* `dtools.containers.boxes`
  - *class** `Box`
    - container that can contain 0 or 1 item of a given type
    - stateful with a procedural interface

### Functional Tuples

Data structures wrapping a Python tuple giving it a functional
interface.

- *module* `dtools.tuples.ftuples`
  - *class* `FTuple`: Functional Tuple
    - immutable tuple-like data structure
    - with a functional interface

______________________________________________________________________

[1]: https://pypi.org/project/dtools.containers/
[2]: https://github.com/grscheller/dtools-containers/
[3]: https://grscheller.github.io/dtools-docs/containers/
[4]: https://github.com/grscheller/dtools-docs
