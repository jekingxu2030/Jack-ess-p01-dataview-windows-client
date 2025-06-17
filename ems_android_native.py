import sys
import json
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QTreeWidget, QTreeWidgetItem, QTextEdit, QLineEdit, QLabel, 
                            QPushButton, QListWidget, QListWidgetItem, QMessageBox, QProgressBar)
from PyQt5.QtGui import QFont, QColor, QIntValidator
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, pyqtSlot, QUrl
from PyQt5.QtWebSockets import QWebSocket
from PyQt5.QtNetwork import QAbstractSocket

# 充放电控制器
class ChargeDischargeController:
    def __init__(self):
        self.charging = False
        self.discharging = False
        self.soc_limit = 80
        self.min_soc_limit = 20

    def monitor_charge_discharge(self, current_soc, charge_time, discharge_time, max_soc, min_soc):
        self.soc_limit = max_soc
        self.min_soc_limit = min_soc
        # 充放电控制逻辑
        status = 'idle'
        message = f'监控中: SOC={current_soc}%, 上限={max_soc}%, 下限={min_soc}%'

        if current_soc >= max_soc and not self.discharging:
            self.charging = False
            self.discharging = True
            status = 'discharging'
            message = f'SOC达到上限 {max_soc}%, 开始放电'
        elif current_soc <= min_soc and not self.charging:
            self.discharging = False
            self.charging = True
            status = 'charging'
            message = f'SOC达到下限 {min_soc}%, 开始充电'
        elif charge_time > 0 and not self.charging:
            self.charging = True
            self.discharging = False
            status = 'charging'
            message = f'定时充电启动, 时长 {charge_time} 分钟'
        elif discharge_time > 0 and not self.discharging:
            self.discharging = True
            self.charging = False
            status = 'discharging'
            message = f'定时放电启动, 时长 {discharge_time} 分钟'

        return {'status': status, 'message': message}

# WebSocket工作线程
class WebSocketWorker(QThread):
    message_received = pyqtSignal(dict)
    connection_status = pyqtSignal(bool, str)
    log_message = pyqtSignal(str)
    connection_error = pyqtSignal(str)

    def __init__(self, url):
        super().__init__()
        self.url = QUrl(url)
        self.websocket = QWebSocket()
        self.connected = False
        self.running = True
        self.reconnect_interval = 5000  # 5秒重连间隔
        self.latest_rtv_data = {}

        # 连接信号槽
        self.websocket.connected.connect(self.on_connected)
        self.websocket.disconnected.connect(self.on_disconnected)
        self.websocket.textMessageReceived.connect(self.on_text_message_received)
        self.websocket.error.connect(self.on_error)

    def run(self):
        self.log_message.emit(f'尝试连接到服务器: {self.url.toString()}')
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
        self.connection_status.emit(True, '已连接到服务器')
        self.log_message.emit('WebSocket连接成功')
        self.send_subscription()

    @pyqtSlot()
    def on_disconnected(self):
        self.connected = False
        self.connection_status.emit(False, '与服务器断开连接')
        self.log_message.emit('WebSocket连接已断开')
        if self.running:
            self.log_message.emit(f'{self.reconnect_interval/1000}秒后尝试重连...')
            QTimer.singleShot(self.reconnect_interval, self.reconnect)

    def reconnect(self):
        if self.running and not self.connected:
            self.log_message.emit('尝试重连...')
            self.websocket.open(self.url)

    @pyqtSlot(str)
    def on_text_message_received(self, message):
        try:
            data = json.loads(message)
            self.message_received.emit(data)
            if 'rtv_data' in data:
                self.latest_rtv_data = data['rtv_data']
        except json.JSONDecodeError:
            self.log_message.emit(f'无效的JSON消息: {message}')

    @pyqtSlot(QAbstractSocket.SocketError)
    def on_error(self, error):
        error_str = f'WebSocket错误: {self.websocket.errorString()}'
        self.connection_status.emit(False, error_str)
        self.log_message.emit(error_str)
        self.connection_error.emit(error_str)

    def send_subscription(self):
        if self.connected:
            try:
                menu_sub = json.dumps({'type': 'menu', 'action': 'subscribe'})
                rtv_sub = json.dumps({'type': 'rtv', 'action': 'subscribe'})
                self.websocket.sendTextMessage(menu_sub)
                self.websocket.sendTextMessage(rtv_sub)
                self.log_message.emit('已发送订阅请求')
            except Exception as e:
                self.log_message.emit(f'发送订阅失败: {str(e)}')

    def send_command(self, command):
        if self.connected:
            try:
                cmd_msg = json.dumps({'type': 'cmd', 'data': command})
                self.websocket.sendTextMessage(cmd_msg)
                self.log_message.emit(f'已发送命令: {command}')
            except Exception as e:
                self.log_message.emit(f'发送命令失败: {str(e)}')

