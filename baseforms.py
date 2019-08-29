from colour import Color


class Transform(object):
    def __init__(self, rng):
        self.r, self.g, self.b = Color(hsl=(rng.random(), 1, 0.5)).rgb
        self.rng = rng

    def transform_colour(self, r, g, b):
        r = (self.r + r) / 2.0
        g = (self.g + g) / 2.0
        b = (self.b + b) / 2.0
        return r, g, b

    def get_name(self):
        return self.__class__.__name__


class ComplexTransform(Transform):
    def transform(self, px, py):
        z = complex(px, py)
        z2 = self.f(z)
        return z2.real, z2.imag


class MoebiusBase(ComplexTransform):
    def __init__(self, rng, xform):
        super(MoebiusBase, self).__init__(rng)
        self.pre_a = complex(rng.uniform(-1, 1), rng.uniform(-1, 1))
        self.pre_b = complex(rng.uniform(-1, 1), rng.uniform(-1, 1))
        self.pre_c = complex(rng.uniform(-1, 1), rng.uniform(-1, 1))
        self.pre_d = complex(rng.uniform(-1, 1), rng.uniform(-1, 1))
        self.xform = xform
        self.__class__.__name__ = "Moeb" + xform.__class__.__name__
        self.post_a = complex(rng.uniform(-1, 1), rng.uniform(-1, 1))
        self.post_b = complex(rng.uniform(-1, 1), rng.uniform(-1, 1))
        self.post_c = complex(rng.uniform(-1, 1), rng.uniform(-1, 1))
        self.post_d = complex(rng.uniform(-1, 1), rng.uniform(-1, 1))

    def f(self, z):
        z2 = (self.pre_a * z + self.pre_b) / (self.pre_c * z + self.pre_d)
        z3 = complex(*self.xform.transform(z2.real, z2.imag))
        return (self.post_a * z3 + self.post_b) / (self.post_c * z3 + self.post_d)
