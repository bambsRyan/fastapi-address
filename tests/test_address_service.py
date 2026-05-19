import pytest
from sqlmodel import Session

from app.models.address import AddressCreate
from app.services import address as address_service

ADDRESS_DATA = AddressCreate(
    name="Home",
    street="123 Main St",
    city="Manila",
    country="Philippines",
    latitude=14.5995,
    longitude=120.9842,
)

NEARBY = ADDRESS_DATA.model_copy(update={"name": "Nearby", "latitude": 14.6007, "longitude": 120.9850})
FAR_AWAY = ADDRESS_DATA.model_copy(update={"name": "Far Away", "latitude": 40.7128, "longitude": -74.0060})


def test_create_address(db: Session):
    address = address_service.create(db, ADDRESS_DATA)
    assert address.id is not None
    assert address.name == "Home"
    assert address.city == "Manila"


def test_search_no_filters_returns_all(db: Session):
    address_service.create(db, ADDRESS_DATA)
    address_service.create(db, ADDRESS_DATA.model_copy(update={"name": "Office"}))
    results, total = address_service.search(db, limit=100)
    assert total == 2
    assert len(results) == 2


def test_search_by_name(db: Session):
    address_service.create(db, ADDRESS_DATA)
    address_service.create(db, ADDRESS_DATA.model_copy(update={"name": "Office"}))
    results, total = address_service.search(db, name="off")
    assert total == 1
    assert results[0].name == "Office"


def test_search_by_city(db: Session):
    address_service.create(db, ADDRESS_DATA)
    address_service.create(db, ADDRESS_DATA.model_copy(update={"name": "Office", "city": "Cebu"}))
    results, total = address_service.search(db, city="cebu")
    assert total == 1
    assert results[0].city == "Cebu"


def test_search_by_country(db: Session):
    address_service.create(db, ADDRESS_DATA)
    address_service.create(db, ADDRESS_DATA.model_copy(update={"name": "Office", "country": "Japan"}))
    results, total = address_service.search(db, country="japan")
    assert total == 1
    assert results[0].country == "Japan"


def test_search_by_street(db: Session):
    address_service.create(db, ADDRESS_DATA)
    address_service.create(db, ADDRESS_DATA.model_copy(update={"name": "Office", "street": "456 Rizal Ave"}))
    results, total = address_service.search(db, street="rizal")
    assert total == 1
    assert results[0].street == "456 Rizal Ave"


def test_search_multiple_filters(db: Session):
    address_service.create(db, ADDRESS_DATA)
    address_service.create(db, ADDRESS_DATA.model_copy(update={"name": "Office", "city": "Cebu"}))
    results, total = address_service.search(db, name="office", city="cebu")
    assert total == 1
    assert results[0].name == "Office"


def test_search_no_match_returns_empty(db: Session):
    address_service.create(db, ADDRESS_DATA)
    results, total = address_service.search(db, city="Tokyo")
    assert total == 0
    assert results == []


def test_proximity_returns_addresses_within_radius(db: Session):
    address_service.create(db, ADDRESS_DATA)
    address_service.create(db, NEARBY)
    address_service.create(db, FAR_AWAY)
    results, total = address_service.search(db, latitude=14.5995, longitude=120.9842, radius_km=1, limit=100)
    names = {r.name for r in results}
    assert total == 2
    assert "Home" in names
    assert "Nearby" in names
    assert "Far Away" not in names


def test_proximity_excludes_addresses_outside_radius(db: Session):
    address_service.create(db, ADDRESS_DATA)
    address_service.create(db, NEARBY)
    results, total = address_service.search(db, latitude=14.5995, longitude=120.9842, radius_km=0.1)
    assert total == 1
    assert results[0].name == "Home"


def test_proximity_no_results_when_all_far(db: Session):
    address_service.create(db, ADDRESS_DATA)
    results, total = address_service.search(db, latitude=40.7128, longitude=-74.0060, radius_km=1)
    assert total == 0
    assert results == []


def test_proximity_combined_with_text_filter(db: Session):
    address_service.create(db, ADDRESS_DATA)
    address_service.create(db, NEARBY)
    results, total = address_service.search(db, name="home", latitude=14.5995, longitude=120.9842, radius_km=1)
    assert total == 1
    assert results[0].name == "Home"


def test_pagination_skip(db: Session):
    for i in range(5):
        address_service.create(db, ADDRESS_DATA.model_copy(update={"name": f"Address {i}"}))
    results, total = address_service.search(db, skip=2, limit=2)
    assert total == 5
    assert len(results) == 2


def test_pagination_limit(db: Session):
    for i in range(5):
        address_service.create(db, ADDRESS_DATA.model_copy(update={"name": f"Address {i}"}))
    results, total = address_service.search(db, limit=3)
    assert total == 5
    assert len(results) == 3


def test_sort_by_name_asc(db: Session):
    address_service.create(db, ADDRESS_DATA.model_copy(update={"name": "Zebra"}))
    address_service.create(db, ADDRESS_DATA.model_copy(update={"name": "Alpha"}))
    results, _ = address_service.search(db, sort_by="name", sort_order="asc", limit=100)
    assert results[0].name == "Alpha"
    assert results[1].name == "Zebra"


def test_sort_by_name_desc(db: Session):
    address_service.create(db, ADDRESS_DATA.model_copy(update={"name": "Zebra"}))
    address_service.create(db, ADDRESS_DATA.model_copy(update={"name": "Alpha"}))
    results, _ = address_service.search(db, sort_by="name", sort_order="desc", limit=100)
    assert results[0].name == "Zebra"
    assert results[1].name == "Alpha"


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
    results, total = address_service.search(db, name=created.name)
    assert total == 0


def test_delete_address_not_found(db: Session):
    result = address_service.delete(db, 999)
    assert result is False


def test_latitude_validation():
    with pytest.raises(Exception):
        AddressCreate(**ADDRESS_DATA.model_dump() | {"latitude": 91.0})


def test_longitude_validation():
    with pytest.raises(Exception):
        AddressCreate(**ADDRESS_DATA.model_dump() | {"longitude": -181.0})
