// 这是获取全部数据列表名称订阅主题及数据响应

// 向服务器发送订阅消息，订阅 "menu" 主题
const subscribeMessage1 = JSON.stringify({ "func": "menu" });
socket.send(subscribeMessage);

// 返回的列表名称数据结构和真实数据
var response1 = {
    "data": {
        "d_air_condition": [
            {
                "chnName": "海悟空调",
                "dispIdx": 1,
                "engName": "air-conditioning",
                "id": 1,
                "rtvList": [
                    {
                        "dispType": 7,
                        "fieldChnName": "海悟空调 柜内温度（℃）",
                        "fieldEngName": "air-conditioning Cabinet temperature",
                        "fieldId": 413100,
                        "fieldName": "rtv_other",
                        "hisIdx": 80,
                        "hisPeriod": 1,
                        "id": 413001100,
                        "rowId": 1,
                        "state": 0,
                        "tableId": 413,
                        "tableName": "d_air_condition",
                        "valueType": 7
                    },
                    {
                        "dispType": 7,
                        "fieldChnName": "海悟空调 内管温度（℃）",
                        "fieldEngName": "air-conditioning Inner tube temperature",
                        "fieldId": 413101,
                        "fieldName": "rtv_other",
                        "hisIdx": 81,
                        "hisPeriod": 1,
                        "id": 413001101,
                        "rowId": 1,
                        "state": 0,
                        "tableId": 413,
                        "tableName": "d_air_condition",
                        "valueType": 7
                    }
                ],
                "tableChnName": "空调定义表",
                "tableEngName": "Air condition define",
                "tableId": 413,
                "tableName": "d_air_condition"
            }
        ],
        "d_pcs": [
            {
                "chnName": "PCS",
                "dispIdx": 1,
                "engName": "PCS",
                "id": 1,
                "rtvList": [
                    {
                        "dispType": 7,
                        "fieldChnName": "PCS AB线实时电压（kV）",
                        "fieldEngName": "PCS Real time voltage of line AB (kV)",
                        "fieldId": 409058,
                        "fieldName": "rtv_Uab",
                        "hisIdx": 0,
                        "hisPeriod": 1,
                        "id": 409001058,
                        "refXid": 0,
                        "rowId": 1,
                        "state": 0,
                        "tableId": 409,
                        "tableName": "d_pcs",
                        "valueType": 7
                    },
                    {
                        "dispType": 7,
                        "fieldChnName": "PCS BC线实时电压（kV）",
                        "fieldEngName": "PCS Real time voltage of line BC (kV)",
                        "fieldId": 409059,
                        "fieldName": "rtv_Ubc",
                        "hisIdx": 1,
                        "hisPeriod": 1,
                        "id": 409001059,
                        "refXid": 0,
                        "rowId": 1,
                        "state": 0,
                        "tableId": 409,
                        "tableName": "d_pcs",
                        "valueType": 7
                    }
                ],
                "tableChnName": "储能机定义表",
                "tableEngName": "Energy storage define",
                "tableId": 409,
                "tableName": "d_pcs"
            }
        ],
        "d_bms": [
            {
                "chnName": "BMS",
                "dispIdx": 1,
                "chnType": "d_bms",
                "id": 1,
                "rtvList": [
                    {
                        "dispType": 12,
                        "fieldChnName": "BMS 簇电池簇状态",
                        "fieldEngName": "BMS cluster status",
                        "fieldId": 412051,
                        "fieldName": "rtv_dev_stat",
                        "hisIdx": 0,
                        "hisPeriod": 0,
                        "id": 412001051,
                        "refXid": 21,
                        "rowId": 1,
                        "state": 0,
                        "tableId": 412,
                        "tableName": "d_bms",
                        "valueType": 5
                    },
                    {
                        "dispType": 7,
                        "fieldChnName": "BMS 簇组电压",
                        "fieldEngName": "BMS Cluster voltage",
                        "fieldId": 412052,
                        "fieldName": "rtv_volt",
                        "hisIdx": 61,
                        "hisPeriod": 1,
                        "id": 412001052,
                        "refXid": 0,
                        "rowId": 1,
                        "state": 0,
                        "tableId": 412,
                        "tableName": "d_bms",
                        "valueType": 7
                    }
                ],
                "tableChnName": "电池管理系统定义表",
                "tableEngName": "Battery manage system define",
                "tableId": 412,
                "tableName": "d_bms"
            }
        ],
        "d_grid": [
            {
                "chnName": "安科瑞电表",
                "dispIdx": 1,
                "engName": "meter",
                "id": 1,
                "rtvList": [
                    {
                        "dispType": 7,
                        "fieldChnName": "安科瑞电表 AB线实时电压（V）",
                        "fieldEngName": "meter Real time voltage of phase AB(kV)",
                        "fieldId": 411052,
                        "fieldName": "rtv_Uab",
                        "hisIdx": 33,
                        "hisPeriod": 1,
                        "id": 411001052,
                        "refXid": 0,
                        "rowId": 1,
                        "state": 0,
                        "tableId": 411,
                        "tableName": "d_grid",
                        "valueType": 7
                    },
                    {
                        "dispType": 7,
                        "fieldChnName": "安科瑞电表 BC线实时电压（V）",
                        "fieldEngName": "meter Real time voltage of phase BC(kV)",
                        "fieldId": 411053,
                        "fieldName": "rtv_Ubc",
                        "hisIdx": 34,
                        "hisPeriod": 1,
                        "id": 411001053,
                        "refXid": 0,
                        "rowId": 1,
                        "state": 0,
                        "tableId": 411,
                        "tableName": "d_grid",
                        "valueType": 7
                    }
                    , {}, {

                    }
                ],
                "tableChnName": "市电并网点定义表",
                "tableEngName": "Grid define",
                "tableId": 411,
                "tableName": "d_grid"
            }
        ]
    },
    "func": "menu"
}

// 向服务器发送订阅消息，订阅 "rtv" 主题
const subscribeMessage2 = JSON.stringify({
    "func": "rtv",
    "ids": [
        412001051, 409001102, 409001103, 409001104, 409001106, 409001107, 409001067, 409001071, 409001075,
    ],
    "period": 5
});

socket.send(subscribeMessage2);

// 返回的数据结构和真实数据
var response2 = {
    data: [
        {
            id: "409001067",
            value: "19.66"
        },
        {
            id: "409001071"
            , value: "0"
        }
    ],
    func: "rtv"
}

/*  备注：  // 数组数量以接口实际数量为准*/