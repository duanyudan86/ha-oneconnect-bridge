"""华为 ``status`` 服务：一个设备状态枚举（同语义、不同整数值）。

同一个 sid 在 947 个 Profile 里语义各不相同，但**每个设备的 ``states`` 只描述一个
语义族**：同一个含义在不同 Profile 里用了不同整数（例如"开/关"是 ``0/1`` 还是
``1/0``）。适配器不推断语义，只做「HA 状态 -> 云端枚举值」的映射；
``select`` 域额外支持反向写回（见 ``apply_command``）。

默认契约来源
    prodId   : ``2N8I`` —— 晾衣机（cover 两态映射为限位）
    Profile  : https://smarthome-drcn.dbankcdn.com/device/guide/2N8I/2N8I.json
    常见性   : 947 个 Profile 使用 serviceId=status；特征名 ``status`` 占 97.6%，
               其余为 value / mode / workStatus / connect 等别名；92.5% 只读
    已验证   : 2026-10-22，5 个不同语义的 Profile（都绑定同一套真实 HA 实体）：
               - ``2N8I`` 限位：cover ``closed`` / ``open`` → 1 / 2，运动中落 ``fallback`` 0
               - ``A2ML`` 计费：``{'on': 1}`` + ``fallback: 0``（未命中走 fallback）
               - ``27NV`` 工作状态：``{'off': 0}`` + ``fallback: 1``（命中与兜底各验一次）
               - ``162X`` 净水器：``0/1/2/3/100`` 五值全量 —— 证明**非连续值域原样上报**
               - ``21BM`` 告警：``0/1/2`` 三值全量；未命中的值不上报且只告警一次
               另有 ``21DA`` ×2（``states: {}`` + ``fallback: 0`` 恒报 0）
    未验证   : 多段状态族（待机/工作中/预约/完成…）只验证到"映射正确"，尚未在
               多态实体上长期运行；``RW`` 方向只实现 ``select`` 域的写回，
               尚未在真实设备上验证

适用边界（对应贡献指南第 6 条：contract 只覆盖语义兼容的差异）
    - ``states`` 只表达**同一语义**在 Profile 中的整数值差异（开/关、有人/无人、
      正常/欠费），而不是用配置把不同语义塞进同一个契约项
    - 不同语义族由各自设备的映射分别描述，适配器不据此推断设备类型或业务含义
    - HA 实体无法表达的语义（例如物理限位「最高/最低」）只能用 ``fallback`` 兜底，
      并应在映射注释里标为未验证
    - ``select`` 实体：它的 state 就是当前选项文本，直接作为 ``states`` 的键使用
      （常见于本地集成把「记忆开关」建模成 select 的设备）。Profile 把该枚举标成
      ``RW`` 时支持写回：云端下发的值反查 ``states`` 后调用
      ``select.select_option``；cover / binary_sensor / sensor 没有可写动作，保持只读
    - 特征名 ``status``、状态读取路径与 payload 组装仍在本模块内

contract（``states`` 与 ``fallback`` 至少配置一项）
    states   : HA 状态字符串 -> 云端枚举值，可以是空映射。按 Profile 的
               ``enumList`` 配置，例如
                   states: { closed: 1, open: 2 }     # 限位：关=上限，开=下限
                   states: { "off": 0, "on": 1 }      # 有人 / 无人
                   states: { "on": 1, "off": 0 }      # 已开启 / 已关闭（反序）
                   states: {}                         # 服务无法观测，只靠 fallback
               ``unknown`` / ``unavailable`` 不进表，代码统一跳过。
    fallback : 未命中 ``states`` 时上报的整数。省略则未命中不上报（并告警一次）
    写回     : 仅 ``select`` 域生效。云端下发 ``status`` 整数值时反查
               ``states`` 得到选项文本并调用 ``select.select_option``；
               ``fallback`` 不参与反查，同一个值对应多个键时无法反查，
               告警一次并跳过
"""

from __future__ import annotations

import logging

from ..models import ServiceRef


_LOGGER = logging.getLogger(__name__)

# 同一个 (服务, 实体, 值) 只告警一次：配置漏项时能看到，但 app 重试不会刷屏
_WARNED: set[tuple[str, str | None, object]] = set()
_WARNED_LIMIT = 1024


def _remember_warning(key: tuple[str, str | None, object]) -> None:
    if len(_WARNED) >= _WARNED_LIMIT:
        _WARNED.pop()
    _WARNED.add(key)


