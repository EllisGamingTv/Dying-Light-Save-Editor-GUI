import os
import importlib.util
import sys
import traceback
import builtins

BANNED_MODULES = {
    "os",
    "subprocess",
    "socket",
    "shutil",
    "ctypes",
    "requests",
    "urllib",
    "http",
    "ftplib",
    "telnetlib",
    "webbrowser",
    "winreg",
    "pathlib",
    "builtins"
    "sys"
}


def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)

    return os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )


def load_plugins():
    plugins = []

    base_path = get_base_path()

    plugin_folder = os.path.join(
        base_path,
        "plugins"
    )

    if not os.path.exists(plugin_folder):
        return plugins

    REAL_IMPORT = builtins.__import__

    def safe_import(
        name,
        globals=None,
        locals=None,
        fromlist=(),
        level=0
    ):
        root = name.split(".")[0]

        if root in BANNED_MODULES:
            raise ImportError(
                f"Blocked dangerous module: {root}"
            )

        return REAL_IMPORT(
            name,
            globals,
            locals,
            fromlist,
            level
        )

    for file in os.listdir(plugin_folder):

        if not file.endswith((".py", ".pyc")):
            continue

        file_path = os.path.join(
            plugin_folder,
            file
        )

        module_name = (
            f"plugin_{os.path.splitext(file)[0]}"
        )

        try:

            if module_name in sys.modules:
                del sys.modules[module_name]

            spec = importlib.util.spec_from_file_location(
                module_name,
                file_path
            )

            if not spec or not spec.loader:
                continue

            module = importlib.util.module_from_spec(spec)

            sys.modules[module_name] = module

            old_import = builtins.__import__
            builtins.__import__ = safe_import

            try:
                spec.loader.exec_module(module)

            finally:
                builtins.__import__ = old_import

            if (
                hasattr(module, "run")
                or hasattr(module, "init_ui")
            ):

                plugins.append({
                    "name": getattr(
                        module,
                        "PLUGIN_NAME",
                        file[:-3]
                    ),

                    "run": getattr(
                        module,
                        "run",
                        None
                    ),

                    "init_ui": getattr(
                        module,
                        "init_ui",
                        None
                    ),

                    "refresh": getattr(
                        module,
                        "refresh",
                        None
                    ),

                    "module": module
                })

        except Exception as e:

            print(
                f"[PLUGIN ERROR] {file}"
            )

            print(str(e))

            traceback.print_exc()

    return plugins