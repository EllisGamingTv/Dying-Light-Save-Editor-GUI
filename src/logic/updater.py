import requests
import threading
import webbrowser

from packaging import version
from tkinter import messagebox

CURRENT_VERSION = "1.6"

GITHUB_API = (
    "https://api.github.com/repos/"
    "EllisGamingTv/Dying-Light-Save-Editor-GUI/releases/latest"
)

def check_updates_async(app):
    threading.Thread(
        target=check_updates,
        args=(app,),
        daemon=True
    ).start()


def check_updates(app):
    try:
        response = requests.get(GITHUB_API, timeout=5)

        if response.status_code != 200:
            return

        data = response.json()

        latest = data["tag_name"].replace("v", "")

        if version.parse(latest) > version.parse(CURRENT_VERSION):

            def show_popup():
                result = messagebox.askyesno(
                    "Update Available",
                    f"A new version is available.\n\n"
                    f"Current: {CURRENT_VERSION}\n"
                    f"Latest: {latest}\n\n"
                    f"Open download page?"
                )

                if result:
                    webbrowser.open(data["html_url"])

            app.after(0, show_popup)

    except Exception as e:
        print("[Updater Error]", e)