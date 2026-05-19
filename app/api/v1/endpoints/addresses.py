from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.database import get_db
from app.models.address import AddressCreate, AddressRead
from app.services import address as address_service

router = APIRouter(prefix="/addresses", tags=["addresses"])


@router.post("/", response_model=AddressRead, status_code=201)
def create_address(address: AddressCreate, db: Session = Depends(get_db)):
    """Create a new address entry.

    Validates latitude (-90 to 90) and longitude (-180 to 180) before saving.
    Returns the created address with its generated id.
    """
    return address_service.create(db, address)


@router.get("/", response_model=list[AddressRead])
def list_addresses(
    name: Optional[str] = None,
    street: Optional[str] = None,
    city: Optional[str] = None,
    country: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    radius_km: Optional[float] = None,
    db: Session = Depends(get_db),
):
    """Search addresses using optional query parameters.

    Text filters (name, street, city, country) are case-insensitive partial
    matches. Proximity search requires all three of latitude, longitude, and
    radius_km — returns addresses within that radius (in km) of the given point.
    All filters can be freely combined.

    - **name**: partial match on address name
    - **street**: partial match on street
    - **city**: partial match on city
    - **country**: partial match on country
    - **latitude**: center point latitude for proximity search
    - **longitude**: center point longitude for proximity search
    - **radius_km**: search radius in kilometres
    """
    proximity = [latitude, longitude, radius_km]
    if any(p is not None for p in proximity) and not all(p is not None for p in proximity):
        raise HTTPException(
            status_code=422,
            detail="latitude, longitude, and radius_km must all be provided together",
        )
    return address_service.search(
        db, name=name, street=street, city=city, country=country,
        latitude=latitude, longitude=longitude, radius_km=radius_km,
    )


@router.patch("/{address_id}", response_model=AddressRead)
def update_address(address_id: int, address: AddressCreate, db: Session = Depends(get_db)):
    """Replace all fields on an existing address.

    Requires a full address body — all fields must be provided.
    Returns 404 if the address does not exist.
    """
    updated = address_service.update(db, address_id, address)
    if not updated:
        raise HTTPException(status_code=404, detail="Address not found")
    return updated


@router.delete("/{address_id}", status_code=204)
def delete_address(address_id: int, db: Session = Depends(get_db)):
    """Delete an address by id.

    Returns 204 on success, 404 if the address does not exist.
    """
    if not address_service.delete(db, address_id):
        raise HTTPException(status_code=404, detail="Address not found")