class StatusServiceAdapter:
    service_id = "status"
    aliases = ("memorySwitch",)
    _domains = {"cover", "binary_sensor", "sensor", "select"}

    def validate_service(self, service: ServiceRef) -> None:
        if service.service_type != "status":
            raise ValueError("status requires st: status")
        unknown = set(dict(service.contract)) - {"states", "fallback"}
        if unknown:
            raise ValueError(
                f"status has unsupported contract keys: {', '.join(sorted(unknown))}"
            )
        states = _states(service)
        fallback = _fallback(service)
        if states is None and fallback is None:
            raise ValueError("status requires states or fallback")
        if not states and fallback is None:
            raise ValueError("status contract needs fallback when states is empty")

    def validate_entities(self, entity_ids: tuple[str, ...]) -> None:
        if len(entity_ids) != 1:
            raise ValueError("status requires exactly one HA entity")
        domain, separator, _object_id = entity_ids[0].partition(".")
        if not separator or domain not in self._domains:
            raise ValueError(
                "status requires a cover, binary_sensor, sensor or select entity"
            )

    async def read_state(
        self, hass, service: ServiceRef, entity_ids: tuple[str, ...]
    ) -> dict[str, object]:
        self.validate_service(service)
        self.validate_entities(entity_ids)
        state = hass.states.get(entity_ids[0])
        if state is None or state.state in {"unknown", "unavailable"}:
            return {}
        states = _states(service) or {}
        if state.state in states:
            return {"status": states[state.state]}
        fallback = _fallback(service)
        if fallback is not None:
            return {"status": fallback}
        # 未命中的状态只告警一次，避免配置漏项时静默无数据
        _warn_unhandled("status", state.state, source=entity_ids[0])
        return {}

    async def apply_command(
        self,
        hass,
        service: ServiceRef,
        entity_ids: tuple[str, ...],
        payload: dict[str, object],
    ) -> None:
        self.validate_service(service)
        self.validate_entities(entity_ids)
        entity_id = entity_ids[0]
        if entity_id.partition(".")[0] != "select":
            # cover / binary_sensor / sensor 没有可写动作，保持只读
            return
        if "status" not in payload:
            return
        value = _wire_int(payload.get("status"))
        if value is None:
            _LOGGER.warning(
                "status <- %s: ignoring non-integer command value %r",
                entity_id,
                payload.get("status"),
            )
            return
        options, ambiguous = _options_by_value(service)
        if value in ambiguous:
            _warn_ambiguous("status", value, source=entity_id)
            return
        option = options.get(value)
        if option is None:
            _warn_unhandled("status", value, source=entity_id)
            return
        state = hass.states.get(entity_id)
        if state is not None and state.state == option:
            return
        await hass.services.async_call(
            "select",
            "select_option",
            {"entity_id": entity_id, "option": option},
            blocking=True,
        )


ADAPTER = StatusServiceAdapter()


def _states(service: ServiceRef) -> dict[str, int] | None:
    """解析并校验 ``states``，返回 HA 状态 -> 枚举值的映射或 ``None``。"""

    raw = service.contract_value("states")
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise ValueError("status contract states must be a mapping")
    result: dict[str, int] = {}
    for key, value in raw.items():
        if not isinstance(key, str) or not key:
            raise ValueError(
                "status contract states keys must be non-empty text "
                "(quote YAML booleans such as 'on' / 'off')"
            )
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError("status contract states values must be integers")
        result[key] = value
    return result


def _fallback(service: ServiceRef) -> int | None:
    """解析并校验 ``fallback``，返回整数或 ``None``。"""

    raw = service.contract_value("fallback")
    if raw is None:
        return None
    if isinstance(raw, bool) or not isinstance(raw, int):
        raise ValueError("status contract fallback must be an integer")
    return raw


def _wire_int(value: object) -> int | None:
    """Accept only wire-plausible numbers (int or integral float); reject bool/str."""

    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return None


def _options_by_value(service: ServiceRef) -> tuple[dict[int, str], set[int]]:
    """云端枚举值 -> select 选项文本，以及无法反查的歧义值集合。"""

    options: dict[int, str] = {}
    ambiguous: set[int] = set()
    for option, value in (_states(service) or {}).items():
        if value in options and options[value] != option:
            ambiguous.add(value)
        else:
            options.setdefault(value, option)
    for value in ambiguous:
        options.pop(value, None)
    return options, ambiguous


def _warn_ambiguous(adapter: str, value: object, *, source: str | None = None) -> None:
    """Report one ambiguous value once per source: several options share it."""

    key = (adapter, source, ("ambiguous", value))
    if key in _WARNED:
        return
    _remember_warning(key)
    label = adapter if source is None else f"{adapter} <- {source}"
    _LOGGER.warning(
        "%s: value %r matches multiple select options; skipping write", label, value
    )


def _warn_unhandled(adapter: str, value: object, *, source: str | None = None) -> None:
    """Report one unhandled value once per source, so a wrong contract is visible."""

    key = (adapter, source, value)
    if key in _WARNED:
        return
    _remember_warning(key)
    label = adapter if source is None else f"{adapter} <- {source}"
    _LOGGER.warning(
        "%s: unhandled value %r has no Home Assistant mapping", label, value
    )
