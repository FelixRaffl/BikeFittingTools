import sys
import math
import numpy as np

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout,
    QVBoxLayout, QFormLayout, QDoubleSpinBox, QLabel,
    QCheckBox, QSplitter, QScrollArea, QPushButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import pyqtgraph.opengl as gl


class BikeCAD(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pro Bike CAD - Pure Fit Geometry")
        self.resize(1400, 900)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.splitter)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMinimumWidth(360)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background-color: #f0f0f0; }")

        left_panel = QWidget()
        left_panel.setStyleSheet("background-color: #f0f0f0; padding: 10px;")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(10)

        self.scroll_area.setWidget(left_panel)
        self.splitter.addWidget(self.scroll_area)

        self.view = gl.GLViewWidget()
        self.view.setBackgroundColor('w')
        self.view.setCameraPosition(distance=1800, elevation=10, azimuth=-90)

        self.splitter.addWidget(self.view)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 3)
        self.splitter.setSizes([360, 1040])

        self.plot_items = []
        self.inputs = {}
        self.computed_geo = {}

        # 1. RAHMEN (Nur noch Stack, Reach & Winkel)
        self.add_header(left_layout, "1. RAHMEN (FRAME)", "#333333")
        frame_form = QFormLayout()
        frame_form.setVerticalSpacing(15)
        self.add_spinbox(frame_form, 'frame_stack', 'Frame Stack', 538.0, 400, 700, 1)
        self.add_spinbox(frame_form, 'frame_reach', 'Frame Reach', 386.0, 300, 500, 1)
        self.add_spinbox(frame_form, 'seat_angle', 'Seat Angle', 74.0, 65, 80, 0.1)
        self.add_spinbox(frame_form, 'head_angle', 'Head Angle', 72.0, 65, 80, 0.1)
        left_layout.addLayout(frame_form)

        left_layout.addSpacing(10)

        # 2. COCKPIT
        self.add_header(left_layout, "2. COCKPIT (FRONT)", "#333333")
        comp_form = QFormLayout()
        comp_form.setVerticalSpacing(12)
        self.add_spinbox(comp_form, 'spacer_height', 'Spacers (inc topcap)', 40.0, 0, 100, 1)
        self.add_spinbox(comp_form, 'stem_length', 'Stem Length', 90.0, 30, 150, 1)
        self.add_spinbox(comp_form, 'stem_angle', 'Stem Angle', -10.0, -30, 40, 1)
        self.add_spinbox(comp_form, 'bar_reach', 'Bar Reach', 75.0, 50, 120, 1)
        self.add_spinbox(comp_form, 'bar_width', 'Bar Width', 400.0, 320, 500, 10)
        self.add_spinbox(comp_form, 'bar_rise', 'Bar Rise', 20.0, 0, 50, 1)
        left_layout.addLayout(comp_form)
        
        left_layout.addSpacing(10)

        # 3. SATTEL
        self.add_header(left_layout, "3. SATTEL (REAR)", "#333333")
        saddle_form = QFormLayout()
        saddle_form.setVerticalSpacing(12)
        self.add_spinbox(saddle_form, 'saddle_height', 'Saddle Ht (BB)', 740.0, 500, 1000, 1)
        self.add_spinbox(saddle_form, 'saddle_setback', 'Saddle Setback', 198.0, 0, 300, 1)
        left_layout.addLayout(saddle_form)

        left_layout.addStretch()
        self.add_header(left_layout, "VISIBILITY & ACTIONS", "#333333")

        self.show_dims_cb = QCheckBox("Show Fit Dimensions")
        self.show_dims_cb.setChecked(True)
        self.show_dims_cb.setStyleSheet(
            "QCheckBox { color: black; font-weight: bold; font-size: 14px; margin-bottom: 5px; } "
            "QCheckBox::indicator { width: 18px; height: 18px; }"
        )
        self.show_dims_cb.stateChanged.connect(self.update_cad)
        left_layout.addWidget(self.show_dims_cb)

        self.show_frame_cb = QCheckBox("Show Frame Geo")
        self.show_frame_cb.setChecked(True)
        self.show_frame_cb.setStyleSheet(
            "QCheckBox { color: black; font-weight: bold; font-size: 14px; margin-bottom: 10px; } "
            "QCheckBox::indicator { width: 18px; height: 18px; }"
        )
        self.show_frame_cb.stateChanged.connect(self.update_cad)
        left_layout.addWidget(self.show_frame_cb)

        self.print_btn = QPushButton("Print Measurements")
        self.print_btn.setStyleSheet("""
            QPushButton {
                background-color: #333333;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 4px;
                margin-top: 5px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
        """)
        self.print_btn.clicked.connect(self.print_measurements)
        left_layout.addWidget(self.print_btn)

        self.update_cad()

    def add_header(self, layout, text, color):
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 15px; margin-top: 10px; margin-bottom: 5px;")
        layout.addWidget(lbl)

    def add_spinbox(self, layout, key, label, val, vmin, vmax, step):
        spin = QDoubleSpinBox()
        spin.setRange(vmin, vmax)
        spin.setValue(val)
        spin.setSingleStep(step)
        spin.setDecimals(1)
        spin.setMinimumHeight(32)
        spin.setStyleSheet("""
            QDoubleSpinBox { background-color: white; color: black; padding: 4px; border: 1px solid #ccc; border-radius: 3px; }
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button { width: 24px; }
        """)
        spin.valueChanged.connect(self.update_cad)
        lbl = QLabel(label + ":")
        lbl.setStyleSheet("color: black; font-weight: 500; font-size: 13px;")
        layout.addRow(lbl, spin)
        self.inputs[key] = spin

    def print_measurements(self):
        print("\n" + "="*40)
        print("        CURRENT BIKE MEASUREMENTS")
        print("="*40)
        print("\n--- INPUTS ---")
        for key, spin in self.inputs.items():
            label = key.replace('_', ' ').title()
            print(f"  {label:<22}: {spin.value():.1f}")
        print("\n--- MEASURED FIT OUTPUTS ---")
        if not self.computed_geo:
            print("  (Geometry not yet calculated)")
        else:
            for label, val in self.computed_geo.items():
                print(f"  {label:<22}: {val:.1f}")
        print("="*40 + "\n")

    def draw_line(self, p1, p2, color, width=3):
        pos = np.array([p1, p2], dtype=np.float32)
        line = gl.GLLinePlotItem(pos=pos, color=color, width=width, antialias=True)
        self.view.addItem(line)
        self.plot_items.append(line)

    def draw_curve(self, points, color, width=2):
        line = gl.GLLinePlotItem(pos=points, color=color, width=width, mode='line_strip', antialias=True)
        self.view.addItem(line)
        self.plot_items.append(line)

    def draw_points(self, points_list, color, size=12):
        pos = np.array(points_list, dtype=np.float32)
        scatter = gl.GLScatterPlotItem(pos=pos, color=color, size=size, pxMode=True)
        self.view.addItem(scatter)
        self.plot_items.append(scatter)

    def draw_3d_text(self, pos, text_str, color=(153, 51, 204, 255)):
        try:
            text_item = gl.GLTextItem(pos=pos, text=text_str, font=QFont("Arial", 11, QFont.Weight.Bold), color=color)
            self.view.addItem(text_item)
            self.plot_items.append(text_item)
        except Exception:
            pass

    def update_cad(self, *args):
        for item in self.plot_items:
            self.view.removeItem(item)
        self.plot_items.clear()

        v = {k: spin.value() for k, spin in self.inputs.items()}

        saddle_length = 270

        sa_rad = math.radians(v['seat_angle'])
        ha_rad = math.radians(v['head_angle'])

        bb_x, bb_y, bb_z = 0, 0, 0

        # Rahmen Startpunkte (Exakt am Stack und Reach)
        htt_x = v['frame_reach']
        htt_z = v['frame_stack']

        # Sattel Position berechnen
        seatpost_x = -v['saddle_height'] * math.cos(sa_rad)
        seatpost_z = v['saddle_height'] * math.sin(sa_rad)

        sm_x = -v['saddle_setback']
        sm_z = seatpost_z

        saddle_front_x = sm_x + (saddle_length / 2)
        saddle_rear_x = sm_x - (saddle_length / 2)

        # Cockpit Berechnung (inkl. Spacer Drift auf der schrägen Achse)
        steerer_top_x = htt_x - v['spacer_height'] * math.cos(ha_rad)
        steerer_top_z = htt_z + v['spacer_height'] * math.sin(ha_rad)

        stem_horiz_deg = (90 - v['head_angle']) + v['stem_angle']
        stem_rad = math.radians(stem_horiz_deg)

        bar_x = steerer_top_x + v['stem_length'] * math.cos(stem_rad)
        bar_z = steerer_top_z + v['stem_length'] * math.sin(stem_rad)

        hw = v['bar_width'] / 2
        hoods_x = bar_x + v['bar_reach']
        hoods_z = bar_z + v['bar_rise']

        # Finale Fitting-Messwerte (Differenzen zwischen Sattel und Griffe)
        saddle_drop = sm_z - hoods_z
        dx = hoods_x - sm_x
        dy = hw
        dz = sm_z - hoods_z
        reach_2d = dx
        reach_3d = math.sqrt(dx**2 + dy**2 + dz**2)

        st_virtual_x = -htt_z / math.tan(sa_rad)
        eff_top_tube_len = htt_x - st_virtual_x
        
        self.computed_geo = {
            'Measured Drop': saddle_drop,
            'Measured Reach (2D)': reach_2d,
            'Measured Reach (3D)': reach_3d,
            'Effective Top Tube': eff_top_tube_len,
        }

        # --- Zeichnen des "Pure Fit" Rahmens ---
        c_frame = (0.1, 0.1, 0.1, 1.0)
        
        # Virtuelles Sitzrohr (Tretlager bis Stack-Höhe)
        self.draw_line((bb_x, 0, bb_z), (st_virtual_x, 0, htt_z), c_frame, 10)
        # Oberrohr (virtuell horizontal)
        self.draw_line((st_virtual_x, 0, htt_z), (htt_x, 0, htt_z), c_frame, 10)
        # Abstraktes Unterrohr (schließt das Dreieck zum Tretlager)
        self.draw_line((htt_x, 0, htt_z), (bb_x, 0, bb_z), c_frame, 10)

        c_seatpost = (0.2, 0.6, 1.0, 1.0)
        c_saddle   = (0.9, 0.2, 0.2, 1.0)
        c_spacers  = (0.2, 0.8, 0.3, 1.0)
        c_stem     = (1.0, 0.5, 0.0, 1.0)
        c_bar      = (0.6, 0.2, 0.8, 1.0)

        self.draw_line((st_virtual_x, 0, htt_z), (seatpost_x, 0, seatpost_z), c_seatpost, 8)
        self.draw_line((seatpost_x, 0, seatpost_z), (sm_x, 0, sm_z), c_saddle, 5)
        self.draw_line((saddle_rear_x, 0, sm_z), (saddle_front_x, 0, sm_z), c_saddle, 12)

        self.draw_line((htt_x, 0, htt_z), (steerer_top_x, 0, steerer_top_z), c_spacers, 10)
        self.draw_line((steerer_top_x, 0, steerer_top_z), (bar_x, 0, bar_z), c_stem, 8)

        b_drop_val = 125
        self.draw_line((bar_x, -hw, bar_z), (bar_x, hw, bar_z), c_bar, 8)

        # Riser-Lenker Konstruktion in 3D
        right_drop = np.array([
            [bar_x, hw, bar_z],               
            [bar_x, hw, hoods_z],        
            [hoods_x, hw, hoods_z],           
            [hoods_x, hw, hoods_z - b_drop_val], 
            [bar_x, hw, hoods_z - b_drop_val] 
        ], dtype=np.float32)
        
        left_drop = np.array([
            [bar_x, -hw, bar_z],
            [bar_x, -hw, hoods_z],
            [hoods_x, -hw, hoods_z],
            [hoods_x, -hw, hoods_z - b_drop_val],
            [bar_x, -hw, hoods_z - b_drop_val]
        ], dtype=np.float32)
        
        self.draw_curve(right_drop, c_bar, 6)
        self.draw_curve(left_drop, c_bar, 6)

        c_point = (1.0, 0.0, 0.0, 1.0)
        # Reduzierte Knotenpunkte für das Fitting-Modell
        nodes = [
            (bb_x, 0, bb_z),
            (sm_x, 0, sm_z),
            (bar_x, 0, bar_z),
            (hoods_x, hw, hoods_z),
            (hoods_x, -hw, hoods_z),
            (steerer_top_x, 0, steerer_top_z),
            (htt_x, 0, htt_z),
            (seatpost_x, 0, seatpost_z),
        ]
        self.draw_points(nodes, c_point, size=14)

        if self.show_dims_cb.isChecked():
            c_fit = (0.6, 0.2, 0.8, 1.0)
            c_ftext = (153, 51, 204, 255)

            ht_off = 150
            ox = -ht_off * math.sin(sa_rad)
            oz = ht_off * math.cos(sa_rad)
            self.draw_line((ox, 0, oz), (seatpost_x + ox, 0, seatpost_z + oz), c_fit, 2)
            self.draw_line((0, 0, 0), (ox, 0, oz), c_fit, 1)
            self.draw_line((seatpost_x, 0, seatpost_z), (seatpost_x + ox, 0, seatpost_z + oz), c_fit, 1)
            self.draw_3d_text([seatpost_x/2 + ox - 40, 0, seatpost_z/2 + oz], f"Ht: {int(v['saddle_height'])}", c_ftext)

            setback_z = sm_z + 150
            self.draw_line((0, 0, setback_z), (sm_x, 0, setback_z), c_fit, 2)
            self.draw_line((0, 0, 0), (0, 0, setback_z), c_fit, 1)
            self.draw_line((sm_x, 0, sm_z), (sm_x, 0, setback_z), c_fit, 1)
            self.draw_3d_text([sm_x/2 - 30, 0, setback_z + 10], f"Offset: {int(v['saddle_setback'])}", c_ftext)

            self.draw_line((sm_x, 0, sm_z), (hoods_x, hw, hoods_z), c_fit, 2)
            self.draw_line((sm_x, 0, sm_z), (hoods_x, -hw, hoods_z), c_fit, 2)
            mid_x = (sm_x + hoods_x) / 2
            mid_y = hw / 2
            mid_z = (sm_z + hoods_z) / 2
            self.draw_3d_text([mid_x - 30, mid_y, mid_z + 30], f"3D Reach: {int(reach_3d)}", c_ftext)

            drop_x = bar_x + 180
            self.draw_line((drop_x, 0, sm_z), (drop_x, 0, hoods_z), c_fit, 2)
            self.draw_line((sm_x, 0, sm_z), (drop_x, 0, sm_z), c_fit, 1)
            self.draw_line((hoods_x, hw, hoods_z), (drop_x, 0, hoods_z), c_fit, 1)
            self.draw_3d_text([drop_x + 10, 0, (sm_z + hoods_z)/2], f"Drop: {int(saddle_drop)}", c_ftext)

        if self.show_frame_cb.isChecked():
            c_geo = (0.1, 0.5, 0.8, 1.0)
            c_gtext = (25, 128, 204, 255)

            stack_x = -250
            self.draw_line((stack_x, 0, 0), (stack_x, 0, htt_z), c_geo, 2)
            self.draw_line((0, 0, 0), (stack_x, 0, 0), c_geo, 1)
            self.draw_line((htt_x, 0, htt_z), (stack_x, 0, htt_z), c_geo, 1)
            self.draw_3d_text([stack_x - 70, 0, htt_z/2], f"Stack: {int(htt_z)}", c_gtext)

            geo_reach_z = htt_z + 200
            self.draw_line((0, 0, geo_reach_z), (htt_x, 0, geo_reach_z), c_geo, 2)
            self.draw_line((0, 0, htt_z), (0, 0, geo_reach_z), c_geo, 1)
            self.draw_line((htt_x, 0, htt_z), (htt_x, 0, geo_reach_z), c_geo, 1)
            self.draw_3d_text([htt_x/2 - 30, 0, geo_reach_z + 10], f"Reach: {int(htt_x)}", c_gtext)

            ett_z = htt_z + 80
            self.draw_line((st_virtual_x, 0, ett_z), (htt_x, 0, ett_z), c_geo, 2)
            self.draw_line((st_virtual_x, 0, htt_z), (st_virtual_x, 0, ett_z), c_geo, 1)
            self.draw_line((htt_x, 0, htt_z), (htt_x, 0, ett_z), c_geo, 1)
            self.draw_3d_text([(htt_x + st_virtual_x)/2 - 30, 0, ett_z + 10], f"ETT: {int(eff_top_tube_len)}", c_gtext)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BikeCAD()
    window.show()
    sys.exit(app.exec())