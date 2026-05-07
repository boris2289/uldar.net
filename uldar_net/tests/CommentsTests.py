import pytest


@pytest.mark.django_db
class TestListComments:
    url = "/api/comments/list"

    def test_list_comments_success(self, api_client, comment):
        response = api_client.get(self.url)
        assert response.status_code == 200
        assert len(response.data) >= 1

    def test_list_comments_empty(self, api_client):
        response = api_client.get(self.url)
        assert response.status_code == 200
        assert response.data == []

    def test_list_comments_wrong_method(self, api_client):
        response = api_client.delete(self.url)
        assert response.status_code == 405


@pytest.mark.django_db
class TestCreateComment:
    url = "/api/comments/create"

    def test_create_comment_success(self, auth_client, question):
        response = auth_client.post(self.url, {
            "text": "This is a new comment.",
            "question": question.id,
        })
        assert response.status_code == 201
        assert response.data["text"] == "This is a new comment."

    def test_create_comment_unauthenticated(self, api_client, question):
        response = api_client.post(self.url, {
            "text": "This is a new comment.",
            "question": question.id,
        })
        assert response.status_code == 401

    def test_create_comment_missing_text(self, auth_client, question):
        response = auth_client.post(self.url, {
            "question": question.id,
        })
        assert response.status_code == 400


@pytest.mark.django_db
class TestUpdateComment:
    def test_update_comment_success(self, auth_client, comment):
        response = auth_client.patch(f"/api/comments/{comment.id}/update", {
            "text": "Updated comment text."
        })
        assert response.status_code == 200
        assert response.data["data"]["text"] == "Updated comment text."

    def test_update_comment_not_author(self, another_auth_client, comment):
        response = another_auth_client.patch(f"/api/comments/{comment.id}/update", {
            "text": "Hacked comment."
        })
        assert response.status_code == 403

    def test_update_comment_not_found(self, auth_client):
        response = auth_client.patch("/api/comments/99999/update", {
            "text": "Updated comment text."
        })
        assert response.status_code == 404


@pytest.mark.django_db
class TestListCommentsByAuthor:
    url = "/api/comments/list_by_author"

    def test_list_by_author_success(self, api_client, user, comment):
        response = api_client.get(self.url, {"author": user.id})
        assert response.status_code == 200
        assert len(response.data) >= 1

    def test_list_by_author_no_comments(self, api_client, another_user):
        response = api_client.get(self.url, {"author": another_user.id})
        assert response.status_code == 200
        assert response.data == []

    def test_list_by_author_missing_param(self, api_client):
        response = api_client.get(self.url)
        assert response.status_code == 400