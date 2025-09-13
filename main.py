from pathlib import Path
from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.modules import inspector
from kivy.properties import NumericProperty, BooleanProperty

VALUE_MAP = {
    "row_x": {1: 0, 2: 10, 3: 11, 4: 20, 5: 21, 6: 22},
    "row_y": {1: 0, 2: 10, 3: 11, 4: 20, 5: 21, 6: 22},
    "row_z": {1: 0, 2: 10, 3: 11, 4: 20, 5: 21, 6: 22},
}

class InterfaceApp(App):
    sel_x = NumericProperty(0)
    sel_y = NumericProperty(0)
    sel_z = NumericProperty(0)
    has_x = BooleanProperty(False)
    has_y = BooleanProperty(False)
    has_z = BooleanProperty(False)

    calc_x = NumericProperty(0)
    calc_y = NumericProperty(0)
    calc_z = NumericProperty(0)

    def build(self):
        root = Builder.load_file("interface.kv")
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
    InterfaceApp().run()
