import random, baseforms
import numpy as np
from math import cos, sin, pi, atan, atan2, sqrt

# theta = atan(px/py)
# phi = atan(py/px)

class Linear(baseforms.Transform):
    def __init__(self, rng):
        super(Linear, self).__init__(rng)
        self.a = self.rng.uniform(-1, 1)
        self.b = self.rng.uniform(-1, 1)
        self.c = self.rng.uniform(-1, 1)
        self.d = self.rng.uniform(-1, 1)

    def transform(self, px, py):
        return (self.a * px + self.b * py, self.c * px + self.d * py)


class Moebius(baseforms.ComplexTransform):
    def __init__(self, rng):
        super(Moebius, self).__init__(rng)
        self.pre_a = complex(self.rng.uniform(-1, 1), self.rng.uniform(-1, 1))
        self.pre_b = complex(self.rng.uniform(-1, 1), self.rng.uniform(-1, 1))
        self.pre_c = complex(self.rng.uniform(-1, 1), self.rng.uniform(-1, 1))
        self.pre_d = complex(self.rng.uniform(-1, 1), self.rng.uniform(-1, 1))

    def f(self, z):
        return (self.pre_a * z + self.pre_b) / (self.pre_c * z + self.pre_d)


class InverseJulia(baseforms.ComplexTransform):
    def __init__(self, rng):
        super(InverseJulia, self).__init__(rng)
        r = sqrt(self.rng.random()) * 0.4 + 0.8
        theta = 2 * pi * self.rng.random()
        self.c = complex(r * cos(theta), r * sin(theta))

    def f(self, z):
        z2 = self.c - z
        theta = atan2(z2.imag, z2.real) * 0.5
        sqrt_r = self.rng.choice([1, -1]) * ((z2.imag * z2.imag + z2.real * z2.real) ** 0.25)
        return complex(sqrt_r * cos(theta), sqrt_r * sin(theta))


class Bubble(baseforms.Transform):
    def __init__(self, rng):
        super(Bubble, self).__init__(rng)

    def transform(self, px, py):
        r = sqrt(px**2 + py**2)
        r2 = 4 / (r**2 + 4)
        return r2*px, r2*py


class Sinusoidal(baseforms.Transform):
    def __init__(self, rng):
        super(Sinusoidal, self).__init__(rng)

    def transform(self, px, py):
        return sin(px), sin(py)


class Spherical(baseforms.Transform):
    def __init__(self, rng):
        super(Spherical, self).__init__(rng)

    def transform(self, px, py):
        r2 = sqrt(px**2 + py**2)**2
        return px/r2, py/r2


class Horseshoe(baseforms.Transform):
    def __init__(self, rng):
        super(Horseshoe, self).__init__(rng)

    def transform(self, px, py):
        r = sqrt(px**2 + py**2)
        return (px-py)*(px+py)/r, 2*px*py/r


class Polar(baseforms.Transform):
    def __init__(self, rng):
        super(Polar, self).__init__(rng)

    def transform(self, px, py):
        r = sqrt(px**2 + py**2)
        theta = atan(px/py)
        return theta/pi, r-1


class Handkerchief(baseforms.Transform):
    def __init__(self, rng):
        super(Handkerchief, self).__init__(rng)

    def transform(self, px, py):
        r = sqrt(px**2 + py**2)
        theta = atan(px/py)
        return r * sin(theta+r), r * cos(theta-r)


class Heart(baseforms.Transform):
    def __init__(self, rng):
        super(Heart, self).__init__(rng)

    def transform(self, px, py):
        r = sqrt(px**2 + py**2)
        theta = atan(px/py)
        return r * sin(theta*r), -r * cos(theta*r)


class Disc(baseforms.Transform):
    def __init__(self, rng):
        super(Disc, self).__init__(rng)

    def transform(self, px, py):
        r = sqrt(px**2 + py**2)
        thpi = atan(px/py)/pi
        return thpi * sin(pi*r), thpi * cos(pi*r)


class Spiral(baseforms.Transform):
    def __init__(self, rng):
        super(Spiral, self).__init__(rng)

    def transform(self, px, py):
        r = sqrt(px**2 + py**2)
        theta = atan(px/py)
        return (cos(theta)+sin(r))/r, (sin(theta)-cos(r))/r


class Hyperbolic(baseforms.Transform):
    def __init__(self, rng):
        super(Hyperbolic, self).__init__(rng)

    def transform(self, px, py):
        r = sqrt(px**2 + py**2)
        theta = atan(px/py)
        return sin(theta)/r, r * cos(theta)


class Diamond(baseforms.Transform):
    def __init__(self, rng):
        super(Diamond, self).__init__(rng)

    def transform(self, px, py):
        r = sqrt(px**2 + py**2)
        theta = atan(px/py)
        return sin(theta)*cos(r), cos(theta)*sin(r)


class Ex(baseforms.Transform):
    def __init__(self, rng):
        super(Ex, self).__init__(rng)

    def transform(self, px, py):
        r = sqrt(px**2 + py**2)
        theta = atan(px/py)
        p03 = sin(theta + r)**3
        p13 = cos(theta - r)**3
        return r * (p03 + p13), r * (p03 - p13)


class Swirl(baseforms.Transform):
    def __init__(self, rng):
        super(Swirl, self).__init__(rng)

    def transform(self, px, py):
        r2 = sqrt(px**2 + py**2)**2
        return px*sin(r2) - py*cos(r2), px*cos(r2) + py*sin(r2)
