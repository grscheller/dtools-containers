# Developer Tools - Container based data structures

Python package of modules implementing container-like data structures.

- **Repositories**
  - [dtools.containers][1] project on *PyPI*
  - [Source code][2] on *GitHub*
- **Detailed documentation**
  - [Detailed API documentation][3] on *GH-Pages*

This project is part of the
[Developer Tools for Python][4] **dtools.** namespace project.

### The Box - dtools.containers.box

Container holding at most one object of a given type. This stateful
(mutable) container contains 0 or 1 item at a given time.

### Functional Tuple - dtools.containers.functional_tuple 

Subclassed tuple with a more functional interface. Gives tuple
a FP methods. Designed to be further inherited from.

### Immutable List - dtools.containers.immutable_list

An immutable, hashable Python list-like object. Hashability will be
enforced at runtime. Mutable list methods will return new objects.

### Maybe Monad - dtools.containers.maybe

An implementation of the maybe (optional) monad. Data structure
represents a possibly missing value. Useful in implementing exception
free code paths.

### Either Monad - dtools.containers.xor

An implementation of a left biased either monad. Data structure
representing either a "left" or "right" value, but not both. These two
values can be the same or different types. The "left" value is usually
taken to be the "happy path" of code flow. The "right" value is often
used for an error condition or a text string describing what went wrong.


[1]: https://pypi.org/project/dtools.containers/
[2]: https://github.com/grscheller/dtools-containers/
[3]: https://grscheller.github.io/dtools-namespace_projects/containers/
[4]: https://github.com/grscheller/dtools-namespace_projects/blob/main/README.md
