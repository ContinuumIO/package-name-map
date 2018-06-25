===============================
package-name-map
===============================


.. image:: https://circleci.com/gh/continuumIO/package-name-map.svg?style=svg
    :target: https://circleci.com/gh/continuumIO/package-name-map
.. image:: https://codecov.io/gh/continuumIO/package-name-map/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/continuumIO/package-name-map


A name-mapping database to help unify package managers.  Every ecosystem makes different decisions for naming packages, and many also split up packages in different ways.  To help package managers on any side of this wheel understand some other side of the wheel, we need to build a global map of equivalency between ecosystems.


Reads in a text file, currently in toml format, like so:


.. code:: toml
    # Missing columns are OK.  The only required key is "description" so that
    #     we communicate what a given entry is intended for.
    [[package]]
    description="Python library for working with graphviz"
    conda="python-graphviz"
    pypi="graphviz"
    debian="python-pygraphviz"


.. code:: toml

    # packages from one ecosystem may map to many packages in another.  One entry should be present for each possible match
    #  For example, here graphviz in conda is both a dev package (headers + link libraries) and a runtime, while Debian splits
    #  out the dev package and the runtime.  Additionally, Debian is carrying an old name for the devel package, so we should
    #  track that, too.
    [[package]]
    description="Runtime libraries and executables for graphviz"
    conda="graphviz"
    debian="graphviz"      # the runtime and executables


.. code:: toml

    # Instead of duplicate entries for transitional or renamed packages, we collect lists
    #   These could be extended into individual columns, or perhaps be one table per key that is then joined somehow
    [[package]]
    description="Development headers and libraries for graphviz"
    conda="graphviz"
    debian=["libgraphviz-dev", "graphviz-dev"]
