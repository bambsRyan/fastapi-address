import logging

from geopy.distance import geodesic
from sqlmodel import Session, select

from app.models.address import Address, AddressCreate, AddressUpdate

logger = logging.getLogger(__name__)


def create(db: Session, address: AddressCreate) -> Address:
    """Persist a new address to the database and return it with its generated id."""
    db_address = Address.model_validate(address)
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    logger.info(f"Address created: id={db_address.id} name='{db_address.name}'")
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
    sort_by: str = "id",
    sort_order: str = "asc",
    skip: int = 0,
    limit: int = 10,
) -> tuple[list[Address], int]:
    """Return a paginated, sorted slice of addresses matching all provided filters.

    Text filters are case-insensitive partial matches. Proximity filter requires
    latitude, longitude, and radius_km together. Sorting is applied at the database
    level; proximity filtering and pagination are applied afterwards in Python so
    that the total count reflects all matching records before slicing.

    Returns a (items, total) tuple where total is the count before pagination.
    """
    sort_col = getattr(Address, sort_by)
    order = sort_col.asc() if sort_order == "asc" else sort_col.desc()

    query = select(Address).order_by(order)
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
        before = len(addresses)
        addresses = [
            a for a in addresses
            if geodesic((latitude, longitude), (a.latitude, a.longitude)).km <= radius_km
        ]
        logger.info(
            f"Proximity filter: {len(addresses)}/{before} addresses within "
            f"{radius_km}km of ({latitude}, {longitude})"
        )

    total = len(addresses)
    logger.info(f"Search returned {total} result(s) (sort={sort_by} {sort_order}, skip={skip}, limit={limit})")
    return addresses[skip: skip + limit], total


def update(db: Session, address_id: int, address: AddressUpdate) -> Address | None:
    """Partially update an existing address. Only fields included in the request are changed.

    Uses exclude_unset=True so omitted fields are left as-is on the stored record.
    Returns None if the address does not exist.
    """
    db_address = db.get(Address, address_id)
    if not db_address:
        logger.warning(f"Update failed: address id={address_id} not found")
        return None
    fields = address.model_dump(exclude_unset=True)
    for key, value in fields.items():
        setattr(db_address, key, value)
    db.commit()
    db.refresh(db_address)
    logger.info(f"Address updated: id={address_id} fields={list(fields.keys())}")
    return db_address


def delete(db: Session, address_id: int) -> bool:
    """Delete an address by id. Returns True if deleted, False if not found."""
    db_address = db.get(Address, address_id)
    if not db_address:
        logger.warning(f"Delete failed: address id={address_id} not found")
        return False
    db.delete(db_address)
    db.commit()
    logger.info(f"Address deleted: id={address_id}")
    return True
