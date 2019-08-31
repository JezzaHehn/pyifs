import config, ifs, os, random, sys


# Create image(s) based on config, using a new random seed each time
if not os.path.exists("im"):
    os.makedirs("im")

i = 0
while i < config.image_count:
    # pick a new seed
    seed = random.randrange(sys.maxsize)

    # first render a low-resolution version to test for quality, then render full res
    lowres = ifs.IFSI(150, 150, 1000, 1000, config.num_transforms, seed)
    if lowres.iterate(): # Only save non-degenerate systems
        if lowres.im.quality() >= 100:
            ifs.IFSI(config.width, config.height, config.iterations, config.num_points, config.num_transforms, seed).iterate().save()
            i += 1


# # Create small images as dataset for classifier and GAN experiments
# for t in ["Linear","Bubble"]:
#     for i in range(10):
#         path = os.path.join("data/training", t)
#         if not os.path.exists(path):
#             os.makedirs(path)
#         filename = os.path.join(path, t + "%03d"%i + ".png")
#         IFSI(config.width, config.height, config.iterations, config.num_points, config.num_transforms, random.randrange(sys.maxsize), include=[t], filename=filename)
# for i in range(10):
#     path = os.path.join("data/validation", t)
#     if not os.path.exists(path):
#         os.makedirs(path)
#     filename = os.path.join(path, t + "%03d"%i + ".png")
#     IFSI(config.width, config.height, config.iterations, config.num_points, config.num_transforms, random.randrange(sys.maxsize), include=[t], filename=filename)
