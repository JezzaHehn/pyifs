import config, inspect, os, random, sys, transforms
from baseforms import MoebiusBase
from click import progressbar
from image import Image


class IFSI: # IFS Image
    def __init__(self, width, height, iterations, num_points, num_transforms, seed, exclude=[], include=[], filename=None):
        self.seed = seed
        self.rng = random.Random(seed)
        self.ifs = IFS(self.rng, num_transforms, exclude, include)
        self.im = Image(width, height)
        self.iterations = iterations
        self.num_points = num_points
        if self.iterate():
        if self.iterate(): # Only save non-degenerate systems
            self.save(filename)

    def iterate(self):
        with progressbar(list(range(self.num_points))) as bar:
            for i in bar:
            for i in bar: # show loading bar if render takes longer than a sec

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
                                print "Degenerate form. Aborting render."
                                return False
                            continue
                    r, g, b = t.transform_colour(r, g, b)

                    # Apply final transform for every iteration
                    fx, fy = self.ifs.final_transform(px, py)
                    x = int((fx + 1) * self.im.width / 2)
                    y = int((fy + 1) * self.im.height / 2)

                    # Plot the point in the image buffer
                    self.im.add_radiance(x, y, [r, g, b])
        return True

    def save(self, filename=None):
        if filename == None:
            filename = "im/" + "-".join([t.__class__.__name__ for w,t in self.ifs.transforms]) + "_" + str(self.seed)
            filename += "_" + str(self.im.width) + "x" + str(self.im.height)
            filename += ".png"
        self.im.save(filename, max(1, (self.num_points * self.iterations) / (self.im.height * self.im.width)))
        print filename


class IFS:
    def __init__(self, rng, num_transforms, exclude, include):
        self.transforms = []
        self.total_weight = 0
        self.rng = rng

        transform_choices = []
        transform_list = inspect.getmembers(sys.modules["transforms"], inspect.isclass)
        name_list = [name for (name, obj) in transform_list]
        name_list = list(set(name_list) - set(exclude))

        if include is not None:
            name_list = list(set(name_list) & set(include))
        for (name, obj) in transform_list:
            if name in name_list:
                transform_choices.append(obj)

        for n in range(num_transforms):
            xform = self.rng.choice(transform_choices)
            if random.random() < config.moebius_chance:
                self.add_transform(MoebiusBase(self.rng, xform(self.rng)))
            else:
                self.add_transform(xform(self.rng))

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

# Create image(s) based on config, using a new random seed each time
for i in range(config.image_count):
    IFSI(config.width, config.height, config.iterations, config.num_points, config.num_transforms, exclude=[], random.randrange(sys.maxsize))