# 主应用窗口
class EMSMonitorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('EMS监控客户端')
        self.setGeometry(100, 100, 800, 600)
        self.controller = ChargeDischargeController()
        self.worker = None
        self.latest_rtv_data = {}
        self.init_ui()
        self.init_timer()
        self.init_websocket()

    def init_ui(self):
        # 设置中文字体
        font = QFont()
        font.setFamily('SimHei')
        self.setFont(font)

        # 主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 连接状态条
        status_layout = QHBoxLayout()
        self.status_label = QLabel('未连接')
        self.status_label.setStyleSheet('color: red; font-weight: bold;')
        self.connection_progress = QProgressBar()
        self.connection_progress.setMaximumWidth(100)
        self.connection_progress.setVisible(False)
        status_layout.addWidget(QLabel('连接状态:'))
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.connection_progress)
        status_layout.addStretch()

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

        # 控制按钮
        self.apply_btn = QPushButton('应用设置')
        self.apply_btn.clicked.connect(self.apply_settings)

        control_layout.addLayout(charge_time_layout)
        control_layout.addLayout(discharge_time_layout)
        control_layout.addLayout(max_soc_layout)
        control_layout.addLayout(min_soc_layout)
        control_layout.addWidget(self.apply_btn)

        # 中间内容区域
        content_layout = QHBoxLayout()

        # 左侧设备树
        self.device_tree = QTreeWidget()
        self.device_tree.setHeaderLabel('设备列表')
        self.device_tree.setMinimumWidth(200)
        content_layout.addWidget(self.device_tree)

        # 右侧数据显示
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # 数据显示列表
        data_list_label = QLabel('实时数据:')
        self.data_list = QListWidget()
        self.data_list.setFont(QFont('SimHei', 10))

        # 日志区域
        log_label = QLabel('系统日志:')
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)

        right_layout.addWidget(data_list_label)
        right_layout.addWidget(self.data_list)
        right_layout.addWidget(log_label)
        right_layout.addWidget(self.log_text)

        content_layout.addWidget(right_panel, 2)

        # 添加所有布局到主布局
        main_layout.addLayout(status_layout)
        main_layout.addLayout(control_layout)
        main_layout.addLayout(content_layout)

    def init_timer(self):
        # 数据刷新定时器
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.update_data_display)
        self.refresh_timer.start(1000)  # 每秒刷新一次

    def init_websocket(self):
        # 初始化WebSocket连接
        self.server_url = 'ws://ems.hy-power.net:8888/E6F7D5412A20?bfca76a4d58bf72a081151f64a910b2637a2f1d980958edc2818cedf62d6a940968b2c415f28458e5c131a06d17049aad10dde5dd6726f7e12847f565fc8c1e221cb8c4bc8924157b019ebd8e99d0761'
        self.start_websocket()

    def start_websocket(self):
        if self.worker is None or not self.worker.isRunning():
            self.worker = WebSocketWorker(self.server_url)
            self.worker.message_received.connect(self.process_message)
            self.worker.connection_status.connect(self.update_connection_status)
            self.worker.log_message.connect(self.add_log_message)
            self.worker.connection_error.connect(self.show_error_message)
            self.worker.start()
            self.connection_progress.setVisible(True)
            self.connection_progress.setRange(0, 0)  # 无限进度条

    def stop_websocket(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()

    def apply_settings(self):
        try:
            charge_time = int(self.charge_time_input.text()) if self.charge_time_input.text() else 0
            discharge_time = int(self.discharge_time_input.text()) if self.discharge_time_input.text() else 0
            max_soc = int(self.max_soc_input.text()) if self.max_soc_input.text() else 80
            min_soc = int(self.min_soc_input.text()) if self.min_soc_input.text() else 20

            current_soc = self.latest_rtv_data.get('soc', 0)
            result = self.controller.monitor_charge_discharge(current_soc, charge_time, discharge_time, max_soc, min_soc)
            self.add_log_message(result['message'])

            # 发送命令到服务器
            if self.worker and self.worker.connected:
                command = {
                    'action': result['status'],
                    'charge_time': charge_time,
                    'discharge_time': discharge_time,
                    'max_soc': max_soc,
                    'min_soc': min_soc
                }
                self.worker.send_command(command)

        except Exception as e:
            self.add_log_message(f'应用设置失败: {str(e)}')
            QMessageBox.critical(self, '错误', f'应用设置失败: {str(e)}')

    def process_message(self, data):
        if 'menu' in data:
            self.update_device_tree(data['menu'])
        elif 'rtv_data' in data:
            self.latest_rtv_data = data['rtv_data']

    def update_device_tree(self, menu_data):
        self.device_tree.clear()
        try:
            for device in menu_data:
                item = QTreeWidgetItem([device['name']])
                for param in device.get('parameters', []):
                    param_item = QTreeWidgetItem([param['name']])
                    item.addChild(param_item)
                self.device_tree.addTopLevelItem(item)
        except Exception as e:
            self.add_log_message(f'更新设备树失败: {str(e)}')

    def update_data_display(self):
        self.data_list.clear()
        if self.latest_rtv_data:
            for key, value in self.latest_rtv_data.items():
                item = QListWidgetItem(f'{key}: {value}')
                # SOC值特殊显示
                if key == 'soc':
                    item.setForeground(QColor('blue'))
                    item.setFont(QFont('SimHei', 10, QFont.Bold))
                self.data_list.addItem(item)

    def update_connection_status(self, connected, message):
        self.status_label.setText(message)
        self.status_label.setStyleSheet('color: green; font-weight: bold;' if connected else 'color: red; font-weight: bold;')
        self.connection_progress.setVisible(not connected)

    def add_log_message(self, message):
        timestamp = time.strftime('%H:%M:%S')
        self.log_text.append(f'[{timestamp}] {message}')
        # 自动滚动到底部
        self.log_text.moveCursor(self.log_text.textCursor().End)

    def show_error_message(self, error):
        QMessageBox.critical(self, '连接错误', error)

    def closeEvent(self, event):
        self.stop_websocket()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 设置全局字体
    font = QFont('SimHei')
    app.setFont(font)
    window = EMSMonitorApp()
    window.show()
    sys.exit(app.exec_())