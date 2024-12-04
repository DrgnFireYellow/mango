import tkinter
import tkhtmlview
import requests
import functools
import json
import webbrowser
import os


def base(root):
    for i in root.winfo_children():
        i.destroy()

    title_label = tkinter.Label(root, text="Mango", font="Sans-Serif 24")
    title_label.pack()

    info_label = tkinter.Label(root, text="A Minimal, Open Source GameBanana Client")
    info_label.pack()


def search_games(root):
    base(root)
    search_frame = tkinter.Frame(root)

    search_box = tkinter.Entry(search_frame)
    search_box.pack()
    search_box.focus()

    def show_search_results():
        search_games_results(root, search_box.get())

    search_button = tkinter.Button(
        search_frame, text="Search Games", command=show_search_results
    )
    search_button.pack()

    search_frame.pack(expand=True)


def search_games_results(root, query):
    base(root)

    back_button = tkinter.Button(
        root, text="⬅︎ Go Back", command=functools.partial(search_games, root)
    )
    back_button.pack(anchor=tkinter.NW)

    results_request = requests.get(
        f"https://gamebanana.com/apiv11/Util/Game/NameMatch?_sName={query}"
    )
    results = results_request.json()["_aRecords"]

    results_frame = tkinter.Frame(root)

    for index, result in enumerate(results):
        tkinter.Label(results_frame, text=result["_sName"], font="Sans-Serif 18").grid(
            row=index + 1, column=1
        )
        tkinter.Button(
            results_frame,
            text="Select",
            command=functools.partial(game, root, result["_idRow"]),
        ).grid(row=index + 1, column=2)

    results_frame.pack(expand=True)


def game(root, game_id):
    base(root)

    back_button = tkinter.Button(
        root, text="⬅︎ Go Back", command=functools.partial(search_games, root)
    )
    back_button.pack(anchor=tkinter.NW)

    name = requests.get(
        f"http://api.gamebanana.com/Core/Item/Data?itemtype=Game&itemid={game_id}&fields=name"
    ).json()[0]

    title_label = tkinter.Label(root, text=name, font="Sans-Serif 18")
    title_label.pack()

    search_frame = tkinter.Frame(root)

    search_box = tkinter.Entry(search_frame)
    search_box.pack()
    search_box.focus()

    def show_search_results():
        search_mods_results(root, game_id, search_box.get())

    search_button = tkinter.Button(
        search_frame, text="Search Mods", command=show_search_results
    )
    search_button.pack()

    search_frame.pack(pady=(0, 20))

    featured_root = tkinter.Canvas(root)

    featured_items = requests.get(
        f"https://gamebanana.com/apiv11/Util/List/Featured?_nPage=1&_idGameRow={game_id}"
    ).json()["_aRecords"]

    for index, item in enumerate(featured_items):
        if item["_sModelName"] == "Mod" or item["_sModelName"] == "Wip":
            tkinter.Label(
                featured_root, text=item["_sName"], font="Sans-Serif 16"
            ).grid(row=index + 1, column=1)
            tkinter.Button(
                featured_root,
                text="View",
                command=functools.partial(
                    mod, root, item["_idRow"], item["_sModelName"]
                ),
            ).grid(row=index + 1, column=2)

    featured_root.pack()


def search_mods_results(root, game_id, query):
    base(root)

    back_button = tkinter.Button(
        root, text="⬅︎ Go Back", command=functools.partial(search_games, root)
    )
    back_button.pack(anchor=tkinter.NW)

    results_root = tkinter.Canvas(root)

    results = requests.get(
        f"https://gamebanana.com/apiv11/Game/{game_id}/Subfeed?_nPage=1&_sSort=default&_sName={query}"
    ).json()["_aRecords"]

    for index, item in enumerate(results):
        if item["_sModelName"] == "Mod" or item["_sModelName"] == "Wip":
            tkinter.Label(results_root, text=item["_sName"], font="Sans-Serif 16").grid(
                row=index + 1, column=1
            )
            tkinter.Button(
                results_root,
                text="View",
                command=functools.partial(
                    mod, root, item["_idRow"], item["_sModelName"]
                ),
            ).grid(row=index + 1, column=2)

    results_root.pack(expand=True)


def mod(root, mod_id, type):
    base(root)

    back_button = tkinter.Button(
        root, text="⬅︎ Go Back", command=functools.partial(search_games, root)
    )
    back_button.pack(anchor=tkinter.NW)

    data = requests.get(
        f"http://api.gamebanana.com/Core/Item/Data?itemtype={type}&itemid={mod_id}&fields=name,text,Owner().name,screenshots,downloads"
    ).json()

    title_label = tkinter.Label(root, text=data[0], font="Sans-Serif 18")
    title_label.pack()

    author_label = tkinter.Label(root, text="By " + data[2])
    author_label.pack()

    downloads_label = tkinter.Label(root, text="Downloads: " + str(data[4]))
    downloads_label.pack()

    description = tkhtmlview.HTMLLabel(root, html=data[1])
    description.pack()

    button_frame = tkinter.Frame(root)

    download_button = tkinter.Button(
        button_frame,
        text="Download",
        command=functools.partial(download, root, mod_id, type),
    )
    download_button.grid(row=1, column=1)

    galleryhtml = ""

    for image in json.loads(data[3]):
        galleryhtml += f"<img src=\"https://images.gamebanana.com/img/ss/{type.lower()}s/{image['_sFile']}\" style=\"width: 75vw;\">"

    with open("temp.html", "w") as tempfile:
        tempfile.write(galleryhtml)

    gallery_button = tkinter.Button(
        button_frame,
        text="View Screenshots (Opens In Browser)",
        command=functools.partial(
            webbrowser.open, "file://" + os.path.abspath("temp.html")
        ),
    )
    gallery_button.grid(row=1, column=2)

    button_frame.pack()


def download(root, mod_id, type):
    base(root)

    back_button = tkinter.Button(
        root, text="⬅︎ Go Back", command=functools.partial(search_games, root)
    )
    back_button.pack(anchor=tkinter.NW)

    version_data = requests.get(
        f"http://api.gamebanana.com/Core/Item/Data?itemtype={type}&itemid={mod_id}&fields=Files().aFiles()"
    ).json()

    versions = version_data[0]

    versions_frame = tkinter.Frame(root)

    for index, version in enumerate(versions):
        tkinter.Label(
            versions_frame, text=versions[version]["_sFile"], font="Sans-Serif 18"
        ).grid(row=index + 1, column=1)
        tkinter.Button(
            versions_frame,
            text="Download",
            command=functools.partial(
                webbrowser.open, "https://gamebanana.com/dl/" + version
            ),
        ).grid(row=index + 1, column=2)

    versions_frame.pack()
