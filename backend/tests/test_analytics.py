"""Unit and integration tests for analytics and Product Hunt launch tracking."""

from fastapi.testclient import TestClient


def test_track_visit_direct(client: TestClient):
    """Test tracking a direct visit."""
    payload = {
        "visitor_id": "test_vis_123",
        "source": "direct",
        "path": "/",
    }
    response = client.post("/api/v1/analytics/track", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["recorded"] is True
    assert data["data"]["source"] == "direct"


def test_track_visit_product_hunt_ref(client: TestClient):
    """Test tracking a visit coming from Product Hunt via query param ?ref=producthunt."""
    payload = {
        "visitor_id": "test_vis_ph_1",
        "ref": "producthunt",
        "path": "/",
    }
    response = client.post("/api/v1/analytics/track", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["recorded"] is True
    assert data["data"]["source"] == "producthunt"


def test_track_visit_product_hunt_referrer(client: TestClient):
    """Test tracking a visit with producthunt.com in referrer."""
    payload = {
        "visitor_id": "test_vis_ph_2",
        "referrer": "https://www.producthunt.com/posts/itr-taxpilot",
        "path": "/",
    }
    response = client.post("/api/v1/analytics/track", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["source"] == "producthunt"


def test_track_visit_github_source(client: TestClient):
    """Test tracking a visit coming from GitHub."""
    payload = {
        "visitor_id": "test_vis_gh_1",
        "ref": "github",
        "path": "/",
    }
    response = client.post("/api/v1/analytics/track", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["source"] == "github"


def test_get_analytics_stats(client: TestClient):
    """Test fetching aggregated launch statistics."""
    # Track one PH visit first
    client.post(
        "/api/v1/analytics/track",
        json={"visitor_id": "ph_user_99", "utm_source": "producthunt", "path": "/"},
    )

    response = client.get("/api/v1/analytics/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "total_visits" in data["data"]
    assert "product_hunt_visits" in data["data"]
    assert data["data"]["product_hunt_visits"] >= 1
    assert "github_stats" in data["data"]
    assert data["data"]["github_stats"]["repo"] == "thakuratul2/ITR-TaxPilot"


def test_get_github_stars(client: TestClient):
    """Test getting GitHub stars endpoint."""
    response = client.get("/api/v1/analytics/github-stars")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["repo"] == "thakuratul2/ITR-TaxPilot"
    assert isinstance(data["data"]["stars"], int)
