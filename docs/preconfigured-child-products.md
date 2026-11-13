# 预置子设备模型

集成默认仅支持华为为 Home Assistant 构建的专属物模型。使用此类模型时，仍需声明对应的 `device_type`，并填写服务与 HA 实体映射。`sub_prod_id`、`manufacturer`、`protocol_type`、`setup_type` 固定为 `00`、`002`、`6`、`0`，`model` 自动生成为 `HA-<prod_id>`。下表列出当前收录的模型、`device_type`、适配状态及对应 Profile。

如需使用自定义物模型，请自行查阅相关资料，并在配置文件中显式配置对应子设备的注册信息。由此产生的不可控因素及法律责任由您自行承担。

默认配置启用 9MU7 智控灯泡，需将 HA 实体占位符替换为实际实体；9MXO 和 9MY5 仍以注释示例提供。
“已适配”为“是”表示设备的核心控制或监测服务已由当前适配器覆盖，不代表 Profile 中所有附加服务均已适配。9MTJ、9MTL 和 9MTX 的 `switch.on` 为布尔值，需设置 `on_type: bool`；9MTJ/9MTL 的亮度契约需设为 `min: 1`、`max: 100`、`step: 1`；9MTX 的电参量由 `electric` 适配器按字段绑定。

| `prod_id` | `device_type` | 已适配 | `DeviceNameSpreading` | `Profile` |
| --- | --- | --- | --- | --- |
| `9MU7` | `119` | 是 | [智控灯泡](https://smarthome-drcn.dbankcdn.com/device/guide/9MU7/h5_001/index.html) | [9MU7 Profile](https://smarthome-drcn.dbankcdn.com/device/guide/9MU7/9MU7.json) |
| `9MXO` | `012` | 是 | [智控空调](https://smarthome-drcn.dbankcdn.com/device/guide/9MXO/h5_001/index.html) | [9MXO Profile](https://smarthome-drcn.dbankcdn.com/device/guide/9MXO/9MXO.json) |
| `9MY5` | `01C` | 是 | [智控窗帘](https://smarthome-drcn.dbankcdn.com/device/guide/9MY5/h5_001/index.html) | [9MY5 Profile](https://smarthome-drcn.dbankcdn.com/device/guide/9MY5/9MY5.json) |
| `9MZK` | `015` | 否 | [智控洗衣机](https://smarthome-drcn.dbankcdn.com/device/guide/9MZK/h5_001/index.html) | [9MZK Profile](https://smarthome-drcn.dbankcdn.com/device/guide/9MZK/9MZK.json) |
| `9MZR` | `023` | 否 | [智控微波炉](https://smarthome-drcn.dbankcdn.com/device/guide/9MZR/h5_001/index.html) | [9MZR Profile](https://smarthome-drcn.dbankcdn.com/device/guide/9MZR/9MZR.json) |
| `9MZT` | `079` | 否 | [智控电磁炉](https://smarthome-drcn.dbankcdn.com/device/guide/9MZT/h5_001/index.html) | [9MZT Profile](https://smarthome-drcn.dbankcdn.com/device/guide/9MZT/9MZT.json) |
| `9MZU` | `174` | 否 | [智控壁挂炉](https://smarthome-drcn.dbankcdn.com/device/guide/9MZU/h5_001/index.html) | [9MZU Profile](https://smarthome-drcn.dbankcdn.com/device/guide/9MZU/9MZU.json) |
| `9MZV` | `021` | 否 | [智控烟机](https://smarthome-drcn.dbankcdn.com/device/guide/9MZV/h5_001/index.html) | [9MZV Profile](https://smarthome-drcn.dbankcdn.com/device/guide/9MZV/9MZV.json) |
| `9MZW` | `090` | 否 | [智控燃气灶](https://smarthome-drcn.dbankcdn.com/device/guide/9MZW/h5_001/index.html) | [9MZW Profile](https://smarthome-drcn.dbankcdn.com/device/guide/9MZW/9MZW.json) |
| `9MZY` | `06F` | 否 | [智控直饮机](https://smarthome-drcn.dbankcdn.com/device/guide/9MZY/h5_001/index.html) | [9MZY Profile](https://smarthome-drcn.dbankcdn.com/device/guide/9MZY/9MZY.json) |
| `9MTJ` | `21F` | 是 | [智控夜灯](https://smarthome-drcn.dbankcdn.com/device/guide/9MTJ/h5_001/index.html) | [9MTJ Profile](https://smarthome-drcn.dbankcdn.com/device/guide/9MTJ/9MTJ.json) |
| `9MTL` | `10E` | 是 | [智控床头灯](https://smarthome-drcn.dbankcdn.com/device/guide/9MTL/h5_001/index.html) | [9MTL Profile](https://smarthome-drcn.dbankcdn.com/device/guide/9MTL/9MTL.json) |
| `9MTM` | `1F1` | 否 | [智控压力传感器](https://smarthome-drcn.dbankcdn.com/device/guide/9MTM/h5_001/index.html) | [9MTM Profile](https://smarthome-drcn.dbankcdn.com/device/guide/9MTM/9MTM.json) |
| `9MTV` | `0B0` | 否 | [智控灭蚊器](https://smarthome-drcn.dbankcdn.com/device/guide/9MTV/h5_001/index.html) | [9MTV Profile](https://smarthome-drcn.dbankcdn.com/device/guide/9MTV/9MTV.json) |
| `9MTW` | `026` | 否 | [智控电饭煲](https://smarthome-drcn.dbankcdn.com/device/guide/9MTW/h5_001/index.html) | [9MTW Profile](https://smarthome-drcn.dbankcdn.com/device/guide/9MTW/9MTW.json) |
| `9MTX` | `211` | 是 | [智控断路器](https://smarthome-drcn.dbankcdn.com/device/guide/9MTX/h5_001/index.html) | [9MTX Profile](https://smarthome-drcn.dbankcdn.com/device/guide/9MTX/9MTX.json) |
| `9MYJ` | `063` | 否 | [智控炸锅](https://smarthome-drcn.dbankcdn.com/device/guide/9MYJ/h5_001/index.html) | [9MYJ Profile](https://smarthome-drcn.dbankcdn.com/device/guide/9MYJ/9MYJ.json) |
