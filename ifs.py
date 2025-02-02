import inspect, numpy, os, random, sys, transforms
from baseforms import MoebiusBase, SphericalBase
from click import progressbar
from image import Image
from math import log10, isnan


def safelog10(x):
    try:
        return log10(x)
    except ValueError:
        return 0.0

def test_seed(num_transforms, moebius_chance, spherical_chance, seed):
    """
    Test whether the IFS seed will be both non-degenerate and interesting by
    rendering a low-resolution version
    """
    lowres = IFSI(150, 150, 1000, 1000, num_transforms, moebius_chance, spherical_chance, seed)
    if lowres.iterate(range(1000)):
        if lowres.im.interest_factor() >= 120:
            return True
    return False


def get_seed(num_transforms, moebius_chance, spherical_chance):
    while True:
        seed = random.randrange(sys.maxsize)
        if test_seed(num_transforms, moebius_chance, spherical_chance, seed):
            return seed


class IFSI: # IFS Image
    def __init__(self, width, height, iterations, num_points, num_transforms, moebius_chance, spherical_chance, seed, exclude=[], include=[], filename=None):
        self.seed = seed
        self.rng = random.Random(seed)
        self.ifs = IFS(self.rng, num_transforms, moebius_chance, spherical_chance, exclude, include)
        self.im = Image(width, height, max(1, (num_points * iterations) / (width * height)))
        self.iterations = iterations
        self.num_points = num_points
        self.name = "-".join([t.get_name() for w,t in self.ifs.transforms])
        if filename == None:
            self.filename = os.path.join("im", self.name + "_" + str(self.seed))
            self.filename += "_" + str(self.im.width) + "x" + str(self.im.height)
            self.filename += ".png"
        else:
            self.filename = filename

    def render(self, bar=True):
        if bar is True:
            label = "Rendering " + self.name
            with progressbar(length=self.num_points, label=label, width=0) as iter:
                if self.iterate(iter):
                    return self
        else:
            if hasattr(bar, "UpdateBar"):
                guibar = bar
            else:
                guibar = None
            if self.iterate(range(self.num_points), guibar=guibar):
                return self
        return False

    def iterate(self, iterator, guibar=None):
        for i in iterator:

            # Start with a random point, and the color black
            px = self.rng.uniform(-1, 1)
            py = self.rng.uniform(-1, 1)
            r, g, b = 0.0, 0.0, 0.0
            zero_count, cont_count = 0, 0

            # Run the starting point through the system repeatedly
            for j in range(self.iterations):
                t = self.ifs.choose_transform()
                try:
                    px, py = t.transform(px, py)
                except ZeroDivisionError:
                    zero_count += 1
                    if zero_count >= 10:
                        cont_count +=1
                        if cont_count >= 10:
                            # Degenerate form. Abort render.
                            return False
                        continue
                r, g, b = t.transform_colour(r, g, b)

                # Apply final transform for every iteration
                fx, fy = self.ifs.final_transform(px, py)
                x = int((fx + 1) * self.im.width / 2)
                y = int((fy + 1) * self.im.height / 2)

                # Plot the point in the image buffer
                self.im.add_radiance(x, y, [r, g, b])

            if guibar:
                guibar.UpdateBar(i+1)
        return self

    def save_image(self):
        if not os.path.exists("im"):
            os.makedirs("im")
        self.im.save(self.filename)
        return self

    def get_image(self):
        a = numpy.array([safelog10(x) for x in self.im.data])
        return numpy.reshape(a / max(a), (self.im.width, self.im.height, 3))

class IFS:
    def __init__(self, rng, num_transforms, moebius_chance, spherical_chance, exclude, include):
        self.transforms = []
        self.total_weight = 0
        self.rng = rng

        transform_choices = []
        transform_list = inspect.getmembers(sys.modules["transforms"], inspect.isclass)
        name_list = [name for (name, obj) in transform_list]
        name_list = list(set(name_list) - set(exclude))

        if include != []:
            name_list = list(set(name_list) & set(include))
        for (name, obj) in transform_list:
            if name in name_list:
                transform_choices.append(obj)

        for n in range(num_transforms):
            # Pick a transform, and possibly either a Moebius and/or Spherical baseform
            xform = self.rng.choice(transform_choices)(self.rng)
            if self.rng.random() < moebius_chance:
                xform = MoebiusBase(self.rng, xform)
            if self.rng.random() < spherical_chance:
                xform = SphericalBase(self.rng, xform)
            self.add_transform(xform)

    def add_transform(self, transform):
        weight = self.rng.gauss(1, 0.2) * self.rng.gauss(1, 0.2)
        self.total_weight += weight
        self.transforms.append((weight, transform))

    def choose_transform(self):
        w = self.rng.random() * self.total_weight
        running_total = 0
        for weight, transform in self.transforms:
            running_total += weight
            if w <= running_total:
                return transform

    def final_transform(self, px, py):
        """
        Final transform to be applied after each iteration
        """
        a = 0.5
        b = 0
        c = 0
        d = 1
        z = complex(px, py)
        z2 = (a * z + b) / (c * z + d)
        return z2.real, z2.imag
