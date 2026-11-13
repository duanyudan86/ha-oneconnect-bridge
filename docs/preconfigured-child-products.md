# 预置子设备模型

集成默认仅支持华为为 Home Assistant 构建的专属物模型。使用此类模型时，仍需声明对应的 `device_type`，并填写服务与 HA 实体映射。`sub_prod_id`、`manufacturer`、`protocol_type`、`setup_type` 固定为 `00`、`002`、`6`、`0`，`model` 自动生成为 `HA-<prod_id>`。下表列出当前配置示例及对应 Profile。

如需使用自定义物模型，请自行查阅相关资料，并在配置文件中显式配置对应子设备的注册信息。由此产生的不可控因素及法律责任由您自行承担。

默认配置启用 9MU7 智控灯泡，需将 HA 实体占位符替换为实际实体；9MXO 和 9MY5 仍以注释示例提供。

| `prod_id` | `DeviceNameSpreading` | `Profile` |
| --- | --- | --- |
| `9MU7` | [智控灯泡](https://smarthome-drcn.dbankcdn.com/device/guide/9MU7/h5_001/index.html) | [9MU7 Profile](https://smarthome-drcn.dbankcdn.com/device/guide/9MU7/9MU7.json) |
| `9MXO` | [智控空调](https://smarthome-drcn.dbankcdn.com/device/guide/9MXO/h5_001/index.html) | [9MXO Profile](https://smarthome-drcn.dbankcdn.com/device/guide/9MXO/9MXO.json) |
| `9MY5` | [智控窗帘](https://smarthome-drcn.dbankcdn.com/device/guide/9MY5/h5_001/index.html) | [9MY5 Profile](https://smarthome-drcn.dbankcdn.com/device/guide/9MY5/9MY5.json) |
