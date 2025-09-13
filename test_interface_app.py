import unittest
import main as appmod

class FakeLabel:
    def __init__(self):
        self.text = ""

class FakeRoot:
    def __init__(self):
        self.ids = {"output_label": FakeLabel()}

class FakeWidget:
    def __init__(self, source, state="down"):
        self.source = source
        self.state = state

def fmt3(a, b, c):
    def f(v): return f"{int(v):02d}"
    return f"{f(a)} {f(b)} {f(c)}"

class InterfaceAppTests(unittest.TestCase):
    def setUp(self):
        self.app = appmod.InterfaceApp()
        self.app.root = FakeRoot()
        self.app.sel_x = self.app.sel_y = self.app.sel_z = 0
        self.app.has_x = self.app.has_y = self.app.has_z = False
        self.app.calc_x = self.app.calc_y = self.app.calc_z = 0
        self.app.update_display()

    def test_initial_display_shows_dashes(self):
        self.assertEqual(self.app.root.ids["output_label"].text, "-- -- --")
        self.assertEqual((self.app.sel_x, self.app.sel_y, self.app.sel_z), (0, 0, 0))
        self.assertEqual((self.app.has_x, self.app.has_y, self.app.has_z), (False, False, False))

    def test_partial_selection_still_dashes(self):
        w = FakeWidget(source="assets/2.jpg", state="down")
        self.app.on_select(w, row="row_x")
        self.assertTrue(self.app.has_x)
        self.assertEqual(self.app.sel_x, 10)
        self.assertEqual(self.app.root.ids["output_label"].text, "-- -- --")
        self.assertEqual((self.app.calc_x, self.app.calc_y, self.app.calc_z), (0, 0, 0))

    def test_all_selected_computation_and_display(self):
        self.app.on_select(FakeWidget("assets/3.jpg", "down"), row="row_x")
        self.app.on_select(FakeWidget("assets/5.jpg", "down"), row="row_y")
        self.app.on_select(FakeWidget("assets/6.jpg", "down"), row="row_z")
        self.assertEqual((self.app.calc_x, self.app.calc_y, self.app.calc_z), (33, 60, 32))
        self.assertEqual(self.app.root.ids["output_label"].text, "33 60 32")

    def test_deselect_resets_and_dashes(self):
        self.app.on_select(FakeWidget("assets/4.jpg", "down"), row="row_x")
        self.app.on_select(FakeWidget("assets/2.jpg", "down"), row="row_y")
        self.app.on_select(FakeWidget("assets/1.jpg", "down"), row="row_z")
        self.assertNotEqual(self.app.root.ids["output_label"].text, "-- -- --")
        self.app.on_select(FakeWidget("assets/2.jpg", "normal"), row="row_y")
        self.assertFalse(self.app.has_y)
        this_run = (self.app.calc_x, self.app.calc_y, self.app.calc_z)
        self.assertEqual(this_run, (0, 0, 0))
        self.assertEqual(self.app.root.ids["output_label"].text, "-- -- --")

    def test_reselect_recomputes_from_raw_not_compound(self):
        self.app.on_select(FakeWidget("assets/3.jpg", "down"), row="row_x")
        self.app.on_select(FakeWidget("assets/5.jpg", "down"), row="row_y")
        self.app.on_select(FakeWidget("assets/4.jpg", "down"), row="row_z")
        first = (self.app.calc_x, self.app.calc_y, self.app.calc_z)
        self.assertEqual(self.app.root.ids["output_label"].text, fmt3(*first))
        self.app.on_select(FakeWidget("assets/6.jpg", "down"), row="row_y")
        self.assertEqual((self.app.calc_x, self.app.calc_y, self.app.calc_z), (33, 57, 31))
        self.assertEqual(self.app.root.ids["output_label"].text, "33 57 31")

    def test_value_map_for_x_row(self):
        cases = [
            ("assets/1.jpg", 0),
            ("assets/2.jpg", 10),
            ("assets/3.jpg", 11),
            ("assets/4.jpg", 20),
            ("assets/5.jpg", 21),
            ("assets/6.jpg", 22),
        ]
        for img, val in cases:
            with self.subTest(img=img, val=val):
                self.app.on_select(FakeWidget(img, "down"), row="row_x")
                self.assertEqual(self.app.sel_x, val)
                self.assertEqual(self.app.root.ids["output_label"].text, "-- -- --")
                self.app.on_select(FakeWidget(img, "normal"), row="row_x")
                self.assertEqual(self.app.sel_x, 0)
                self.assertFalse(self.app.has_x)
                self.assertEqual(self.app.root.ids["output_label"].text, "-- -- --")

    def test_equation_outputs_for_combinations(self):
        cases = [
            ("assets/1.jpg", "assets/2.jpg", "assets/3.jpg", "11 27 21"),
            ("assets/4.jpg", "assets/5.jpg", "assets/6.jpg", "51 60 23"),
            ("assets/2.jpg", "assets/1.jpg", "assets/4.jpg", "31 35 10"),
        ]
        for x_img, y_img, z_img, exp in cases:
            with self.subTest(x=x_img, y=y_img, z=z_img):
                app = appmod.InterfaceApp()
                app.root = FakeRoot()
                app.update_display()
                app.on_select(FakeWidget(x_img, "down"), row="row_x")
                app.on_select(FakeWidget(y_img, "down"), row="row_y")
                app.on_select(FakeWidget(z_img, "down"), row="row_z")
                self.assertEqual(app.root.ids["output_label"].text, exp)

if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(InterfaceAppTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    failures = len(result.failures)
    errors = len(result.errors)
    passed = result.testsRun - failures - errors
    print(f"\nSUMMARY: PASSED={passed}  FAILED={failures}  ERRORS={errors}")
