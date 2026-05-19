ADDRESS_PAYLOAD = {
    "name": "Home",
    "street": "123 Main St",
    "city": "Manila",
    "country": "Philippines",
    "latitude": 14.5995,
    "longitude": 120.9842,
}


def test_create_address(client):
    response = client.post("/api/v1/addresses/", json={
        "name": "Home",
        "street": "123 Main St",
        "city": "Manila",
        "country": "Philippines",
        "latitude": 14.5995,
        "longitude": 120.9842,
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Home"
    assert data["street"] == "123 Main St"
    assert data["city"] == "Manila"
    assert data["country"] == "Philippines"
    assert data["latitude"] == 14.5995
    assert data["longitude"] == 120.9842
    assert "id" in data


def test_proximity_search_returns_results(client):
    client.post("/api/v1/addresses/", json=ADDRESS_PAYLOAD)
    response = client.get("/api/v1/addresses/", params={
        "latitude": 14.5995, "longitude": 120.9842, "radius_km": 1,
    })
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_proximity_search_partial_params_returns_422(client):
    response = client.get("/api/v1/addresses/", params={"latitude": 14.5995, "radius_km": 1})
    assert response.status_code == 422
