import datetime

class ChargeDischargeController:
    def __init__(self):
        self.is_charging = False
        self.is_discharging = False

    def monitor_charge_discharge(self, soc, charging_start_time, charging_end_time, discharging_start_time, discharging_end_time, soc_upper_limit, soc_lower_limit):
        current_time = datetime.datetime.now().time()  # 获取当前时间

        # 测试被调用传入参数打印
        print("当前SOC值:", soc)
        print("充电开始时间:", charging_start_time)
        print("充电结束时间:", charging_end_time)
        print("放电开始时间:", discharging_start_time)
        print("放电结束时间:", discharging_end_time)
        print("SOC上限:", soc_upper_limit)
        print("SOC下限:", soc_lower_limit)

        # 判断是否在充电时间段内
        # if charging_start_time <= current_time <= charging_end_time:
        #     if not self.is_charging:
        #         self.start_charging()  # 启动充电
        #     if soc >= soc_upper_limit:
        #         self.stop_charging()  # 停止充电

        # # 判断是否在放电时间段内
        # elif discharging_start_time <= current_time <= discharging_end_time:
        #     if not self.is_discharging:
        #         self.start_discharging()  # 启动放电
        #     if soc <= soc_lower_limit:
        #         self.stop_discharging()  # 停止放电


    def start_charging(self):
        self.is_charging = True
        print("开始充电")

    def stop_charging(self):
        self.is_charging = False
        print("停止充电")

    def start_discharging(self):
        self.is_discharging = True
        print("开始放电")

    def stop_discharging(self):
        self.is_discharging = False
        print("停止放电")


def monitor_data(soc, battery_status, current, power, temperature, charging_start_time, charging_end_time, discharging_start_time, discharging_end_time, soc_upper_limit, soc_lower_limit):
    """
    处理监控数据的方法。
    """
    print("SOC:", soc)
    print("Battery Status:", battery_status)
    print("Current:", current)
    print("Power:", power)
    print("Temperature:", temperature)
    print("Charging Start Time:", charging_start_time)
    print("Charging End Time:", charging_end_time)
    print("Discharging Start Time:", discharging_start_time)
    print("Discharging End Time:", discharging_end_time)
    print("SOC Upper Limit:", soc_upper_limit)
    print("SOC Lower Limit:", soc_lower_limit)
    
    # 在这里添加数据判断和处理逻辑
    if soc > soc_upper_limit:
        print("SOC超出上限，需要降低充电速率")
    elif soc < soc_lower_limit:
        print("SOC超出下限，需要提高充电速率")
    else:
        print("SOC正常，继续充电")