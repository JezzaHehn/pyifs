import config, getopt, os, random, sys
from ifs import get_seed, IFSI

def print_help():
    print("""
    -?, --help: Display this list
    --headless: Run headless (without graphical interface)
    -w, --width: Image width
    -h, --height: Image height

    Headless options
    -c, --count: Number of images to create
    """)

# First, process command line args
try:
    opts, args = getopt.getopt(sys.argv[1:], "?cwh",
                 ["help","headless","count","width","height"])
except getopt.error as msg:
    sys.stdout = sys.stderr
    print(msg)
    print_help()
    sys.exit(2)

# Set default values, then correct as needed per arg
HEADLESS = False
for opt, arg in opts:
    if opt in ["-?","--help"]:
        print_help(sys.argv[0])
        sys.exit(0)
    if opt in ["--headless"]:
        HEADLESS = True
    if opt in ["-c","--count"]:
        config.image_count = int(arg)
        HEADLESS = True
    if opt in ["-w","--width"]:
        config.width = int(arg)
    if opt in ["-h","--height"]:
        config.height = int(arg)
# if args and args[0] != '-':
#     with open(args[0], 'rb') as f:
#         func(f, sys.stdout.buffer)
# else:
#     func(sys.stdin.buffer, sys.stdout.buffer)


if HEADLESS:
    # Create small images as dataset for classifier and GAN experiments
    for subdir, num in [("training",500),("validation",50)]:
        for i in range(num):
            path = os.path.join("data", subdir, "ifs")
            if not os.path.exists(path): os.makedirs(path)
            filename = os.path.join(path, "%03d"%i + ".png")
            # Create new ONLY if that filename hasn't been used yet
            # (for manual data sanitation, selective regeneration)
            if not os.path.exists(filename):
                ifsi = IFSI(config.width, config.height, config.iterations,
                            config.num_points, config.num_transforms,
                            config.moebius_chance, config.spherical_chance,
                            get_seed(config.num_transforms, config.moebius_chance,
                            config.spherical_chance), filename=filename)
                ifsi.render().save_image()

else:
    # Set up gui
    import PySimpleGUI as sg
    from matplotlib import pyplot as plt
    plt.ion()

    # Set default colour scheme for windows
    sg.ChangeLookAndFeel('GreenTan')

    # Get a starting seed
    seed = get_seed(config.num_transforms, config.moebius_chance, config.spherical_chance)

    # Top menu buttons
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

    # Create and open the main window using the above layout
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
            try:
                seed = int(values["seed"])
            except ValueError:
                seed = 0

        if event == "Render to File":
            ifsi = IFSI(int(values["width"]), int(values["height"]),
                        int(values["iterations"]), int(values["num_points"]),
                        int(values["num_transforms"]), int(values["moebius_chance"])/100,
                        int(values["spherical_chance"])/100, seed)
            bar = main_window.Element("progress")
            bar.UpdateBar(0, int(values["num_points"]))
            if ifsi.render(bar=bar):
                ifsi.save_image()
                ifsi.save_parameters()
                plt.imshow(ifsi.get_image())
                plt.draw()
                image_window = sg.Window(ifsi.filename, [[sg.Image(ifsi.filename)]])
                image_window.Finalize()

        if event.startswith("editor"):
            x, y = values["editor"]
            if event.endswith("+UP"):
                print(f"UP {values['editor']}")
            else:
                print(f"DOWN {values['editor']}")

        else:
            # Print unrecognized events.
            # Mainly for debugging; shouldn't normally happen.
            print(event, values)
