class DataProcessor:
    def __init__(self):
        self.device_info = {}  # 设备ID到设备信息的映射
        self.latest_rtv_data = {}  # 存储最新的实时数据
        self.menu_data = {}  # 存储菜单数据

    def process_menu_data(self, menu_data):
        """处理菜单数据并构建设备信息映射"""
        self.menu_data = menu_data
        self.device_info.clear()
        
        for device_type, devices in menu_data.items():
            for device in devices:
                for rtv_item in device.get("rtvList", []):
                    item_id = str(rtv_item["id"])
                    self.device_info[item_id] = {
                        "name": rtv_item.get("fieldChnName", ""),
                        "eng_name": rtv_item.get("fieldEngName", ""),
                        "device_type": device_type,
                        "device_name": device.get("chnName", ""),
                        "table_name": device.get("tableName", "")
                    }

    def process_rtv_data(self, rtv_data):
        """处理实时数据并更新缓存"""
        for item in rtv_data:
            item_id = str(item.get("id"))
            value = item.get("value", "N/A")
            self.latest_rtv_data[item_id] = value

    def get_menu_data(self):
        """获取原始菜单数据"""
        return self.menu_data

    def get_device_info(self, item_id):
        """根据ID获取设备信息"""
        return self.device_info.get(item_id, {})

    def get_latest_value(self, item_id):
        """根据ID获取最新数据值"""
        return self.latest_rtv_data.get(item_id, "N/A")

    def get_grouped_data(self, rtv_ids=None):
        """将数据按设备类型分组"""
        grouped_data = {
            "d_bms": [],
            "d_pcs": [],
            "d_grid": [],
            "d_air_condition": []
        }

        target_ids = rtv_ids if rtv_ids else self.latest_rtv_data.keys()

        for item_id in target_ids:
            device_info = self.get_device_info(item_id)
            if not device_info:
                continue

            device_type = device_info.get("device_type")
            value = self.get_latest_value(item_id)

            if device_type in grouped_data:
                grouped_data[device_type].append((item_id, device_info, value))

        return grouped_data