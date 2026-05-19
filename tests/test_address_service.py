import pytest
from sqlmodel import Session

from app.models.address import AddressCreate
from app.services import address as address_service

# Manila city hall — used as the base for proximity tests
ADDRESS_DATA = AddressCreate(
    name="Home",
    street="123 Main St",
    city="Manila",
    country="Philippines",
    latitude=14.5995,
    longitude=120.9842,
)

# ~158m away from ADDRESS_DATA
NEARBY = ADDRESS_DATA.model_copy(update={"name": "Nearby", "latitude": 14.6007, "longitude": 120.9850})

# New York — ~13,700km from Manila
FAR_AWAY = ADDRESS_DATA.model_copy(update={"name": "Far Away", "latitude": 40.7128, "longitude": -74.0060})


def test_create_address(db: Session):
    address = address_service.create(db, ADDRESS_DATA)
    assert address.id is not None
    assert address.name == "Home"
    assert address.city == "Manila"


def test_search_no_filters_returns_all(db: Session):
    address_service.create(db, ADDRESS_DATA)
    address_service.create(db, ADDRESS_DATA.model_copy(update={"name": "Office"}))
    results = address_service.search(db)
    assert len(results) == 2


def test_search_by_name(db: Session):
    address_service.create(db, ADDRESS_DATA)
    address_service.create(db, ADDRESS_DATA.model_copy(update={"name": "Office"}))
    results = address_service.search(db, name="off")
    assert len(results) == 1
    assert results[0].name == "Office"


def test_search_by_city(db: Session):
    address_service.create(db, ADDRESS_DATA)
    address_service.create(db, ADDRESS_DATA.model_copy(update={"name": "Office", "city": "Cebu"}))
    results = address_service.search(db, city="cebu")
    assert len(results) == 1
    assert results[0].city == "Cebu"


def test_search_by_country(db: Session):
    address_service.create(db, ADDRESS_DATA)
    address_service.create(db, ADDRESS_DATA.model_copy(update={"name": "Office", "country": "Japan"}))
    results = address_service.search(db, country="japan")
    assert len(results) == 1
    assert results[0].country == "Japan"


def test_search_by_street(db: Session):
    address_service.create(db, ADDRESS_DATA)
    address_service.create(db, ADDRESS_DATA.model_copy(update={"name": "Office", "street": "456 Rizal Ave"}))
    results = address_service.search(db, street="rizal")
    assert len(results) == 1
    assert results[0].street == "456 Rizal Ave"


def test_search_multiple_filters(db: Session):
    address_service.create(db, ADDRESS_DATA)
    address_service.create(db, ADDRESS_DATA.model_copy(update={"name": "Office", "city": "Cebu"}))
    results = address_service.search(db, name="office", city="cebu")
    assert len(results) == 1
    assert results[0].name == "Office"


def test_search_no_match_returns_empty(db: Session):
    address_service.create(db, ADDRESS_DATA)
    results = address_service.search(db, city="Tokyo")
    assert results == []


def test_proximity_returns_addresses_within_radius(db: Session):
    address_service.create(db, ADDRESS_DATA)   # Home — at center
    address_service.create(db, NEARBY)          # ~158m away
    address_service.create(db, FAR_AWAY)        # ~13,700km away
    results = address_service.search(db, latitude=14.5995, longitude=120.9842, radius_km=1)
    names = {r.name for r in results}
    assert "Home" in names
    assert "Nearby" in names
    assert "Far Away" not in names


def test_proximity_excludes_addresses_outside_radius(db: Session):
    address_service.create(db, ADDRESS_DATA)  # Home — at center
    address_service.create(db, NEARBY)         # ~158m away
    results = address_service.search(db, latitude=14.5995, longitude=120.9842, radius_km=0.1)
    assert len(results) == 1
    assert results[0].name == "Home"


def test_proximity_no_results_when_all_far(db: Session):
    address_service.create(db, ADDRESS_DATA)
    results = address_service.search(db, latitude=40.7128, longitude=-74.0060, radius_km=1)
    assert results == []


def test_proximity_combined_with_text_filter(db: Session):
    address_service.create(db, ADDRESS_DATA)   # Home — within radius
    address_service.create(db, NEARBY)          # Nearby — within radius
    results = address_service.search(db, name="home", latitude=14.5995, longitude=120.9842, radius_km=1)
    assert len(results) == 1
    assert results[0].name == "Home"


def test_update_address(db: Session):
    created = address_service.create(db, ADDRESS_DATA)
    updated_data = ADDRESS_DATA.model_copy(update={"name": "Office", "city": "Cebu"})
    updated = address_service.update(db, created.id, updated_data)
    assert updated is not None
    assert updated.name == "Office"
    assert updated.city == "Cebu"


def test_update_address_not_found(db: Session):
    result = address_service.update(db, 999, ADDRESS_DATA)
    assert result is None


def test_delete_address(db: Session):
    created = address_service.create(db, ADDRESS_DATA)
    deleted = address_service.delete(db, created.id)
    assert deleted is True
    assert address_service.search(db, name=created.name) == []


def test_delete_address_not_found(db: Session):
    result = address_service.delete(db, 999)
    assert result is False


def test_latitude_validation():
    with pytest.raises(Exception):
        AddressCreate(**ADDRESS_DATA.model_dump() | {"latitude": 91.0})


def test_longitude_validation():
    with pytest.raises(Exception):
        AddressCreate(**ADDRESS_DATA.model_dump() | {"longitude": -181.0})
