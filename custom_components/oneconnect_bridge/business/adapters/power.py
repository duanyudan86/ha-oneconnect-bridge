"""Huawei ``power`` read-only power measurement service adapter.

Profile 中的 ``power`` 通常只有一个只读的 ``current`` 数值特性（单位 W），
适配器直接读取 HA 实体的数值并上报，不做单位换算。如果 HA 实体的单位是
kW，请先用模板传感器换算成 W 再绑定。

``current`` 字段名来自 Profile 的常见写法；如果其他设备的 power 服务用了
不同字段名，需要扩展本适配器，而不是复制一份。
"""

from __future__ import annotations

import math

from ..models import ServiceRef


class PowerServiceAdapter:
    service_id = "power"
    _domains = {"sensor", "number", "input_number"}

    def validate_service(self, service: ServiceRef) -> None:
        if service.service_type != "power":
            raise ValueError("power requires st: power")
        if service.contract:
            raise ValueError("power does not accept contract overrides")

    def validate_entities(self, entity_ids: tuple[str, ...]) -> None:
        if len(entity_ids) != 1:
            raise ValueError("power requires exactly one HA entity")
        domain = entity_ids[0].partition(".")[0]
        if domain not in self._domains:
            raise ValueError("power requires a sensor, number or input_number entity")

    async def read_state(
        self, hass, service: ServiceRef, entity_ids: tuple[str, ...]
    ) -> dict[str, object]:
        self.validate_service(service)
        self.validate_entities(entity_ids)
        state = hass.states.get(entity_ids[0])
        if state is None or state.state in {"unknown", "unavailable"}:
            return {}
        try:
            value = float(state.state)
        except (TypeError, ValueError):
            return {}
        if not math.isfinite(value) or value < 0:
            return {}
        return {"current": int(round(value))}

    async def apply_command(
        self,
        hass,
        service: ServiceRef,
        entity_ids: tuple[str, ...],
        payload: dict[str, object],
    ) -> None:
        # ``current`` 在 Profile 里是只读（method: R），没有可执行的 HA 动作。
        self.validate_service(service)
        self.validate_entities(entity_ids)


ADAPTER = PowerServiceAdapter()
