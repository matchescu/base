from dataclasses import dataclass, field


@dataclass(repr=True, eq=True, order=True, unsafe_hash=True, frozen=True)
class FeatureInfo:
    name: str = field(init=True, repr=True, hash=True, compare=True)
    ordinal: int = field(init=True, repr=True, hash=True, compare=True)
