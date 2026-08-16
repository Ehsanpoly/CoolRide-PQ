from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from .models import ControlDecision, Telemetry


@dataclass(frozen=True)
class AdapterCapability:
    protocol: str
    read_only: bool
    supports_quality: bool
    supports_timestamp: bool
    command_acknowledgement: bool


class TelemetryAdapter(ABC):
    @abstractmethod
    def capabilities(self) -> AdapterCapability:
        raise NotImplementedError

    @abstractmethod
    def read(self) -> Telemetry:
        raise NotImplementedError


class CommandAdapter(ABC):
    @abstractmethod
    def capabilities(self) -> AdapterCapability:
        raise NotImplementedError

    @abstractmethod
    def validate(self, decision: ControlDecision) -> tuple[bool, tuple[str, ...]]:
        raise NotImplementedError

    @abstractmethod
    def apply(self, decision: ControlDecision) -> Mapping[str, Any]:
        raise NotImplementedError


class AdvisoryOnlyAdapter(CommandAdapter):
    """Default adapter: records a decision but cannot actuate equipment."""

    def capabilities(self) -> AdapterCapability:
        return AdapterCapability("advisory", True, True, True, False)

    def validate(self, decision: ControlDecision) -> tuple[bool, tuple[str, ...]]:
        return True, ("advisory_only_no_actuation",)

    def apply(self, decision: ControlDecision) -> Mapping[str, Any]:
        return {"status": "recorded", "actuated": False, "decision": decision.to_dict()}
