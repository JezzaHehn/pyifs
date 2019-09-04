import config, os, random, sys
import PySimpleGUI as sg
from ifs import get_seed, IFSI


# Set default colour scheme for windows
sg.ChangeLookAndFeel('GreenTan')

# Get a starting seed
seed = get_seed(config.num_transforms, config.moebius_chance, config.spherical_chance)

menu_def = [
    ["File", ["Open Parameters", "Save Parameters", "Save Image", "Exit"]],
    ["Edit", "Undo"],
    ["Help", "About..."]
]

main_layout = [
    [sg.Menu(menu_def, tearoff=True)],
    [
        sg.Text("Width", size=(8, 1), pad=(0,0)),
        sg.InputText(config.width, key="width", size=(10, 1), pad=(0,0)),
        sg.Text("Iterations", size=(10  , 1), pad=(10,0)),
        sg.InputText(config.iterations, key="iterations", size=(15, 20), pad=(0,0))
    ],
    [
        sg.Text("Height", size=(8, 1), pad=(0,0)),
        sg.InputText(config.height, key="height", size=(10, 1), pad=(0,0)),
        sg.Text("Num Points", size=(10, 1), pad=(10,0)),
        sg.InputText(config.num_points, key="num_points", size=(15, 20), pad=(0,0))
    ],
    [
        sg.Text("Number of Transforms", size=(15, 2), pad=(0,0)),
        sg.Slider(range=(1, 10), orientation="h", size=(20, 20), default_value=config.num_transforms, key="num_transforms")
    ],
    [
        sg.Text("Moebius Base Probability", size=(15, 2), pad=(0,0)),
        sg.Slider(range=(0, 100), orientation="h", size=(20, 20), default_value=int(config.moebius_chance*100), key="moebius_chance")
    ],
    [
        sg.Text("Spherical Base Probability", size=(15, 2), pad=(0,0)),
        sg.Slider(range=(0, 100), orientation="h", size=(20, 20), default_value=int(config.spherical_chance*100), key="spherical_chance")
    ],
    [
        sg.Button("Random Seed"),
        sg.InputText(seed, key="seed", size=(30,1), enable_events=True)
    ],
    [
        sg.Button("Render to File"),
        sg.ProgressBar(config.num_points, orientation="h", size=(20,20), key="progress")
    ]
]


main_window = sg.Window("PyIFS", main_layout)
main_window.Finalize()


# Main window event loop
while True:
    event, values = main_window.Read()
    if event is None or event == "Exit":
        break  # exit the program

    if event == "Random Seed":
        seed = get_seed(int(values["num_transforms"]), int(values["moebius_chance"])/100, int(values["spherical_chance"])/100)
        main_window.Element("seed").Update(str(seed))

    if event == "seed":
        seed = int(values["seed"])

    if event == "Render to File":
        ifsi = IFSI(int(values["width"]), int(values["height"]),
                    int(values["iterations"]), int(values["num_points"]),
                    int(values["num_transforms"]), int(values["moebius_chance"])/100,
                    int(values["spherical_chance"])/100, seed)
        bar = main_window.Element("progress")
        bar.max_value = int(values["num_points"])
        if ifsi.render(bar=bar):
            ifsi.save()
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
