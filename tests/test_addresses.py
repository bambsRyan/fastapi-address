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
