import config, inspect, random, sys, transforms
from click import progressbar
from image import Image


class IFSI: # IFS Image
    def __init__(self, width, height, iterations, num_points, num_transforms, seed):
        self.seed = seed
        self.rng = random.Random(seed)
        self.ifs = IFS(self.rng, num_transforms)
        self.im = Image(width, height)
        self.iterations = iterations
        self.num_points = num_points
        self.iterate()
        self.save()

    def iterate(self):
        with progressbar(list(range(self.num_points))) as bar:
            for i in bar:
                px = self.rng.uniform(-1, 1)
                py = self.rng.uniform(-1, 1)
                r, g, b = 0.0, 0.0, 0.0

                for j in range(self.iterations):
                    t = self.ifs.choose_transform()
                    px, py = t.transform(px, py)
                    r, g, b = t.transform_colour(r, g, b)

                    fx, fy = self.ifs.final_transform(px, py)
                    x = int((fx + 1) * self.im.width / 2)
                    y = int((fy + 1) * self.im.height / 2)

                    self.im.add_radiance(x, y, [r, g, b])

    def save(self):
        filename = "im/" + "-".join([t.__class__.__name__ for w,t in self.ifs.transforms])
        filename += "_" + str(self.seed) + "_" + str(self.im.width) + "x" + str(self.im.height) + ".png"
        self.im.save(filename, max(1, (self.num_points * self.iterations) / (self.im.height * self.im.width)))
        print filename


class IFS:
    def __init__(self, rng, num_transforms):
        self.transforms = []
        self.total_weight = 0
        self.rng = rng
        transform_choices = []
        for (name, obj) in inspect.getmembers(sys.modules["transforms"], inspect.isclass):
            # if inspect.isclass(obj):
            transform_choices.append(obj)

        for n in range(num_transforms):
            cls = self.rng.choice(transform_choices)
            self.add_transform(cls(self.rng))

    def add_transform(self, transform):
        weight = self.rng.gauss(1, 0.15) * self.rng.gauss(1, 0.15)
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
        a = 0.5
        b = 0
        c = 0
        d = 1
        z = complex(px, py)
        z2 = (a * z + b) / (c * z + d)
        return z2.real, z2.imag


for i in range(config.image_count):
    IFSI(config.width, config.height, config.iterations, config.num_points, config.num_transforms, random.randrange(sys.maxsize))
