An Iterated Function System in Python
=====================================

Initially written under the guidance of Thomas Ludwig one night at KiwiFoo. The tone-mapped image handling comes from Minilight. Restructuring and additional transforms by Jezza Hehn.

NOTE: While this will run in standard Python 2, using PyPy will be about 40x faster.

Running
-------

Just run

    pypy pyifs.py

NOTE: If you get a nice result, the random seed is saved in the image filename if you wish to re-render at a different resolution.

Customization
-------------

Parts of the code that can be customized are as follows:

* You can adjust the `width`, `height`, `iterations`, `num_points`, `num_transforms`, and `image_count` in `config.py`
* You can write new `Transform` or `ComplexTransform` classes in `transforms.py`

Writing New Transforms
----------------------

A new subclass of `Transform` should randomize its parameters in `__init__`
then implement a `transform` method that takes two args (the x, y of the
point) and returns a new x, y.

Alternatively, you can subclass `ComplexTransform`. Instead of implementing
`transform`, implement a method `f` that takes a single complex number
argument and returns a new complex number.

Examples
--------

![example IFS](https://raw.githubusercontent.com/jezzahehn/pyifs/master/example.png)
![example IFS2](https://raw.githubusercontent.com/jezzahehn/pyifs/master/example2.png)
![example IFS3](https://raw.githubusercontent.com/jezzahehn/pyifs/master/example3.png)
![example IFS4](https://raw.githubusercontent.com/jezzahehn/pyifs/master/example4.png)
