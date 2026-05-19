ADDRESS_PAYLOAD = {
    "name": "Home",
    "street": "123 Main St",
    "city": "Manila",
    "country": "Philippines",
    "latitude": 14.5995,
    "longitude": 120.9842,
}


def test_create_address(client):
    response = client.post("/api/v1/addresses/", json=ADDRESS_PAYLOAD)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Home"
    assert data["street"] == "123 Main St"
    assert data["city"] == "Manila"
    assert data["country"] == "Philippines"
    assert data["latitude"] == 14.5995
    assert data["longitude"] == 120.9842
    assert "id" in data


def test_list_returns_page_envelope(client):
    client.post("/api/v1/addresses/", json=ADDRESS_PAYLOAD)
    response = client.get("/api/v1/addresses/")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "skip" in data
    assert "limit" in data
    assert "data" in data
    assert data["total"] == 1
    assert len(data["data"]) == 1


def test_pagination(client):
    for i in range(5):
        client.post("/api/v1/addresses/", json={**ADDRESS_PAYLOAD, "name": f"Address {i}"})
    response = client.get("/api/v1/addresses/", params={"skip": 2, "limit": 2})
    data = response.json()
    assert data["total"] == 5
    assert len(data["data"]) == 2


def test_sort_by_name_desc(client):
    client.post("/api/v1/addresses/", json={**ADDRESS_PAYLOAD, "name": "Zebra"})
    client.post("/api/v1/addresses/", json={**ADDRESS_PAYLOAD, "name": "Alpha"})
    response = client.get("/api/v1/addresses/", params={"sort_by": "name", "sort_order": "desc", "limit": 100})
    data = response.json()["data"]
    assert data[0]["name"] == "Zebra"
    assert data[1]["name"] == "Alpha"


def test_proximity_search_returns_results(client):
    client.post("/api/v1/addresses/", json=ADDRESS_PAYLOAD)
    response = client.get("/api/v1/addresses/", params={
        "latitude": 14.5995, "longitude": 120.9842, "radius_km": 1,
    })
    assert response.status_code == 200
    assert response.json()["total"] == 1


def test_proximity_search_partial_params_returns_422(client):
    response = client.get("/api/v1/addresses/", params={"latitude": 14.5995, "radius_km": 1})
    assert response.status_code == 422


def test_patch_updates_only_provided_fields(client):
    created = client.post("/api/v1/addresses/", json=ADDRESS_PAYLOAD).json()
    response = client.patch(f"/api/v1/addresses/{created['id']}", json={"city": "Cebu"})
    assert response.status_code == 200
    data = response.json()
    assert data["city"] == "Cebu"
    assert data["name"] == ADDRESS_PAYLOAD["name"]
    assert data["street"] == ADDRESS_PAYLOAD["street"]


def test_update_nonexistent_address_returns_404(client):
    response = client.patch("/api/v1/addresses/999", json={"city": "Cebu"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Address not found"


def test_delete_nonexistent_address_returns_404(client):
    response = client.delete("/api/v1/addresses/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Address not found"


def test_unhandled_exception_returns_500(client, monkeypatch):
    from app.services import address as address_service

    def boom(*args, **kwargs):
        raise RuntimeError("Simulated unexpected failure")

    monkeypatch.setattr(address_service, "create", boom)
    response = client.post("/api/v1/addresses/", json=ADDRESS_PAYLOAD)
    assert response.status_code == 500
    assert response.json()["detail"] == "Internal server error"
