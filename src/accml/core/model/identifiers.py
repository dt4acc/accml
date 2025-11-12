from dataclasses import dataclass


@dataclass(frozen=True)
class LatticeElementPropertyID:
    element_name: str
    property: str

    def known(self) -> bool:
        return self.property is not None and self.element_name is not None


@dataclass(frozen=True)
class DevicePropertyID:
    device_name: str
    property: str

    def known(self) -> bool:
        return self.property is not None and self.device_name is not None


@dataclass(frozen=True, eq=True)
class ConversionID:
    lattice_property_id: LatticeElementPropertyID
    device_property_id: DevicePropertyID
