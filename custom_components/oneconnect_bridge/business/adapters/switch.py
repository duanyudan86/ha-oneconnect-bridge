"""Huawei `switch.on` adapter with configurable wire and climate control.

同一套适配器覆盖 Profile 里常见的 ``switch`` 服务族：serviceId 可以是
``switch`` / ``switch1``~``switch4`` / ``usbSwitch1``，空调的 ``switchPTC``
（电辅热），以及热水器的 ``inchingSwitch``（点动循环）/ ``boostMode``
（增压洗）；这些服务都是单个布尔 ``on``（1 开 / 0 关）。``st`` 仍写
``switch``，``sid`` 填 Profile 里的服务标识即可。
"""

from __future__ import annotations

from ..models import ServiceRef


class SwitchServiceAdapter:
    service_id = "switch"
    aliases = (
        "switch1",
        "switch2",
        "switch3",
        "switch4",
        "usbSwitch1",
        "switchPTC",
        "inchingSwitch",
        "boostMode",
    )
    _domains = {"climate", "light", "switch", "fan"}

    def validate_service(self, service: ServiceRef) -> None:
        if service.service_type not in {"switch", "binarySwitch"}:
            raise ValueError("switch requires st: switch or binarySwitch")
        unknown = set(dict(service.contract)) - {"on_type", "on_mode"}
        if unknown:
            raise ValueError(
                f"switch has unsupported contract keys: {', '.join(sorted(unknown))}"
            )
        if _on_type(service) not in {"int", "bool"}:
            raise ValueError("switch contract on_type must be int or bool")
        if not isinstance(_on_mode(service), str) or not _on_mode(service):
            raise ValueError("switch contract on_mode must be non-empty text")

    def validate_entities(self, entity_ids: tuple[str, ...]) -> None:
        if len(entity_ids) != 1:
            raise ValueError("switch currently requires exactly one HA entity")
        domain, separator, _object_id = entity_ids[0].partition(".")
        if not separator or domain not in self._domains:
            raise ValueError("switch requires a climate, light, switch, or fan entity")

    async def read_state(
        self, hass, service: ServiceRef, entity_ids: tuple[str, ...]
    ) -> dict[str, object]:
        self.validate_service(service)
        self.validate_entities(entity_ids)
        state = hass.states.get(entity_ids[0])
        if state is None:
            return {}
        domain = entity_ids[0].partition(".")[0]
        if domain == "climate":
            if state.state in {"unknown", "unavailable", "off"}:
                is_on = False
            else:
                is_on = True
        elif state.state in {"on", "off"}:
            is_on = state.state == "on"
        else:
            return {}
        return {"on": is_on if _on_type(service) == "bool" else int(is_on)}

    async def apply_command(
        self,
        hass,
        service: ServiceRef,
        entity_ids: tuple[str, ...],
        payload: dict[str, object],
    ) -> None:
        self.validate_service(service)
        self.validate_entities(entity_ids)
        enabled = _parse_on_value(service, payload.get("on"))
        if enabled is None:
            return
        domain, _separator, _object_id = entity_ids[0].partition(".")
        if domain == "climate":
            state = hass.states.get(entity_ids[0])
            hvac_mode = "off" if not enabled else _on_mode(service)
            allowed = state.attributes.get("hvac_modes") if state else None
            if isinstance(allowed, list) and allowed and hvac_mode not in allowed:
                return
            await hass.services.async_call(
                "climate",
                "set_hvac_mode",
                {"entity_id": entity_ids[0], "hvac_mode": hvac_mode},
                blocking=True,
            )
            return
        await hass.services.async_call(
            domain,
            "turn_on" if enabled else "turn_off",
            {"entity_id": entity_ids[0]},
            blocking=True,
        )


ADAPTER = SwitchServiceAdapter()


def _parse_on_value(service: ServiceRef, value: object) -> bool | None:
    if _on_type(service) == "int":
        if isinstance(value, bool) or not isinstance(value, int) or value not in {0, 1}:
            return None
        return bool(value)
    return value if isinstance(value, bool) else None


def _on_type(service: ServiceRef) -> str:
    return service.contract_value("on_type", "int")


def _on_mode(service: ServiceRef) -> str:
    return service.contract_value("on_mode", "auto")
