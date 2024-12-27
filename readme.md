系统设计步骤：
1.登录EMS管理后台：http://ems.hy-power.net:8114/dashboard/index
     --登录账号：BAIYILED01
     --登录密码：123456789
     --验证码：需要系统自动识别，如果识别三次失败，请提后台验证码图片由供人工输入

说明：
   -先实现第1步后，再来实现第2步;
   -第1步用有窗口的方式来实现，可以实时观察数据;


2.获取主页menu list --固定的websocket token

   // 创建 WebSocket 连接
const socket = new WebSocket('ws://ems.hy-power.net:8888/E6F7D5412A20?d0bdae3f37de30f0a3386ca265b9dad07111a89679add764042f12ca60d017da2bc9de82cfcb45f59151e279661e6954639c4def137595e5e7350632baced8925503b37206c533afad17ad72120a814a');

// 监听连接建立
socket.onopen = function(event) {
    console.log('WebSocket连接已建立');
    
    // 向服务器发送订阅消息，订阅 "menu" 主题
    const subscribeMessage = JSON.stringify({ func: 'menu' });
    socket.send(subscribeMessage);
    console.log('已发送订阅请求:', subscribeMessage);
};

// 监听消息接收
socket.onmessage = function(event) {
    const data = event.data;

    try {
        // 如果收到的消息是 JSON 格式
        const json = JSON.parse(data);
        console.log('收到 JSON 消息:', json);

        // 根据数据处理和展示
        if (json.func === "menu" && json.data) {
            // 假设数据格式符合你之前给出的样例
            const menuData = json.data;
            Object.keys(menuData).forEach((deviceType) => {
                console.log(`设备类型: ${deviceType}`);
                menuData[deviceType].forEach((device) => {
                    console.log(`设备名称: ${device.chnName}, 英文名称: ${device.engName}`);
                });
            });
        }

    } catch (err) {
        // 如果收到的消息不是 JSON 格式
        if (data instanceof ArrayBuffer) {
            console.log('收到二进制消息:', new Uint8Array(data));
        } else {
            console.log('收到非 JSON 消息:', data);
        }
    }
};

// 监听错误
socket.onerror = function(error) {
    console.error('WebSocket 错误:', error);
};

// 监听连接关闭
socket.onclose = function() {
    console.log('WebSocket连接已关闭');
};



  // 向服务器发送订阅消息，订阅 "menu" 主题
    const subscribeMessage = JSON.stringify({    "func": "rtv",
    "ids": [
      412001051, 409001102, 409001103, 409001104, 409001106, 409001107, 409001067, 409001071, 409001075, 
    ],
    "period": 5 });
    socket.send(subscribeMessage);
    console.log('已发送订阅请求:', subscribeMessage);

   

 取出数据然后以表格或其他元素显示形式，分别显示空调、BMS、PCS、电网4组设备的数据中的 


第3步：实现数据获取，并实时显示
// 向服务器发送订阅消息，订阅 "rtv" 主题
const subscribeMessage2 = JSON.stringify({
    "func": "rtv",
    "ids": [
        412001051, 409001102, 409001103, 409001104, 409001106, 409001107, 409001067, 409001071, 409001075,
    ],
    "period": 5
});
socket.send(subscribeMessage2);



第4步：监控关键数据SOC
在ems_websocket_client.py程序中的更新数据的地方加一个调用外部监控模块：F:\360Downloads\BaiduNetdiskDownload\WicToolDemo\autoRunBY-EMS\emsContronl.py
然后将412001056-SOC、412001051-簇电池簇状态、412001053-簇组电流、409001067-三相实时有功功率(KW)、413001100-柜内温度(℃) 这些数据传递到模块中，然后分别设计判断方法，分别判断数据及相关处理，
同时


# EMS监控系统使用说明

## 环境要求
- Python 3.8+
- Chrome浏览器

## 安装步骤
1. 安装依赖包：
```bash
pip install -r requirements.txt
```

2. 运行程序：
```bash
python ems_monitor.py
```

## 功能说明
1. 自动登录EMS管理后台
2. 自动识别验证码（失败后支持人工输入）
3. 实时获取并显示仪表盘数据
4. 提供图形界面，方便监控和操作

## 使用方法
1. 点击"启动监控"按钮开始监控
2. 程序会自动进行登录和数据获取
3. 如果验证码识别失败三次，会弹出输入框请求手动输入
4. 可以随时点击"停止监控"按钮结束监控
5. 所有操作日志都会实时显示在主界面
