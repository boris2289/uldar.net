import pytest


@pytest.mark.django_db
class TestListTags:
    url = "/api/tags/list"

    def test_list_tags_success(self, api_client, tag):
        response = api_client.get(self.url)
        assert response.status_code == 200
        assert len(response.data) >= 1

    def test_list_tags_empty(self, api_client):
        response = api_client.get(self.url)
        assert response.status_code == 200
        assert response.data == []

    def test_list_tags_wrong_method(self, api_client):
        response = api_client.post(self.url, {})
        assert response.status_code == 401 # unauthenticated


@pytest.mark.django_db
class TestCreateTag:
    url = "/api/tags/create"

    def test_create_tag_success(self, auth_client):
        response = auth_client.post(self.url, {"name": "Django"})
        assert response.status_code == 201
        assert response.data["name"] == "Django"
        assert response.data["slug"] == "django"

    def test_create_tag_unauthenticated(self, api_client):
        response = api_client.post(self.url, {"name": "Django"})
        assert response.status_code == 401

    def test_create_tag_missing_name(self, auth_client):
        response = auth_client.post(self.url, {})
        assert response.status_code == 400


@pytest.mark.django_db
class TestRetrieveTag:
    def test_retrieve_tag_success(self, api_client, tag, question):
        response = api_client.get(f"/api/tags/{tag.slug}/retrieve")
        assert response.status_code == 200
        assert response.data["tag"]["slug"] == tag.slug
        assert "questions" in response.data

    def test_retrieve_tag_not_found(self, api_client):
        response = api_client.get("/api/tags/nonexistent-slug/retrieve")
        assert response.status_code == 404

    def test_retrieve_tag_wrong_method(self, api_client, tag):
        response = api_client.post(f"/api/tags/{tag.slug}/retrieve", {})
        assert response.status_code == 405 # POST is not allowed (405)