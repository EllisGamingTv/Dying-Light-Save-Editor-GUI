import tkinter as tk
from tkinter import ttk, filedialog
import json
import os
import subprocess
import shutil
import time
import webbrowser

from logic.batch import run_batch
from logic.cheats import max_kings, max_quantity, max_skill
from logic.plugin_loader import load_plugins

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
        self.title("Dying Light Save Editor GUI")
        self.geometry("1000x700")

        self.json_path = DEFAULT_JSON
        self.current_data = None
        self.weapon_map = {}
        self.inventory_map = {}
        self.skill_map = {}
        self.clipboard_data = None
        self.global_map = {}
        self.plugins = load_plugins()

        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.current_tree = None
        for plugin in self.plugins:
            if plugin["init_ui"]:
                plugin["init_ui"](self)
    def create_widgets(self):
        top = tk.Frame(self)
        top.pack(fill=tk.X, pady=5)

        tk.Button(top, text="Open Save", command=self.load_save).pack(side=tk.LEFT, padx=5)
        tk.Button(top, text="Save Changes", command=self.save_changes).pack(side=tk.LEFT, padx=5)
        tk.Button(top, text="Browse JSON", command=self.choose_file).pack(side=tk.LEFT, padx=5)
        tk.Button(top, text="About", command=self.show_about).pack(side=tk.LEFT, padx=5)
        tk.Button(top, text="Full Kings", command=self.max_kings).pack(side=tk.LEFT, padx=5)
        tk.Button(top, text="Max Amount", command=self.max_amount).pack(side=tk.LEFT, padx=5)

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
        plugin_frame = tk.LabelFrame(self, text="Plugins")
        plugin_frame.pack(fill=tk.X, pady=5)

        for plugin in self.plugins:
            tk.Button(
                plugin_frame,
                text=plugin["name"],
                command=lambda p=plugin: self.run_plugin(p)
            ).pack(side=tk.LEFT, padx=5)

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

        inventory = player.get("inventory", {})

        all_items = (
            inventory.get("items1", []) +
            inventory.get("quickSlots", []) +
            inventory.get("equipmentSlots", [])
        )

        weapons = [
            item for item in all_items
            if isinstance(item, dict)
        ]
        items = player.get("inventory", {}).get("items3", [])
        skills = player.get("buffs", []) + player.get("skills", [])

        self.weapon_map.clear()
        self.inventory_map.clear()
        self.skill_map.clear()
        btn_frame = tk.Frame(self.tab_skills)
        btn_frame.pack(fill=tk.X, pady=5)

        tk.Button(
            btn_frame,
            text="Add All Legend Skills",
            command=self.add_legend_skills
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="Delete Selected",
            command=self.delete_selected_skills
        ).pack(side=tk.LEFT, padx=5)

        btn_frame = tk.Frame(self.tab_weapons)
        btn_frame.pack(fill=tk.X, pady=5)

        tk.Button(
            btn_frame,
            text="Max Condition + Reset Repairs",
            command=self.max_weapon_stats
        ).pack(side=tk.LEFT, padx=5)

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
        for key in ["health", "fury"]:
            frame = tk.Frame(parent)
            frame.pack(pady=5)

            tk.Label(frame, text=key, width=10).pack(side=tk.LEFT)

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
                        if "inventory" not in player:
                            player["inventory"] = {}
                        player["inventory"]["cash"] = int(v.get())
                    else:
                        player[k] = float(v.get())
                except:
                    pass

            entry.bind("<Return>", save_value)
            entry.bind("<FocusOut>", save_value)

            tk.Button(frame, text="Max", command=lambda v=var: v.set("99999999")).pack(side=tk.LEFT)
            frame = tk.Frame(parent)
            frame.pack(pady=10)

            tk.Label(frame, text="Money", width=10).pack(side=tk.LEFT)

            value = player.get("inventory", {}).get("cash", 0)

            var = tk.StringVar(value=str(value))
            entry = tk.Entry(frame, textvariable=var)
            entry.pack(side=tk.LEFT)

            def save_cash(e=None, v=var):
                try:
                    if "inventory" not in player:
                        player["inventory"] = {}
                    player["inventory"]["cash"] = int(v.get())
                except:
                    pass

            entry.bind("<Return>", save_cash)
            entry.bind("<FocusOut>", save_cash)

            tk.Button(frame, text="Max", command=lambda: var.set("99999999")).pack(side=tk.LEFT)

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
        tree.bind("<Button-1>", lambda e: setattr(self, "current_tree", tree))

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
            self.global_map[(tree, row_id)] = (index, data, item)

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
            index, parent_list, item = self.global_map[(tree, row_id)]

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

        tk.Label(win, text="Dying Light Save Editor GUI By paradox32000", font=("Arial", 14)).pack(pady=10)

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
        
    def max_kings(self):
        if not self.current_data:
            return

        tree = self.current_tree
        if not tree:
            return

        selected = tree.selection()
        if not selected:
            return

        row_id = selected[0]
        index, parent_list, item = self.global_map[(tree, row_id)]

        max_kings(item)

        self.populate()
        
    def max_amount(self):
        if not self.current_data:
            return

        tree = self.current_tree
        if not tree:
            return

        selected = tree.selection()

        if selected:
            row_id = selected[0]
            index, parent_list, item = self.global_map[(tree, row_id)]

            if "quantity" in item:
                max_quantity(item)

            elif "stacks" in item:
                max_skill(item)

            elif "unknown" in item and "unknown001" in item["unknown"]:
                item["unknown"]["unknown001"] = 9999

        else:
            player = self.current_data.get("player", {})
            inv = player.get("inventory", {})

            for obj in inv.get("equipmentSlots", []):
                if "quantity" in obj:
                    obj["quantity"] = 999999999

            for obj in inv.get("items3", []):
                if "quantity" in obj:
                    obj["quantity"] = 999999999

            for skill in player.get("skills", []):
                if "stacks" in skill:
                    skill["stacks"] = 9999

            for buff in player.get("buffs", []):
                if "stacks" in buff:
                    buff["stacks"] = 9999
                elif "unknown" in buff and "unknown001" in buff["unknown"]:
                    buff["unknown"]["unknown001"] = 9999

        self.populate()
        
    def run_plugin(self, plugin):
        tree = self.current_tree
        if not tree:
            return

        selected = tree.selection()
        if not selected:
            return

        items = []
        for row_id in selected:
            index, parent_list, item = self.global_map[(tree, row_id)]
            items.append(item)

        if plugin["run"]:
            plugin["run"](self, items)

        self.populate()
        
    def add_legend_skills(self):
        if not self.current_data:
            return

        player = self.current_data.get("player", {})
        buffs = player.get("buffs", [])

        legend_skills = [
            "LegendSkill_UnarmedDamage",
            "LegendSkill_OneHandedDamage",
            "LegendSkill_TwoHandedDamage",
            "LegendSkill_FirearmsDamage",
            "LegendSkill_BowDamage",
            "LegendSkill_ThrowingDamage",
            "LegendSkill_MaxStamina",
            "LegendSkill_MaxHealth",
            "LegendSkill_HealthRegeneration",
            "LegendSkill_HealingEfficiency"
        ]

        existing = {b.get("name") for b in buffs}

        for skill in legend_skills:
            skill_name = skill + "_skill"

            if skill_name not in existing:
                buffs.append({
                    "name": skill_name,
                    "stacks": 25
                })

        player["buffs"] = buffs
        self.populate()
        
    def delete_selected_skills(self):
        tree = self.current_tree
        if not tree:
            return

        selected = tree.selection()
        if not selected:
            return

        player = self.current_data.get("player", {})

        for row_id in reversed(selected):
            if (tree, row_id) not in self.global_map:
                continue

            index, data, item = self.global_map[(tree, row_id)]

            if item in player.get("buffs", []):
                player["buffs"].remove(item)

            elif item in player.get("skills", []):
                player["skills"].remove(item)

        self.populate()
        
    def max_weapon_stats(self):
        if not self.current_data:
            return

        tree = self.current_tree
        if not tree:
            return

        selected = tree.selection()

        if selected:
            for row_id in selected:
                if (tree, row_id) not in self.global_map:
                    continue

                index, parent_list, item = self.global_map[(tree, row_id)]

                if "condition" in item:
                    item["condition"] = 999999

                if "repairs" in item:
                    item["repairs"] = 0

        else:
            player = self.current_data.get("player", {})
            inventory = player.get("inventory", {})

            for item in inventory.get("equipmentSlots", []):
                if "condition" in item:
                    item["condition"] = 999999
                if "repairs" in item:
                    item["repairs"] = 0

            for item in inventory.get("items3", []):
                if "condition" in item:
                    item["condition"] = 999999
                if "repairs" in item:
                    item["repairs"] = 0

        self.populate()