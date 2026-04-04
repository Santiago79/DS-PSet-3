from dataclasses import dataclass

@dataclass
class UserResponseDTO:
    id: str
    name: str
    email: str
    role: str

@dataclass
class LoginRequestDTO:
    email: str
    password: str

@dataclass
class LoginResponseDTO:
    access_token: str
    token_type: str = "bearer"