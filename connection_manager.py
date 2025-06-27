import asyncio
import websockets
import json
from PyQt5.QtCore import QThread, pyqtSignal

class WebSocketWorker(QThread):
    message_signal = pyqtSignal(dict)
    log_signal = pyqtSignal(str)
    refresh_signal = pyqtSignal()

    def __init__(self, token):
        super().__init__()
        self.is_running = True
        self.websocket = None
        self.need_refresh = False
        self.token = token
        self.uri = f'ws://ems.hy-power.net:8888/E6F7D5412A20?{self.token}'
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Origin": "http://ems.hy-power.net:8114"
        }

    async def connect_websocket(self):
        if not self.token:
            self.log_signal.emit("未设置token，使用默认token")
            self.token = "a7b403de831ad791006d86e86ecd67ae9df47ba05146fd407080b85a78f430882a1286f19d2d9fbee41ad81fce7e13dc24d75c2a3db4eb445b7f552a0f4bdba656486d824b90533603b7a92ee9130396"
            self.uri = f'ws://ems.hy-power.net:8888/E6F7D5412A20?{self.token}'

        while self.is_running:
            try:
                async with websockets.connect(self.uri, extra_headers=self.headers) as websocket:
                    self.websocket = websocket
                    self.log_signal.emit("WebSocket连接已建立")
                    menu_subscribe = {"func": "menu"}
                    await websocket.send(json.dumps(menu_subscribe))
                    self.log_signal.emit("已发送menu订阅请求")

                    while self.is_running:
                        try:
                            if self.need_refresh:
                                self.need_refresh = False
                                menu_subscribe = {"func": "menu"}
                                await websocket.send(json.dumps(menu_subscribe))
                                self.log_signal.emit("已重新发送menu订阅请求")

                            message = await websocket.recv()
                            self.log_signal.emit(f"收到原始消息: {message[:100]}...")
                            data = json.loads(message)
                            self.message_signal.emit(data)

                            if data.get("func") == "menu":
                                rtv_ids = []
                                menu_data = data.get("data", {})
                                for device_type, devices in menu_data.items():
                                    for device in devices:
                                        for rtv_item in device.get("rtvList", []):
                                            rtv_ids.append(rtv_item["id"])
                                rtv_subscribe = {"func": "rtv", "ids": rtv_ids, "period": 5}
                                await websocket.send(json.dumps(rtv_subscribe))
                                self.log_signal.emit(f"已发送rtv订阅请求，订阅 {len(rtv_ids)} 个ID")

                        except websockets.exceptions.ConnectionClosed:
                            self.log_signal.emit("WebSocket连接已关闭，准备重连...")
                            break
                        except json.JSONDecodeError as e:
                            self.log_signal.emit(f"JSON解析错误: {str(e)}")
                        except Exception as e:
                            self.log_signal.emit(f"接收数据错误: {str(e)}")

            except Exception as e:
                self.log_signal.emit(f"WebSocket连接错误: {str(e)}，3秒后重试...")
                await asyncio.sleep(3)

    def run(self):
        asyncio.run(self.connect_websocket())

    def send_cmd_subscription(self, cmd_id, ref_fid, ref_rid, value):
        message = {
            "func": "cmd",
            "id": cmd_id,
            "refFid": ref_fid,
            "refRid": ref_rid,
            "value": value
        }
        if self.websocket and self.is_running:
            asyncio.run(self.websocket.send(json.dumps(message)))
            self.log_signal.emit(f"发送CMD消息: {json.dumps(message)}")

    def stop(self):
        self.is_running = False
        self.websocket = None
        self.log_signal.emit("WebSocket工作线程已停止")

    def request_refresh(self):
        self.need_refresh = True