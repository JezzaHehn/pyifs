Iterated Function System Renderer in Python
=====================================

This program randomly generates IFS fractal images using the chaos game and linear tone mapping.

Initially written in Python 2 under the guidance of Thomas Ludwig one night at KiwiFoo. The tone-mapped image handling comes from Minilight. Restructuring, port to Python 3, and additional transforms by Jezza Hehn. Most of the additional transforms have been converted from Scott Draves' original paper on fractal flames.

NOTE: While this will run in standard Python 3, using PyPy3 will be about 40x faster.


Installing
----------

You will need to install PyPy3, as well as the modules `colour`, `click`, `numpy`, and `zlib` using PyPy3's pip. [Please see this page for further details.](https://www.pypy.org/download.html)


Running
-------

Just run

    pypy3 pyifs.py

NOTE: If you get a nice result, the random seed is saved as a large integer in the image filename. If you wish to re-render at a different resolution, pass this seed to the IFSI constructor instead of a new random integer.


Customization
-------------

Parts of the code that can be customized are as follows:

* You can adjust the `width`, `height`, `iterations`, `num_points`, `num_transforms`, `moebius_chance`, and `image_count` in the file `config.py`
* You can write new `Transform` or `ComplexTransform` classes in `transforms.py`


Writing New Transforms
----------------------

A new subclass of `Transform` should randomize its parameters in `__init__` then implement a `transform` method that takes two args (the x, y of the point) and returns a new x, y.

Alternatively, you can subclass `ComplexTransform`. Instead of implementing `transform`, implement a method `f` that takes a single complex number argument and returns a new complex number.


Examples
--------

![example IFS 1](https://raw.githubusercontent.com/jezzahehn/pyifs/master/Handkerchief-MoebHorseshoe-InverseJulia_640203127151861639.png)
![example IFS 2](https://raw.githubusercontent.com/jezzahehn/pyifs/master/InverseJulia-Moebius-Moebius-InverseJulia_4523210280205849639_1000x1000.png)
![example IFS 3](https://raw.githubusercontent.com/jezzahehn/pyifs/master/MoebDiamond-Horseshoe-MoebDiamond_5586231712168643826.png)
![example IFS 4](https://raw.githubusercontent.com/jezzahehn/pyifs/master/MoebSwirl-MoebSwirl-MoebSwirl_1913761909573458553_1500x1500.png)
