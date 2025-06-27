import sys

import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem, QTextEdit, QLineEdit, QLabel, QPushButton, QListWidget, QListWidgetItem, QMessageBox)
from PyQt5.QtGui import QFont, QIcon, QColor, QIntValidator
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, pyqtSlot, QUrl
from PyQt5.QtGui import QFont, QIcon, QColor
from PyQt5.QtWebSockets import QWebSocket
from PyQt5.QtNetwork import QAbstractSocket, QTcpSocket, QHostAddress

class ChargeDischargeController:
    def __init__(self):
        self.charging = False
        self.discharging = False
        self.soc_limit = 80
        self.min_soc_limit = 20

    def monitor_charge_discharge(self, current_soc, charge_time, discharge_time, max_soc, min_soc):
        self.soc_limit = max_soc
        self.min_soc_limit = min_soc
        # 这里实现充放电控制逻辑
        return {
            'status': 'idle',
            'message': f'Monitoring: SOC={current_soc}%, Max={max_soc}%, Min={min_soc}%'
        }

class WebSocketWorker(QThread):
    message_received = pyqtSignal(dict)
    connection_status = pyqtSignal(bool, str)
    log_message = pyqtSignal(str)

    def __init__(self, url):
        super().__init__()
        self.url = QUrl(url)
        self.websocket = QWebSocket()
        self.connected = False
        self.running = True
        self.latest_rtv_data = {}

        self.websocket.connected.connect(self.on_connected)
        self.websocket.disconnected.connect(self.on_disconnected)
        self.websocket.textMessageReceived.connect(self.on_text_message_received)
        self.websocket.error.connect(self.on_error)

    def run(self):
        self.websocket.open(self.url)
        self.exec_()

    def stop(self):
        self.running = False
        self.websocket.close()
        self.quit()
        self.wait()

    @pyqtSlot()
    def on_connected(self):
        self.connected = True
        self.connection_status.emit(True, 'Connected to server')
        self.log_message.emit('WebSocket connected successfully')
        # 发送订阅消息
        self.send_subscription()

    @pyqtSlot()
    def on_disconnected(self):
        self.connected = False
        self.connection_status.emit(False, 'Disconnected from server')
        self.log_message.emit('WebSocket disconnected')
        if self.running:
            self.log_message.emit('Attempting to reconnect...')
            QTimer.singleShot(5000, lambda: self.websocket.open(self.url))

    @pyqtSlot(str)
    def on_text_message_received(self, message):
        try:
            data = json.loads(message)
            self.message_received.emit(data)
            if 'rtv_data' in data:
                self.latest_rtv_data = data['rtv_data']
        except json.JSONDecodeError:
            self.log_message.emit(f'Invalid JSON message: {message}')

    @pyqtSlot('QAbstractSocket::SocketError')
    def on_error(self, error):
        error_str = f'WebSocket error: {self.websocket.errorString()}'
        self.connection_status.emit(False, error_str)
        self.log_message.emit(error_str)

    def send_subscription(self):
        if self.connected:
            menu_sub = json.dumps({'type': 'menu', 'action': 'subscribe'})
            rtv_sub = json.dumps({'type': 'rtv', 'action': 'subscribe'})
            self.websocket.sendTextMessage(menu_sub)
            self.websocket.sendTextMessage(rtv_sub)
            self.log_message.emit('Sent subscription requests')

    def send_command(self, command):
        if self.connected:
            cmd_msg = json.dumps({'type': 'cmd', 'data': command})
            self.websocket.sendTextMessage(cmd_msg)
            self.log_message.emit(f'Sent command: {command}')

