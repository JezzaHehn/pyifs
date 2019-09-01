import config, os, random, sys
import PySimpleGUI as sg
from ifs import test_seed, IFSI

layout = [
    [
        sg.Graph(
            canvas_size=(config.width, config.height),
            graph_bottom_left=(0, 0),
            graph_top_right=(config.width, config.height),
            key="graph",
            change_submits=True,
            drag_submits=True
        )
    ]
]

seed = random.randrange(sys.maxsize)
if test_seed(config.num_transforms, seed):
    ifsi = IFSI(config.width, config.height, config.iterations, config.num_points, config.num_transforms, seed).render()
    raw = ifsi.im.raw()

    window = sg.Window("PyIFS", layout)
    window.Finalize()

    graph = window.Element("graph")
    graph.DrawImage(data=raw, location=(0,0))

    while True:
        event, values = window.Read()
        if event is None:
            break  # exit
        # print(event, values)

        if event.startswith("graph"):
            x, y = values["graph"]
            if event.endswith('+UP'):
                print(f"UP {values['graph']}")
            else:
                print(f"DOWN {values['graph']}")

        else:
            print(event, values)

else:
    print("Bad seed!  :(  ")

# # Create image(s) based on config, using a new random seed each time
# i = 0
# while i < config.image_count:
#     # pick a new seed
#     seed = random.randrange(sys.maxsize)
#     if test_seed(config.num_transforms, seed):
#         IFSI(config.width, config.height, config.iterations, config.num_points, config.num_transforms, seed).render().save()
#         i += 1


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
