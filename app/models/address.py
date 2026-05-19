from typing import Optional
from sqlmodel import SQLModel, Field


class AddressBase(SQLModel):
    """Shared fields and validation rules for all address schemas."""

    name: str
    street: str
    city: str
    country: str
    latitude: float = Field(ge=-90, le=90, description="Latitude (-90 to 90)")
    longitude: float = Field(ge=-180, le=180, description="Longitude (-180 to 180)")


class Address(AddressBase, table=True):
    """Database table model. Inherits all fields from AddressBase and adds a primary key."""

    id: Optional[int] = Field(default=None, primary_key=True)


class AddressCreate(AddressBase):
    """Request body schema for creating an address. No id required."""

    pass


class AddressRead(AddressBase):
    """Response schema for address data. Always includes the id."""

    id: int


class AddressPage(SQLModel):
    """Paginated response envelope for the address list endpoint."""

    total: int
    skip: int
    limit: int
    data: list[AddressRead]
