"""Register the Huawei service adapters shipped with this integration."""

from __future__ import annotations

from .api import ServiceAdapter
from .registry import ADAPTERS


def _register_adapter(
    adapters: dict[str, ServiceAdapter],
    owners: dict[str, str],
    module_name: str,
    adapter: ServiceAdapter,
) -> None:
    service_id = getattr(adapter, "service_id", None)
    if not isinstance(service_id, str) or not service_id:
        raise ValueError(f"adapter module {module_name} has no valid service_id")

    aliases = getattr(adapter, "aliases", ())
    if not isinstance(aliases, tuple) or any(
        not isinstance(alias, str) or not alias for alias in aliases
    ):
        raise ValueError(
            f"adapter module {module_name} aliases must be a tuple of non-empty text"
        )

    service_ids = (service_id, *aliases)
    if len(set(service_ids)) != len(service_ids):
        raise ValueError(
            f"adapter module {module_name} declares duplicate service IDs: "
            f"{', '.join(service_ids)}"
        )
    for candidate in service_ids:
        previous_owner = owners.get(candidate)
        if previous_owner is not None:
            raise ValueError(
                f"duplicate Huawei service ID {candidate!r}: "
                f"{module_name} conflicts with {previous_owner}"
            )
        adapters[candidate] = adapter
        owners[candidate] = module_name


def _build_adapters() -> dict[str, ServiceAdapter]:
    adapters: dict[str, ServiceAdapter] = {}
    owners: dict[str, str] = {}
    for adapter in ADAPTERS:
        module_name = type(adapter).__module__.rsplit(".", 1)[-1]
        _register_adapter(adapters, owners, module_name, adapter)
    return adapters


_ADAPTERS_BY_SERVICE_ID = _build_adapters()


def get_service_adapter(service_id: str) -> ServiceAdapter:
    try:
        return _ADAPTERS_BY_SERVICE_ID[service_id]
    except KeyError as error:
        raise ValueError(f"unknown Huawei service: {service_id}") from error


__all__ = ["get_service_adapter"]
