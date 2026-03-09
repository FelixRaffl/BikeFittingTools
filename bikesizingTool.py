import sys
import math
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                             QVBoxLayout, QFormLayout, QDoubleSpinBox, QLabel, 
                             QCheckBox, QSplitter, QScrollArea)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import pyqtgraph.opengl as gl

class BikeCAD(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pro Bike CAD - GPU Accelerated")
        self.resize(1400, 900)

        # --- Main Layout ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.splitter)

        # --- Left UI Panel (Now wrapped in a Scroll Area) ---
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMinimumWidth(360) # Locked minimum width for the scroll area
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background-color: #f0f0f0; }")
        
        left_panel = QWidget()
        left_panel.setStyleSheet("background-color: #f0f0f0; padding: 10px;")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(10) 
        
        self.scroll_area.setWidget(left_panel)
        self.splitter.addWidget(self.scroll_area)

        # --- Right 3D View (OpenGL) ---
        self.view = gl.GLViewWidget()
        self.view.setBackgroundColor('w') 
        self.view.setCameraPosition(distance=2200, elevation=10, azimuth=-90)
        
        self.splitter.addWidget(self.view)

        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 3)
        self.splitter.setSizes([360, 1040])

        self.plot_items = []

        # --- Build UI Forms ---
        self.inputs = {}
        
        # 1. Rider Fit Data
        self.add_header(left_layout, "RIDER FIT DATA", "#333333")
        fit_form = QFormLayout()
        fit_form.setVerticalSpacing(15) 
        self.add_spinbox(fit_form, 'saddle_height', 'Saddle Ht', 733.0, 500, 1000, 1)
        self.add_spinbox(fit_form, 'saddle_setback', 'Saddle Offset', 0.0, -100, 100, 1) 
        self.add_spinbox(fit_form, 'saddle_reach', 'Saddle Reach', 660.0, 400, 900, 1)
        self.add_spinbox(fit_form, 'saddle_drop', 'Saddle Drop', 96.0, -100, 300, 1)
        left_layout.addLayout(fit_form)

        left_layout.addSpacing(10) 

        # 2. Components / Geo
        self.add_header(left_layout, "COMPONENTS / GEO", "#333333")
        comp_form = QFormLayout()
        comp_form.setVerticalSpacing(12) 
        self.add_spinbox(comp_form, 'stem_length', 'Stem Length', 90.0, 30, 150, 1)
        self.add_spinbox(comp_form, 'stem_angle', 'Stem Angle', -6.0, -30, 40, 1)
        self.add_spinbox(comp_form, 'bar_reach', 'Bar Reach', 80.0, 50, 120, 1)
        self.add_spinbox(comp_form, 'bar_width', 'Bar Width', 400.0, 320, 500, 10)
        self.add_spinbox(comp_form, 'topcap_height', 'Topcap Ht', 15.0, 0, 50, 1)
        self.add_spinbox(comp_form, 'spacer_height', 'Spacer Ht', 40.0, 0, 100, 5)
        self.add_spinbox(comp_form, 'front_angle', 'Front Angle', 72.0, 65, 80, 0.5)
        self.add_spinbox(comp_form, 'seat_angle', 'Seat Angle', 73.5, 65, 80, 0.5)
        left_layout.addLayout(comp_form)

        # 3. Output Toggles
        left_layout.addStretch() 
        self.add_header(left_layout, "VISIBILITY", "#333333")
        
        self.show_dims_cb = QCheckBox("Show Fit Dimensions")
        self.show_dims_cb.setChecked(True)
        self.show_dims_cb.setStyleSheet("QCheckBox { color: black; font-weight: bold; font-size: 14px; margin-bottom: 5px; } QCheckBox::indicator { width: 18px; height: 18px; }")
        self.show_dims_cb.stateChanged.connect(self.update_cad)
        left_layout.addWidget(self.show_dims_cb)

        self.show_frame_cb = QCheckBox("Show Frame Geo")
        self.show_frame_cb.setChecked(True)
        self.show_frame_cb.setStyleSheet("QCheckBox { color: black; font-weight: bold; font-size: 14px; margin-bottom: 10px; } QCheckBox::indicator { width: 18px; height: 18px; }")
        self.show_frame_cb.stateChanged.connect(self.update_cad)
        left_layout.addWidget(self.show_frame_cb)

        self.update_cad()

    # --- UI Helpers ---
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

    # --- 3D Drawing Helpers ---
    def draw_line(self, p1, p2, color, width=3):
        pos = np.array([p1, p2], dtype=np.float32)
        line = gl.GLLinePlotItem(pos=pos, color=color, width=width, antialias=True)
        self.view.addItem(line)
        self.plot_items.append(line)
        
    def draw_dashed_line(self, p1, p2, color, width=2):
        start = np.array(p1)
        end = np.array(p2)
        dist = np.linalg.norm(end - start)
        num_segments = max(int(dist / 20), 1)  
        
        for i in range(num_segments):
            if i % 2 == 0:  
                t1 = i / num_segments
                t2 = (i + 1) / num_segments
                s = start + t1 * (end - start)
                e = start + t2 * (end - start)
                self.draw_line(s, e, color, width)

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

    # --- Core CAD Math & Rendering ---
    def update_cad(self, *args):
        # 1. Clear old graphics
        for item in self.plot_items:
            self.view.removeItem(item)
        self.plot_items.clear()

        # 2. Pull values
        v = {k: spin.value() for k, spin in self.inputs.items()}

        # Constants
        fork_length = 370 
        wheel_radius = 340 
        saddle_length = 270
        bb_drop = 73 
        chainstay = 415

        sa_rad = math.radians(v['seat_angle'])
        ha_rad = math.radians(v['front_angle'])

        bb_x, bb_y, bb_z = 0, 0, 0
        rd_x, rd_y, rd_z = -chainstay, 0, bb_drop

        # Seatpost
        seatpost_x = -v['saddle_height'] * math.cos(sa_rad)
        seatpost_z = v['saddle_height'] * math.sin(sa_rad)

        # Saddle
        sm_x = seatpost_x - v['saddle_setback']
        sm_z = seatpost_z
        saddle_front_x = sm_x + (saddle_length / 2)
        saddle_rear_x = sm_x - (saddle_length / 2)

        # Bars
        bar_x = sm_x + v['saddle_reach']
        bar_z = sm_z - v['saddle_drop']

        # Stem & Headset
        stem_horiz_deg = (90 - v['front_angle']) + v['stem_angle']
        stem_rad = math.radians(stem_horiz_deg)

        steerer_top_x = bar_x - v['stem_length'] * math.cos(stem_rad)
        steerer_top_z = bar_z - v['stem_length'] * math.sin(stem_rad)
        
        total_spacers = v['spacer_height'] + v['topcap_height']
        htt_x = steerer_top_x + total_spacers * math.cos(ha_rad)
        htt_z = steerer_top_z - total_spacers * math.sin(ha_rad)
        
        # Frame Outputs
        st_virtual_x = -htt_z / math.tan(sa_rad)
        eff_top_tube_len = htt_x - st_virtual_x
        total_steer_axis = (htt_z - bb_drop) / math.sin(ha_rad)
        calc_head_tube = total_steer_axis - fork_length

        htb_x = htt_x + calc_head_tube * math.cos(ha_rad)
        htb_z = htt_z - calc_head_tube * math.sin(ha_rad)
        
        fd_x = htb_x + fork_length * math.cos(ha_rad)
        fd_z = bb_drop 

        # --- Draw Frame (Black, Thicker Lines) ---
        c_frame = (0.1, 0.1, 0.1, 1.0)
        self.draw_line((bb_x, 0, bb_z), (st_virtual_x, 0, htt_z), c_frame, 12) 
        self.draw_line((st_virtual_x, 0, htt_z), (htt_x, 0, htt_z), c_frame, 10) 
        self.draw_line((htt_x, 0, htt_z), (htb_x, 0, htb_z), c_frame, 14) 
        self.draw_line((htb_x, 0, htb_z), (bb_x, 0, bb_z), c_frame, 12) 
        self.draw_line((bb_x, 0, bb_z), (rd_x, 0, rd_z), c_frame, 8) 
        self.draw_line((htb_x, 0, htb_z), (fd_x, 0, fd_z), c_frame, 10) 

        # --- Draw Components (Thicker Lines) ---
        c_comp = (0.4, 0.4, 0.4, 1.0)
        self.draw_line((st_virtual_x, 0, htt_z), (seatpost_x, 0, seatpost_z), c_comp, 8) 
        self.draw_line((seatpost_x, 0, seatpost_z), (sm_x, 0, sm_z), c_frame, 5) 
        self.draw_line((saddle_rear_x, 0, sm_z), (saddle_front_x, 0, sm_z), c_frame, 12) 
        self.draw_line((htt_x, 0, htt_z), (steerer_top_x, 0, steerer_top_z), c_comp, 10) 
        self.draw_line((steerer_top_x, 0, steerer_top_z), (bar_x, 0, bar_z), c_frame, 8) 

        # Handlebars
        hw = v['bar_width'] / 2 
        b_reach = v['bar_reach']
        b_drop = 125 
        self.draw_line((bar_x, -hw, bar_z), (bar_x, hw, bar_z), c_frame, 8) 
        
        right_drop = np.array([[bar_x, hw, bar_z], [bar_x + b_reach, hw, bar_z], 
                               [bar_x + b_reach, hw, bar_z - b_drop], [bar_x + 20, hw, bar_z - b_drop]], dtype=np.float32)
        left_drop = np.array([[bar_x, -hw, bar_z], [bar_x + b_reach, -hw, bar_z], 
                              [bar_x + b_reach, -hw, bar_z - b_drop], [bar_x + 20, -hw, bar_z - b_drop]], dtype=np.float32)
        self.draw_curve(right_drop, c_frame, 6)
        self.draw_curve(left_drop, c_frame, 6)

        # --- Draw Nodes / Measurement Points (Solid Red Dots) ---
        c_point = (1.0, 0.0, 0.0, 1.0) 
        nodes = [
            (bb_x, 0, bb_z),         
            (sm_x, 0, sm_z),         
            (bar_x, 0, bar_z),       
            (steerer_top_x, 0, steerer_top_z), 
            (htt_x, 0, htt_z),       
            (htb_x, 0, htb_z),       
            (seatpost_x, 0, seatpost_z), 
            (rd_x, 0, rd_z),         
            (fd_x, 0, fd_z)          
        ]
        self.draw_points(nodes, c_point, size=14) 

        # --- Draw FIT Dimensions (Purple) ---
        if self.show_dims_cb.isChecked():
            c_fit = (0.6, 0.2, 0.8, 1.0) # Solid Purple
            color_fit_text = (153, 51, 204, 255)
            
            self.draw_dashed_line((0, 0, 0), (seatpost_x, 0, seatpost_z), c_fit, 2)  
            self.draw_dashed_line((seatpost_x, 0, sm_z), (sm_x, 0, sm_z), c_fit, 2)  
            self.draw_dashed_line((sm_x, 0, sm_z), (bar_x, 0, sm_z), c_fit, 2)       
            self.draw_dashed_line((bar_x, 0, sm_z), (bar_x, 0, bar_z), c_fit, 2)     
            
            self.draw_3d_text([seatpost_x/2 - 50, 0, seatpost_z/2 + 20], f"Ht: {int(v['saddle_height'])}", color_fit_text)
            self.draw_3d_text([(seatpost_x + sm_x)/2 - 20, 0, sm_z + 20], f"Offset: {int(v['saddle_setback'])}", color_fit_text)
            self.draw_3d_text([(sm_x + bar_x)/2 - 30, 0, sm_z + 15], f"Reach: {int(v['saddle_reach'])}", color_fit_text)
            self.draw_3d_text([bar_x + 15, 0, (sm_z + bar_z)/2], f"Drop: {int(v['saddle_drop'])}", color_fit_text)

        # --- Draw FRAME GEO Dimensions (Blue) ---
        if self.show_frame_cb.isChecked():
            c_geo = (0.1, 0.5, 0.8, 1.0) # Solid Blue
            color_geo_text = (25, 128, 204, 255)
            
            self.draw_dashed_line((0, 0, 0), (0, 0, htt_z), c_geo, 2)                      
            self.draw_dashed_line((0, 0, htt_z), (htt_x, 0, htt_z), c_geo, 2)              
            self.draw_dashed_line((htt_x, 0, htt_z), (st_virtual_x, 0, htt_z), c_geo, 2)   
            self.draw_dashed_line((htt_x, 0, htt_z), (htb_x, 0, htb_z), c_geo, 2)          
            
            self.draw_3d_text([-60, 0, htt_z/2], f"Stack: {int(htt_z)}", color_geo_text)
            self.draw_3d_text([htt_x/2 - 20, 0, htt_z + 15], f"Reach: {int(htt_x)}", color_geo_text)
            self.draw_3d_text([(htt_x + st_virtual_x)/2 - 30, 0, htt_z - 15], f"ETT: {int(eff_top_tube_len)}", color_geo_text)
            self.draw_3d_text([(htt_x + htb_x)/2 + 15, 0, (htt_z + htb_z)/2], f"HT: {int(calc_head_tube)}", color_geo_text)

        # --- Draw Wheels & Ground ---
        theta = np.linspace(0, 2 * np.pi, 60)
        wy = np.zeros(60)
        rw_pos = np.column_stack((rd_x + wheel_radius * np.cos(theta), wy, rd_z + wheel_radius * np.sin(theta))).astype(np.float32)
        fw_pos = np.column_stack((fd_x + wheel_radius * np.cos(theta), wy, fd_z + wheel_radius * np.sin(theta))).astype(np.float32)
        
        c_wheel = (0.7, 0.7, 0.7, 1.0)
        self.draw_curve(rw_pos, c_wheel, 2)
        self.draw_curve(fw_pos, c_wheel, 2)
        self.draw_line((-1000, 0, bb_drop - wheel_radius), (1000, 0, bb_drop - wheel_radius), (0.6, 0.4, 0.2, 1.0), 3)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BikeCAD()
    window.show()
    sys.exit(app.exec())