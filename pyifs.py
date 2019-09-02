import config, os, random, sys
import PySimpleGUI as sg
from ifs import test_seed, IFSI


# Set default colour scheme for windows
sg.ChangeLookAndFeel('GreenTan')


# Import default configuration parameters from config.py
width = config.width
height = config.height
iterations = config.iterations
num_points = config.num_points
num_transforms = config.num_transforms
moebius_chance = config.moebius_chance

# Pick a random seed based on default params
while True:
    seed = random.randrange(sys.maxsize)
    if test_seed(num_transforms, moebius_chance, seed):
        break

menu_def = [
    ["File", ["Open Parameters", "Save Parameters", "Save Image", "Exit"]],
    ["Edit", "Undo"],
    ["Help", "About..."]
]

main_layout = [
    [sg.Menu(menu_def, tearoff=True)],
    [sg.Column([
        [sg.Text("Width", size=(10, 2))],
        [sg.Text("Height", size=(10, 2))]
     ]),
     sg.Column([
        [sg.InputText(str(width), key="width", size=(20, 20), enable_events=True)],
        [sg.InputText(str(height), key="height", size=(20, 20), enable_events=True)]
     ])
    ],
    [sg.Column([
        [sg.Text("Iterations", size=(12, 2))],
        [sg.Text("Num Points", size=(12, 2))]
     ]),
     sg.Column([
        [sg.InputText(str(iterations), key="iterations", size=(20, 20), enable_events=True)],
        [sg.InputText(str(num_points), key="num_points", size=(20, 20), enable_events=True)]
     ])
    ],
    [sg.Column([
        [sg.Text("Number of Transforms", size=(15, 2))],
        [sg.Text("Moebius Wrapper Probability", size=(15, 2))]
     ]),
     sg.Column([
        [sg.Slider(range=(1, 10), orientation="h", size=(20, 20), default_value=num_transforms, key="num_transforms", enable_events=True)],
        [sg.Slider(range=(0, 100), orientation="h", size=(20, 20), default_value=int(moebius_chance*100), key="moebius_chance", enable_events=True)]
     ])
    ],
    [sg.Button("Random Seed"),
     sg.InputText(seed, key="seed", enable_events=True)],
    [sg.Button("Render to File")]
]


main_window = sg.Window("PyIFS", main_layout)
main_window.Finalize()

# Main window event loop
while True:
    event, values = main_window.Read()
    if event is None or event == "Exit":
        break  # exit the program

    if event == "width":
        width = int(values["width"])

    if event == "height":
        height = int(values["height"])

    if event == "iterations":
        iterations = int(values["iterations"])

    if event == "num_points":
        num_points = int(values["num_points"])

    if event == "num_transforms":
        num_transforms = int(values["num_transforms"])

    if event == "moebius_chance":
        moebius_chance = int(values["moebius_chance"])

    if event == "Random Seed":
        while True:
            seed = random.randrange(sys.maxsize)
            if test_seed(num_transforms, moebius_chance, seed):
                main_window.Element("seed").Update(str(seed))
                break

    if event == "seed":
        seed = int(values["seed"])

    if event == "Render to File":
        ifsi = IFSI(width, height, iterations, num_points, num_transforms, moebius_chance, seed).render().save()
        image_window = sg.Window(ifsi.filename, [[sg.Image(ifsi.filename)]])
        image_window.Finalize()

    if event.startswith("editor"):
        x, y = values["editor"]
        if event.endswith("+UP"):
            print(f"UP {values['editor']}")
        else:
            print(f"DOWN {values['editor']}")


    # else:
    #     print(event, values)



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
