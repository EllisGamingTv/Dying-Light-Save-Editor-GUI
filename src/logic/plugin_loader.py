import os
import importlib.util
import sys

def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def load_plugins():
    plugins = []

    base_path = get_base_path()
    plugin_folder = os.path.join(base_path, "plugins")

    if not os.path.exists(plugin_folder):
        return plugins

    for file in os.listdir(plugin_folder):
        if file.endswith(".py"):
            file_path = os.path.join(plugin_folder, file)

            try:
                spec = importlib.util.spec_from_file_location(file[:-3], file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                if hasattr(module, "run") or hasattr(module, "init_ui"):
                    plugins.append({
                        "name": getattr(module, "name", file[:-3]),
                        "run": getattr(module, "run", None),
                        "init_ui": getattr(module, "init_ui", None),
                        "refresh": getattr(module, "refresh", None),
                        "module": module
})

            except Exception as e:
                print(f"[PLUGIN ERROR] {file}: {e}")

    return plugins