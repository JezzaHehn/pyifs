from colour import Color

class Transform(object):
    def __init__(self, rng):
        c = Color(hsl=(rng.random(), 1, 0.5))
        self.r, self.g, self.b = c.rgb
        self.rng = rng

    def transform_colour(self, r, g, b):
        r = (self.r + r) / 2
        g = (self.g + g) / 2
        b = (self.b + b) / 2
        return r, g, b


class ComplexTransform(Transform):
    def transform(self, px, py):
        z = complex(px, py)
        z2 = self.f(z)
        return z2.real, z2.imag