class WebSocketClient(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('EMS Monitor Client (Android Compatible)')
        self.setGeometry(100, 100, 1024, 768)
        self.controller = ChargeDischargeController()
        self.worker = None
        self.latest_rtv_data = {}
        self.init_ui()
        self.init_timer()

    def init_ui(self):
        # 设置中文字体
        font = QFont()
        font.setFamily('SimHei')
        self.setFont(font)

        # 主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 顶部URL输入区域
        url_layout = QHBoxLayout()
        url_label = QLabel('服务器地址:')
        self.url_input = QLineEdit('ws://ems.hy-power.net:8888/E6F7D5412A20?bfca76a4d58bf72a081151f64a910b2637a2f1d980958edc2818cedf62d6a940968b2c415f28458e5c131a06d17049aad10dde5dd6726f7e12847f565fc8c1e221cb8c4bc8924157b019ebd8e99d0761')
        self.url_input.setPlaceholderText('输入WebSocket服务器URL')
        self.connect_btn = QPushButton('连接')
        self.disconnect_btn = QPushButton('断开')
        self.refresh_btn = QPushButton('刷新数据')

        self.disconnect_btn.setEnabled(False)

        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        url_layout.addWidget(self.connect_btn)
        url_layout.addWidget(self.disconnect_btn)
        url_layout.addWidget(self.refresh_btn)

        # 中间内容区域
        content_layout = QHBoxLayout()

        # 左侧设备树
        self.device_tree = QTreeWidget()
        self.device_tree.setHeaderLabel('设备列表')
        self.device_tree.setMinimumWidth(250)
        content_layout.addWidget(self.device_tree)

        # 右侧数据显示
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # 充放电控制区域
        control_layout = QHBoxLayout()

        # 充电时间
        charge_time_layout = QVBoxLayout()
        charge_time_label = QLabel('充电时间 (分钟):')
        self.charge_time_input = QLineEdit()
        self.charge_time_input.setValidator(QIntValidator(0, 1440))
        self.charge_time_input.setPlaceholderText('0-1440')
        charge_time_layout.addWidget(charge_time_label)
        charge_time_layout.addWidget(self.charge_time_input)

        # 放电时间
        discharge_time_layout = QVBoxLayout()
        discharge_time_label = QLabel('放电时间 (分钟):')
        self.discharge_time_input = QLineEdit()
        self.discharge_time_input.setValidator(QIntValidator(0, 1440))
        self.discharge_time_input.setPlaceholderText('0-1440')
        discharge_time_layout.addWidget(discharge_time_label)
        discharge_time_layout.addWidget(self.discharge_time_input)

        # SOC上限
        max_soc_layout = QVBoxLayout()
        max_soc_label = QLabel('SOC上限 (%):')
        self.max_soc_input = QLineEdit('80')
        self.max_soc_input.setValidator(QIntValidator(50, 100))
        max_soc_layout.addWidget(max_soc_label)
        max_soc_layout.addWidget(self.max_soc_input)

        # SOC下限
        min_soc_layout = QVBoxLayout()
        min_soc_label = QLabel('SOC下限 (%):')
        self.min_soc_input = QLineEdit('20')
        self.min_soc_input.setValidator(QIntValidator(0, 50))
        min_soc_layout.addWidget(min_soc_label)
        min_soc_layout.addWidget(self.min_soc_input)

        control_layout.addLayout(charge_time_layout)
        control_layout.addLayout(discharge_time_layout)
        control_layout.addLayout(max_soc_layout)
        control_layout.addLayout(min_soc_layout)

        # 数据显示列表
        data_list_label = QLabel('实时数据:')
        self.data_list = QListWidget()
        self.data_list.setFont(QFont('Courier New', 10))

        # 日志区域
        log_label = QLabel('系统日志:')
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setMaximumHeight(150)

        right_layout.addLayout(control_layout)
        right_layout.addWidget(data_list_label)
        right_layout.addWidget(self.data_list)
        right_layout.addWidget(log_label)
        right_layout.addWidget(self.log_display)

        content_layout.addWidget(right_panel, 2)

        # 添加所有布局到主布局
        main_layout.addLayout(url_layout)
        main_layout.addLayout(content_layout, 1)

        # 连接信号槽
        self.connect_btn.clicked.connect(self.start_websocket)
        self.disconnect_btn.clicked.connect(self.stop_websocket)
        self.refresh_btn.clicked.connect(self.refresh_data)
        self.device_tree.itemClicked.connect(self.on_tree_item_clicked)

        # 初始化设备树
        self.init_device_tree()

    def init_device_tree(self):
        # 添加示例设备节点
        root_items = [
            ('BMS', ['BMS1', 'BMS2', 'BMS3']),
            ('PCS', ['PCS1', 'PCS2']),
            ('Grid', ['Grid1']),
            ('Air Condition', ['AC1', 'AC2'])
        ]

        for root_name, children in root_items:
            root = QTreeWidgetItem([root_name])
            for child_name in children:
                child = QTreeWidgetItem([child_name])
                root.addChild(child)
            self.device_tree.addTopLevelItem(root)
            root.setExpanded(True)

    def init_timer(self):
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(1000)

    def start_websocket(self):
        if not self.validate_inputs():
            return

        url = self.url_input.text().strip()
        if not url.startswith('ws://') and not url.startswith('wss://'):
            url = 'ws://' + url

        self.worker = WebSocketWorker(url)
        self.worker.message_received.connect(self.handle_message)
        self.worker.connection_status.connect(self.update_connection_status)
        self.worker.log_message.connect(self.add_log)
        self.worker.start()

        self.connect_btn.setEnabled(False)
        self.disconnect_btn.setEnabled(True)
        self.add_log(f'Connecting to {url}...')

    def stop_websocket(self):
        if self.worker:
            self.worker.stop()
            self.worker = None
            self.connect_btn.setEnabled(True)
            self.disconnect_btn.setEnabled(False)
            self.add_log('Disconnected from server')

    def refresh_data(self):
        self.add_log('Refreshing data...')
        self.data_list.clear()
        if self.worker and self.worker.connected:
            self.worker.send_subscription()
        else:
            self.start_websocket()

    def handle_message(self, message):
        if 'menu' in message:
            self.update_device_tree(message['menu'])
        elif 'rtv_data' in message:
            self.latest_rtv_data = message['rtv_data']
            self.update_data_display()

    def update_device_tree(self, menu_data):
        # 这里实现从服务器菜单数据更新设备树的逻辑
        pass

    def update_data_display(self):
        selected_item = self.device_tree.currentItem()
        if selected_item:
            self.update_data_list_by_ids(self.get_rtv_ids_for_item(selected_item))

    def on_tree_item_clicked(self, item, column):
        self.update_data_list_by_ids(self.get_rtv_ids_for_item(item))

    def get_item_level(self, item):
        level = 0
        while item.parent():
            item = item.parent()
            level += 1
        return level

    def get_rtv_ids_for_item(self, item):
        # 根据选择的设备项返回相应的RTV IDs
        item_text = item.text(0)
        parent_text = item.parent().text(0) if item.parent() else ''

        # 这里应该根据实际的RTV ID映射关系返回
        return [f'{parent_text}_{item_text}_temp', f'{parent_text}_{item_text}_voltage']

    def update_data_list_by_ids(self, rtv_ids):
        self.data_list.clear()
        if not rtv_ids or not self.latest_rtv_data:
            return

        for rtv_id in rtv_ids:
            if rtv_id in self.latest_rtv_data:
                value = self.latest_rtv_data[rtv_id]
                item = QListWidgetItem(f'{rtv_id}: {value}')
                # 设置不同类型数据的颜色
                if 'temp' in rtv_id.lower():
                    temp = float(value.split()[0])
                    if temp > 50:
                        item.setBackground(QColor(255, 100, 100))
                    elif temp > 35:
                        item.setBackground(QColor(255, 200, 100))
                self.data_list.addItem(item)

    def update_connection_status(self, connected, message):
        status = 'Connected' if connected else 'Disconnected'
        self.statusBar().showMessage(f'Status: {status} - {message}')
        self.connect_btn.setEnabled(not connected)
        self.disconnect_btn.setEnabled(connected)

    def add_log(self, message):
        self.log_display.append(message)
        # 滚动到底部
        self.log_display.moveCursor(self.log_display.textCursor().End)

    def update_display(self):
        if not self.worker or not self.worker.connected:
            return

        # 获取当前SOC值（这里使用模拟数据）
        current_soc = float(self.latest_rtv_data.get('BMS_BMS1_SOC', '50').split()[0])

        # 获取输入值
        charge_time = int(self.charge_time_input.text()) if self.charge_time_input.text() else 0
        discharge_time = int(self.discharge_time_input.text()) if self.discharge_time_input.text() else 0
        max_soc = int(self.max_soc_input.text()) if self.max_soc_input.text() else 80
        min_soc = int(self.min_soc_input.text()) if self.min_soc_input.text() else 20

        # 调用充放电控制逻辑
        result = self.controller.monitor_charge_discharge(current_soc, charge_time, discharge_time, max_soc, min_soc)
        self.add_log(result['message'])

    def validate_inputs(self):
        # 验证URL输入
        if not self.url_input.text().strip():
            QMessageBox.warning(self, '输入错误', '请输入服务器URL')
            return False

        # 验证数值输入
        try:
            if self.charge_time_input.text() and int(self.charge_time_input.text()) < 0:
                QMessageBox.warning(self, '输入错误', '充电时间不能为负数')
                return False
            if self.discharge_time_input.text() and int(self.discharge_time_input.text()) < 0:
                QMessageBox.warning(self, '输入错误', '放电时间不能为负数')
                return False
            if self.max_soc_input.text():
                max_soc = int(self.max_soc_input.text())
                if max_soc < 50 or max_soc > 100:
                    QMessageBox.warning(self, '输入错误', 'SOC上限必须在50-100之间')
                    return False
            if self.min_soc_input.text():
                min_soc = int(self.min_soc_input.text())
                if min_soc < 0 or min_soc > 50:
                    QMessageBox.warning(self, '输入错误', 'SOC下限必须在0-50之间')
                    return False
            return True
        except ValueError:
            QMessageBox.warning(self, '输入错误', '请输入有效的数字')
            return False

    def closeEvent(self, event):
        self.stop_websocket()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 设置全局字体以支持中文
    font = QFont('SimHei')
    app.setFont(font)
    window = WebSocketClient()
    window.show()
    sys.exit(app.exec_())