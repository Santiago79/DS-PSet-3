from dataclasses import dataclass, field
from typing import Optional
from backend.domain.exceptions import ValidationError
from domain.enums import Role
from uuid import uuid4

@dataclass
class User:
    name: str
    email: str
    hashed_password: str
    role: Role
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        if not self.name or len(self.name.strip()) < 2:
            raise ValidationError("El nombre del cliente debe tener al menos 2 caracteres")
        if "@" not in self.email:
            raise ValidationError("El formato del email es inválido")
