from geopy.distance import geodesic
from sqlmodel import Session, select

from app.models.address import Address, AddressCreate


def create(db: Session, address: AddressCreate) -> Address:
    """Persist a new address to the database and return it with its generated id."""
    db_address = Address.model_validate(address)
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    return db_address


def search(
    db: Session,
    name: str | None = None,
    street: str | None = None,
    city: str | None = None,
    country: str | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
    radius_km: float | None = None,
) -> list[Address]:
    """Return addresses matching all provided filters.

    Text filters (name, street, city, country) are case-insensitive partial
    matches. Proximity filter (latitude, longitude, radius_km) must all be
    supplied together; when present, only addresses within radius_km of the
    given point are returned. Filters can be freely combined.
    """
    query = select(Address)
    if name:
        query = query.where(Address.name.ilike(f"%{name}%"))
    if street:
        query = query.where(Address.street.ilike(f"%{street}%"))
    if city:
        query = query.where(Address.city.ilike(f"%{city}%"))
    if country:
        query = query.where(Address.country.ilike(f"%{country}%"))
    addresses = db.exec(query).all()
    if latitude is not None and longitude is not None and radius_km is not None:
        addresses = [
            a for a in addresses
            if geodesic((latitude, longitude), (a.latitude, a.longitude)).km <= radius_km
        ]
    return addresses


def update(db: Session, address_id: int, address: AddressCreate) -> Address | None:
    """Replace all fields on an existing address. Returns None if not found."""
    db_address = db.get(Address, address_id)
    if not db_address:
        return None
    for key, value in address.model_dump().items():
        setattr(db_address, key, value)
    db.commit()
    db.refresh(db_address)
    return db_address


def delete(db: Session, address_id: int) -> bool:
    """Delete an address by id. Returns True if deleted, False if not found."""
    db_address = db.get(Address, address_id)
    if not db_address:
        return False
    db.delete(db_address)
    db.commit()
    return True
