import os
import importlib.util
import sys
import traceback

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
        if not file.endswith(".py"):
            continue

        file_path = os.path.join(plugin_folder, file)
        module_name = f"plugin_{file[:-3]}"

        try:
            if module_name in sys.modules:
                del sys.modules[module_name]

            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)

            sys.modules[module_name] = module

            if spec and spec.loader:
                spec.loader.exec_module(module)
            else:
                continue

            if hasattr(module, "run") or hasattr(module, "init_ui"):
                plugins.append({
                    "name": getattr(module, "PLUGIN_NAME", file[:-3]),
                    "run": getattr(module, "run", None),
                    "init_ui": getattr(module, "init_ui", None),
                    "refresh": getattr(module, "refresh", None),
                    "module": module
                })

        except Exception:
            print(f"[PLUGIN ERROR] {file}")
            traceback.print_exc()

    return plugins