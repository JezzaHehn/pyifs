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
        self.coef_a = complex(rng.gauss(0, 0.2), rng.gauss(0, 0.2))
        self.coef_b = complex(rng.gauss(0, 0.2), rng.gauss(0, 0.2))
        self.coef_c = complex(rng.gauss(0, 0.2), rng.gauss(0, 0.2))
        self.coef_d = complex(rng.gauss(0, 0.2), rng.gauss(0, 0.2))
        self.xform = xform
        self.transform_colour = self.xform.transform_colour

    def get_name(self):
        return "Moeb" + self.xform.__class__.__name__

    def f(self, z):
        # apply pre-Moebius (az+b)/(cz+d)
        z = (self.coef_a * z + self.coef_b) / (self.coef_c * z + self.coef_d)

        # apply inner transform
        z = complex(*self.xform.transform(z.real, z.imag))

        # return post-Moebius (dz-b)/(-cz+a), which is inverse of pre-Moebius
        return (self.coef_d * z - self.coef_b) / (-self.coef_c * z + self.coef_a)
