from pathlib import Path
import os
import sys

from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.modules import inspector
from kivy.properties import NumericProperty, BooleanProperty
from kivy.resources import resource_add_path, resource_find

VALUE_MAP = {
    "row_x": {1: 0, 2: 10, 3: 11, 4: 20, 5: 21, 6: 22},
    "row_y": {1: 0, 2: 10, 3: 11, 4: 20, 5: 21, 6: 22},
    "row_z": {1: 0, 2: 10, 3: 11, 4: 20, 5: 21, 6: 22},
}

ASSETS_DIR = "assets"

def _base_dir():
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

def _add_resource_paths():
    base = _base_dir()
    resource_add_path(base)
    resource_add_path(os.path.join(base, ASSETS_DIR))

def _asset_path(relpath: str) -> str:

    _add_resource_paths()
    if not relpath.startswith(f"{ASSETS_DIR}{os.sep}") and not relpath.startswith(f"{ASSETS_DIR}/"):
        relpath = os.path.join(ASSETS_DIR, relpath)
    resolved = resource_find(relpath)
    if not resolved:
        resolved = os.path.join(_base_dir(), relpath)
    return resolved

class BeamsmasherApp(App):
    sel_x = NumericProperty(0)
    sel_y = NumericProperty(0)
    sel_z = NumericProperty(0)
    has_x = BooleanProperty(False)
    has_y = BooleanProperty(False)
    has_z = BooleanProperty(False)

    calc_x = NumericProperty(0)
    calc_y = NumericProperty(0)
    calc_z = NumericProperty(0)

    def asset(self, relpath: str) -> str:
        return _asset_path(relpath)

    def build(self):
        _add_resource_paths()
        kv_path = resource_find("beamsmasher.kv") or os.path.join(_base_dir(), "beamsmasher.kv")
        if not os.path.exists(kv_path):
            raise FileNotFoundError(f"Couldn't locate beamsmasher.kv at: {kv_path}")
        root = Builder.load_file(kv_path)
        inspector.create_inspector(Window, self)
        self.update_display()
        return root

    def on_select(self, widget, row):
        if widget.state == "down":
            try:
                raw = int(Path(widget.source).stem)
            except Exception:
                return
            mapped = VALUE_MAP.get(row, {}).get(raw, raw)
            if row == "row_x":
                self.sel_x, self.has_x = mapped, True
            elif row == "row_y":
                self.sel_y, self.has_y = mapped, True
            elif row == "row_z":
                self.sel_z, self.has_z = mapped, True
        else:
            if row == "row_x":
                self.sel_x, self.has_x = 0, False
            elif row == "row_y":
                self.sel_y, self.has_y = 0, False
            elif row == "row_z":
                self.sel_z, self.has_z = 0, False

        if self.has_x and self.has_y and self.has_z:
            self.compute_xyz()
        else:
            self.calc_x = self.calc_y = self.calc_z = 0
            self.update_display()

    def compute_xyz(self):
        x, y, z = self.sel_x, self.sel_y, self.sel_z
        self.calc_x = (x * 2) + 11
        self.calc_y = ((2 * z) + y) - 5
        self.calc_z = abs((y + z) - x)
        self.update_display()

    def update_display(self):
        if not (self.has_x and self.has_y and self.has_z):
            text = "-- -- --"
        else:
            def fmt(v): return f"{int(v):02d}"
            text = f"{fmt(self.calc_x)} {fmt(self.calc_y)} {fmt(self.calc_z)}"
        if self.root and "output_label" in self.root.ids:
            self.root.ids["output_label"].text = text

if __name__ == "__main__":
    BeamsmasherApp().run()
