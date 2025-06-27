from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTextEdit, QTreeWidget, QTreeWidgetItem, QListWidget, QListWidgetItem, QHeaderView, QGraphicsDropShadowEffect, QLineEdit, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QIcon, QFont, QIntValidator
from data_processor import DataProcessor
from connection_manager import WebSocketWorker
import sys
import json
from datetime import datetime

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.data_processor = DataProcessor()
        self.ws_worker = None
        self.initUI()
        self.setup_signals()
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(3000)

    def initUI(self):
        self.setWindowTitle('BY-EMS Monitoring System V1.0')
        self.setGeometry(100, 100, 1600, 900)
        self.setStyleSheet("QMainWindow { border: none; background-color: white; }")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Left panel setup
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(5, 2, 5, 5)
        left_panel.setMaximumWidth(700)
        left_panel.setStyleSheet("QWidget { background-color: white; border-radius: 5px;}")

        # Device tree
        self.device_tree = QTreeWidget(self)
        self.device_tree.setHeaderLabels(['设备列表'])
        self.device_tree.setStyleSheet("QTreeWidget { background-color: white; font-size: 12px; border: none; color: black;}")
        left_layout.addWidget(self.device_tree)

        # Monitoring settings panel
        self.setup_monitoring_panel(left_layout)

        # Log display
        self.log_text = QTextEdit(self)
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(int(self.height() * 0.5))
        self.log_text.setStyleSheet("QTextEdit { background-color: #f8f8f8; font-size: 12px; color: black; border: 1px solid #e0e0e0; border-radius: 3px;}")
        left_layout.addWidget(self.log_text)

        # Control buttons
        self.setup_buttons(left_layout)

        # Right panel - data display
        self.data_list = QListWidget(self)
        self.data_list.setStyleSheet("QListWidget { font-size: 12px; border: 1px solid #cccccc; background-color: white; color: black; border-radius: 3px; padding: 5px;}")

        main_layout.addWidget(left_panel)
        main_layout.addWidget(self.data_list)

    def setup_monitoring_panel(self, parent_layout):
        # Implementation of monitoring settings panel
        monitoring_settings_panel = QWidget()
        monitoring_settings_layout = QVBoxLayout(monitoring_settings_panel)
        monitoring_settings_layout.setContentsMargins(10, 10, 10, 10)
        monitoring_settings_panel.setStyleSheet("QWidget { background-color: white; padding: 10px; border: 1px solid #cccccc;}")

        # Token input
        token_label = QLabel('WebSocket Token:')
        token_widget = QWidget()
        token_layout = QHBoxLayout(token_widget)
        self.token_input = QLineEdit()
        self.token_input.setFixedWidth(450)
        self.token_input.setText("e167f6f558238169710ac8b9d5650b61d481490772716cd194692bfcda4d6128ff00f4c65ebf2d2e1ef708549e524d6235ad9c9d10924d778036649652059b867271c4ceb0bb0b063db5ce953c41be1d")
        token_layout.addWidget(token_label)
        token_layout.addWidget(self.token_input)
        monitoring_settings_layout.addWidget(token_widget)

        # Charging time setting
        charge_layout = QHBoxLayout()
        charge_label = QLabel('充电时间 (分钟):')
        self.charge_time_input = QLineEdit()
        self.charge_time_input.setValidator(QIntValidator(0, 1440))
        self.charge_time_input.setText('60')
        charge_layout.addWidget(charge_label)
        charge_layout.addWidget(self.charge_time_input)
        monitoring_settings_layout.addLayout(charge_layout)

        # Discharging time setting
        discharge_layout = QHBoxLayout()
        discharge_label = QLabel('放电时间 (分钟):')
        self.discharge_time_input = QLineEdit()
        self.discharge_time_input.setValidator(QIntValidator(0, 1440))
        self.discharge_time_input.setText('30')
        discharge_layout.addWidget(discharge_label)
        discharge_layout.addWidget(self.discharge_time_input)
        monitoring_settings_layout.addLayout(discharge_layout)

        # SOC limit setting
        soc_layout = QHBoxLayout()
        soc_label = QLabel('SOC限制 (%):')
        self.soc_limit_input = QLineEdit()
        self.soc_limit_input.setValidator(QIntValidator(0, 100))
        self.soc_limit_input.setText('80')
        soc_layout.addWidget(soc_label)
        soc_layout.addWidget(self.soc_limit_input)
        monitoring_settings_layout.addLayout(soc_layout)

        # Apply button for settings
        apply_btn = QPushButton('应用设置')
        apply_btn.setStyleSheet("background-color: #FFC107; color: black; border-radius: 3px; padding: 5px;")
        monitoring_settings_layout.addWidget(apply_btn)

        parent_layout.addWidget(monitoring_settings_panel)

    def setup_buttons(self, parent_layout):
        button_layout = QHBoxLayout()
        self.connect_btn = QPushButton('连接WebSocket')
        self.disconnect_btn = QPushButton('断开连接')
        self.refresh_btn = QPushButton('刷新数据')

        self.connect_btn.clicked.connect(self.start_websocket)
        self.disconnect_btn.clicked.connect(self.stop_websocket)
        self.refresh_btn.clicked.connect(self.refresh_data)

        self.disconnect_btn.setEnabled(False)
        self.refresh_btn.setEnabled(False)

        # Button styles
        # Enhanced button styles with hover effects
        self.connect_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; border-radius: 3px; padding: 6px 12px; font-size: 12px; border: none; } QPushButton:hover { background-color: #45a049; }")
        self.disconnect_btn.setStyleSheet("QPushButton { background-color: #f44336; color: white; border-radius: 3px; padding: 6px 12px; font-size: 12px; border: none; } QPushButton:hover { background-color: #d32f2f; }")
        self.refresh_btn.setStyleSheet("QPushButton { background-color: #2196F3; color: white; border-radius: 3px; padding: 6px 12px; font-size: 12px; border: none; } QPushButton:hover { background-color: #1976D2; }")

        button_layout.addWidget(self.connect_btn)
        button_layout.addWidget(self.disconnect_btn)
        button_layout.addWidget(self.refresh_btn)
        parent_layout.addLayout(button_layout)

    def setup_signals(self):
        self.device_tree.itemClicked.connect(self.on_tree_item_clicked)

    def log(self, message):
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.log_text.append(f"{current_time} - {message}")

    def start_websocket(self):
        try:
            self.connect_btn.setEnabled(False)
            self.disconnect_btn.setEnabled(True)
            self.refresh_btn.setEnabled(True)
            self.log("正在连接WebSocket...")

            token = self.token_input.text()
            self.ws_worker = WebSocketWorker(token)
            self.ws_worker.message_signal.connect(self.handle_message)
            self.ws_worker.log_signal.connect(self.log)
            self.ws_worker.start()
            # 启动定时刷新
            self.update_timer = QTimer()
            self.update_timer.timeout.connect(self.refresh_data)
            self.update_timer.start(1000)
            # 连接成功后自动刷新数据
            QTimer.singleShot(1000, self.refresh_data)
        except Exception as e:
            self.log(f"启动WebSocket连接失败: {str(e)}")
            self.connect_btn.setEnabled(True)
    def stop_websocket(self):
        if self.ws_worker:
            self.ws_worker.stop()
            self.ws_worker = None
        self.connect_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(False)
        self.refresh_btn.setEnabled(False)
        self.log("WebSocket连接已断开")

    def handle_message(self, data):
        func_type = data.get('func')
        if func_type == 'menu':
            self.data_processor.process_menu_data(data.get('data', {}))
            self.update_device_tree()
        elif func_type == 'rtv':
            self.data_processor.process_rtv_data(data.get('data', []))
            # 数据更新后刷新显示
            self.refresh_data()
            current_item = self.device_tree.currentItem()
            if current_item:
                self.update_data_list(current_item)

    def update_device_tree(self):
        self.device_tree.clear()
        menu_data = self.data_processor.get_menu_data()
        for device_type, devices in menu_data.items():
            type_item = QTreeWidgetItem([device_type])
            self.device_tree.addTopLevelItem(type_item)
            for device in devices:
                device_item = QTreeWidgetItem([f"{device['id']} - {device.get('chnName')}"])
                type_item.addChild(device_item)
                for rtv_item in device.get('rtvList', []):
                    rtv_node = QTreeWidgetItem([f"{rtv_item['id']} - {rtv_item.get('fieldChnName')}"])
                    device_item.addChild(rtv_node)
            type_item.setExpanded(True)
        # 自动选择第一个顶级项目
        if self.device_tree.topLevelItemCount() > 0:
            self.device_tree.setCurrentItem(self.device_tree.topLevelItem(0))

    def on_tree_item_clicked(self, item, column):
        self.update_data_list(item)

    def update_data_list(self, item):
        self.data_list.clear()
        item_level = self.get_item_level(item)
        rtv_ids = self.get_rtv_ids_for_item(item, item_level)
        self.update_data_list_by_ids(rtv_ids)

    def get_item_level(self, item):
        level = 0
        current = item
        while current.parent():
            level += 1
            current = current.parent()
        return level

    def get_rtv_ids_for_item(self, item, level):
        if level == 2:  # RTV item
            return [item.text(0).split(' - ')[0]]
        elif level == 1:  # Device item
            rtv_ids = []
            for i in range(item.childCount()):
                rtv_ids.append(item.child(i).text(0).split(' - ')[0])
            return rtv_ids
        elif level == 0:  # Group item
            rtv_ids = []
            for i in range(item.childCount()):
                device_item = item.child(i)
                for j in range(device_item.childCount()):
                    rtv_ids.append(device_item.child(j).text(0).split(' - ')[0])
            return rtv_ids
        return []

    def update_data_list_by_ids(self, rtv_ids):
        try:
            self.data_list.clear()
            
            # 按设备类型对数据进行分组
            grouped_data = {
                "d_bms": [],
                "d_pcs": [],
                "d_grid": [],
                "d_air_condition": []
            }

            # 将数据分组
            for rtv_id in rtv_ids:
                str_id = str(rtv_id)
                rtv_data = self.data_processor.get_latest_value(rtv_id)
                
                if isinstance(rtv_data, dict):
                    processed_data = rtv_data
                elif isinstance(rtv_data, str):
                    try:
                        processed_data = json.loads(rtv_data)
                        if not isinstance(processed_data, dict):
                            self.log(f"RTV ID {rtv_id} data is not a JSON object")
                            continue
                    except json.JSONDecodeError:
                        self.log(f"RTV ID {rtv_id} data is not valid JSON: {rtv_data[:50]}")
                        continue
                else:
                    self.log(f"Invalid data format for RTV ID {rtv_id}: {type(rtv_data)}")
                    continue

                device_type = processed_data.get('device_type', 'unknown')
                if device_type in grouped_data:
                    grouped_data[device_type].append((str_id, processed_data))

            # 设备类型颜色映射
            color_map = {
                "d_bms": QColor(230, 230, 255),           # 浅蓝色 - BMS电池
                "d_pcs": QColor(255, 230, 230),           # 浅红色 - PCS
                "d_grid": QColor(255, 255, 230),          # 浅黄色 - 电网
                "d_air_condition": QColor(230, 255, 230)  # 浅绿色 - 空调
            }

            # 添加数据到列表
            for device_type, items in grouped_data.items():
                if items:
                    # 添加设备类型标题
                    title_item = QListWidgetItem(f"*{device_type}*")
                    title_item.setBackground(color_map[device_type])
                    self.data_list.addItem(title_item)

                    # 添加该类型的所有数据项
                    for str_id, processed_data in items:
                        name = processed_data.get('name', 'Unknown')
                        value = processed_data.get('value', 'N/A')
                        unit = processed_data.get('unit', '')
                        display_text = f"ID: {str_id:<12}  {name:<30}  {value:<10} {unit}"
                        
                        list_item = QListWidgetItem(display_text)
                        # 设置等宽字体以便对齐
                        font = QFont("Courier New")
                        list_item.setFont(font)
                        # 设置背景色
                        list_item.setBackground(color_map[device_type])
                        self.data_list.addItem(list_item)

        except Exception as e:
            self.log(f"Error updating data list: {str(e)}")

    def refresh_data(self):
        self.log("手动刷新数据...")
        if self.ws_worker:
            self.ws_worker.request_refresh()

    def update_display(self):
        # 定期刷新当前选中项的数据
        current_item = self.device_tree.currentItem()
        if current_item:
            self.update_data_list(current_item)

    def closeEvent(self, event):
        self.stop_websocket()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())