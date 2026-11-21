"""Explicit registry of trusted Huawei service adapters."""

from __future__ import annotations

from .action import ADAPTER as ACTION
from .air_detector import ADAPTER as AIR_DETECTOR
from .alarm import ADAPTER as ALARM
from .api import ServiceAdapter
from .brightness import ADAPTER as BRIGHTNESS
from .cct import ADAPTER as CCT
from .cleaner_robot import ADAPTER as CLEANER_ROBOT
from .colour import ADAPTER as COLOUR
from .electric import ADAPTER as ELECTRIC
from .fan import ADAPTER as FAN
from .gas_sensor import ADAPTER as GAS_SENSOR
from .hcho import ADAPTER as HCHO
from .humidity import ADAPTER as HUMIDITY
from .mode import ADAPTER as MODE
from .motor import ADAPTER as MOTOR
from .open_level import ADAPTER as OPEN_LEVEL
from .opener import ADAPTER as OPENER
from .power import ADAPTER as POWER
from .status import ADAPTER as STATUS
from .switch import ADAPTER as SWITCH
from .temperature import ADAPTER as TEMPERATURE


ADAPTERS: tuple[ServiceAdapter, ...] = (
    SWITCH,
    BRIGHTNESS,
    CCT,
    COLOUR,
    ELECTRIC,
    TEMPERATURE,
    HUMIDITY,
    AIR_DETECTOR,
    MOTOR,
    OPEN_LEVEL,
    OPENER,
    HCHO,
    ALARM,
    GAS_SENSOR,
    MODE,
    FAN,
    CLEANER_ROBOT,
    POWER,
    STATUS,
    ACTION,
)
