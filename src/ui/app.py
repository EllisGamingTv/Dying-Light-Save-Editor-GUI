import tkinter as tk
from tkinter import ttk, filedialog
import json
import os
import subprocess
import shutil
import time
import webbrowser

from logic.batch import run_batch

EDITOR_DIR = r"C:\Editor"
SAMPLE_BAT = os.path.join(EDITOR_DIR, "sample.bat")
UPDATE_BAT = os.path.join(EDITOR_DIR, "update.bat")
DEFAULT_JSON = os.path.join(EDITOR_DIR, "save_coop_0.sav(edited).json")
SAVE_PATH = os.path.join(EDITOR_DIR, "save_coop_0.sav")
JSON_PATH = os.path.join(EDITOR_DIR, "save_coop_0.sav(edited).json")
TEMP_JSON = os.path.join(EDITOR_DIR, "._tmp.json")
TEMP_SAVE = os.path.join(EDITOR_DIR, "._tmp.sav")


class SaveEditorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Dying Light Json Editor UI")
        self.geometry("1000x700")

        self.json_path = DEFAULT_JSON
        self.current_data = None
        self.weapon_map = {}
        self.inventory_map = {}
        self.skill_map = {}
        self.clipboard_data = None
        self.global_map = {}

        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_widgets(self):
        top = tk.Frame(self)
        top.pack(fill=tk.X, pady=5)

        tk.Button(top, text="Open Save", command=self.load_save).pack(side=tk.LEFT, padx=5)
        tk.Button(top, text="Save Changes", command=self.save_changes).pack(side=tk.LEFT, padx=5)
        tk.Button(top, text="Browse JSON", command=self.choose_file).pack(side=tk.LEFT, padx=5)
        tk.Button(top, text="About", command=self.show_about).pack(side=tk.LEFT, padx=5)

        self.status = tk.Label(top, text="")
        self.status.pack(side=tk.RIGHT, padx=10)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.tab_weapons = ttk.Frame(self.notebook)
        self.tab_inventory = ttk.Frame(self.notebook)
        self.tab_skills = ttk.Frame(self.notebook)
        self.tab_stats = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_weapons, text="Weapons")
        self.notebook.add(self.tab_inventory, text="Inventory")
        self.notebook.add(self.tab_skills, text="Skills")
        self.notebook.add(self.tab_stats, text="Stats")

    def choose_file(self):
        path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if path:
            self.json_path = path

    def set_status(self, text):
        self.status.config(text=text)
        self.update()

    def load_save(self):
        self.set_status("Decrypting...")

        current_save = SAVE_PATH

        subprocess.run(
            [
                "editor.exe",
                "sample",
                current_save,
                f"--patch={TEMP_JSON}"
            ],
            cwd=EDITOR_DIR,
            shell=True
        )

        if os.path.exists(TEMP_JSON):
            with open(TEMP_JSON, "r", encoding="utf-8") as f:
                self.current_data = json.load(f)
            self.populate()

        self.set_status("")

    def save_changes(self):
        if not self.current_data:
            return
        self.focus()

        self.set_status("Saving...")

        with open(TEMP_JSON, "w", encoding="utf-8") as f:
            json.dump(self.current_data, f, indent=4)
            f.flush()
            os.fsync(f.fileno())

        time.sleep(0.2)

        subprocess.run(
            [
                "editor.exe",
                "update",
                SAVE_PATH,
                f"--patch={TEMP_JSON}",
                f"--output={TEMP_SAVE}"
            ],
            cwd=EDITOR_DIR,
            shell=True
        )

        shutil.move(TEMP_SAVE, SAVE_PATH)

        self.load_save()
        
        if os.path.exists(TEMP_JSON):
            os.remove(TEMP_JSON)
            
        self.set_status("")

    def populate(self):
        for tab in (self.tab_weapons, self.tab_inventory, self.tab_skills, self.tab_stats):
            for widget in tab.winfo_children():
                widget.destroy()


        player = self.current_data.get("player", {})

        player = self.current_data.get("player", {})

        weapons = player.get("inventory", {}).get("equipmentSlots", [])
        items = player.get("inventory", {}).get("items3", [])
        skills = player.get("buffs", []) + player.get("skills", [])

        self.weapon_map.clear()
        self.inventory_map.clear()
        self.skill_map.clear()

        self.create_table(
            self.tab_weapons,
            ["name","quantity","condition","repairs","id","craftPlan","upgradeSockets"],
            weapons,
        self.weapon_map
        )

        self.create_table(
            self.tab_inventory,
            ["name","quantity","id","craftPlan","upgradeSockets"],
            items,
            self.inventory_map
        )

        self.create_table(self.tab_skills, ["name","stacks"], skills, self.skill_map)

        self.create_stats(self.tab_stats, player)

    def create_stats(self, parent, player):
        for key in ["health", "fury", "cash"]:
            frame = tk.Frame(parent)
            frame.pack(pady=5)

            tk.Label(frame, text=key, width=10).pack(side=tk.LEFT)
            tk.Button(frame, text="Max", command=lambda: var.set("99999999")).pack(side=tk.LEFT)

            if key == "cash":
                value = player.get("inventory", {}).get("cash", 0)
            else:
                value = player.get(key, 0)

            var = tk.StringVar(value=str(value))
            entry = tk.Entry(frame, textvariable=var)
            entry.pack(side=tk.LEFT)

            def save_value(e=None, k=key, v=var):
                try:
                    if k == "cash":
                        player["inventory"]["cash"] = int(v.get())
                    else:
                        player[k] = float(v.get())
                except:
                    pass

            entry.bind("<Return>", save_value)
            entry.bind("<FocusOut>", save_value)

    def create_table(self, parent, columns, data, map_ref):
        tree = ttk.Treeview(parent, columns=columns, show="headings")
        self.tree = tree
        tree = self.tree

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)

        tree.pack(fill=tk.BOTH, expand=True)

        menu = tk.Menu(tree, tearoff=0)
        menu.add_command(label="Copy", command=lambda: self.copy_row(tree))
        menu.add_command(label="Paste", command=lambda: self.paste_row(tree))
        menu.add_command(label="Duplicate", command=lambda: self.duplicate_row(tree))

        def show_menu(event):
            row = tree.identify_row(event.y)
            if row:
                tree.selection_set(row)
                menu.post(event.x_root, event.y_root)

        tree.bind("<Button-3>", show_menu)

        for index, item in enumerate(data):
            values = []
            for col in columns:
                if col == "stacks":
                    if "stacks" in item:
                        values.append(item["stacks"])
                    elif "unknown" in item and "unknown001" in item["unknown"]:
                        values.append(item["unknown"]["unknown001"])
                    else:
                        values.append("")
                else:
                    if col == "upgradeSockets":
                        values.append(",".join(item.get("upgradeSockets", [])))
                    else:
                        values.append(item.get(col, ""))
            row_id = tree.insert("", tk.END, values=values)
            map_ref[row_id] = (tree, index, data)
            self.global_map[(tree, row_id)] = (index, data)

        tree.bind("<Double-1>", lambda e: self.edit_cell(e, tree, columns))

    def edit_cell(self, event, tree, columns):
        row_id = tree.identify_row(event.y)
        if not row_id:
            return

        col_index = int(tree.identify_column(event.x)[1:]) - 1
        key = columns[col_index]

        x, y, width, height = tree.bbox(row_id, f"#{col_index+1}")

        entry = tk.Entry(tree)
        entry.place(x=x, y=y, width=width, height=height)

        current_value = tree.item(row_id)["values"][col_index]
        entry.insert(0, current_value)
        entry.focus()

        def save_edit(e=None):
            new_value = entry.get()
            index, parent_list = self.global_map[(tree, row_id)]
            item = parent_list[index]

            try:
                if key == "name":
                    item[key] = new_value

                elif key == "stacks":
                    if "stacks" in item:
                        item["stacks"] = int(new_value)
                    elif "unknown" in item and "unknown001" in item["unknown"]:
                        item["unknown"]["unknown001"] = int(new_value)

                elif key in ["quantity", "repairs", "id"]:
                    item[key] = int(new_value)

                elif key == "condition":
                    item[key] = float(new_value)

                elif key == "craftPlan":
                    item[key] = new_value

                elif key == "upgradeSockets":
                    item["upgradeSockets"] = [s.strip() for s in new_value.split(",") if s.strip()]

                else:
                    item[key] = new_value

                values = list(tree.item(row_id)["values"])
                values[col_index] = new_value
                tree.item(row_id, values=values)

            except Exception as e:
                print("ERROR:", e, "| value:", new_value)
                return

            entry.destroy()

        entry.bind("<Return>", save_edit)
        entry.bind("<FocusOut>", save_edit)

    def copy_row(self, tree):
        selected = tree.selection()
        if not selected:
            return

        row_id = selected[0]

        for map_ref in [self.weapon_map, self.inventory_map, self.skill_map]:
            if row_id in map_ref:
                _, index, data = map_ref[row_id]
                self.clipboard_data = data[index].copy()
                break

    def paste_row(self, tree):
        selected = tree.selection()
        if not selected or not self.clipboard_data:
            return

        row_id = selected[0]

        for map_ref in [self.weapon_map, self.inventory_map, self.skill_map]:
            if row_id in map_ref:
                tree, target, _ = map_ref[row_id]
                break

        for key in self.clipboard_data:
            target[key] = self.clipboard_data[key]

        values = [target.get(col, "") for col in tree["columns"]]
        tree.item(row_id, values=values)
        
    def show_about(self):

        win = tk.Toplevel(self)
        win.title("About")
        win.geometry("400x200")

        tk.Label(win, text="Dying Light Json Editor UI by Kayo", font=("Arial", 14)).pack(pady=10)

        tk.Label(
            win,
            text="This tool requires Steffen's Save Editor to work.",
            wraplength=350,
            justify="center"
        ).pack(pady=5)

        link = tk.Label(win, text="Download here", fg="blue", cursor="hand2")
        link.pack(pady=10)

        def open_link(e):
            webbrowser.open("https://steffenl.com/projects/dying-light-save-editor/releases")

        link.bind("<Button-1>", open_link)
        
    def cleanup(self):
        if os.path.exists(TEMP_JSON):
            os.remove(TEMP_JSON)
        if os.path.exists(TEMP_SAVE):
            os.remove(TEMP_SAVE)
                
    def on_close(self):
        self.cleanup()
        self.destroy()
        
    def duplicate_row(self, tree):
        selected = tree.selection()
        if not selected:
            return

        row_id = selected[0]

        for map_ref in [self.weapon_map, self.inventory_map, self.skill_map]:
            if row_id in map_ref:
                _, index, data = map_ref[row_id]

                new_item = data[index].copy()

                data.append(new_item)
                break

        self.populate()