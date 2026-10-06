import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture
def client():
    original_activities = {
        name: {
            key: value[:] if isinstance(value, list) else value
            for key, value in activity.items()
        }
        for name, activity in activities.items()
    }

    activities.clear()
    activities.update(
        {
            name: {
                key: value[:] if isinstance(value, list) else value
                for key, value in activity.items()
            }
            for name, activity in original_activities.items()
        }
    )

    yield TestClient(app)

    activities.clear()
    activities.update(original_activities)


def test_get_activities_returns_all_activities(client):
    # Arrange
    # Using the seeded activity list from the app.

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert "Programming Class" in payload
    assert "Gym Class" in payload


def test_signup_for_activity_adds_email_to_participants(client):
    # Arrange
    activity_name = "Basketball Team"
    student_email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={student_email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {student_email} for {activity_name}"
    assert student_email in activities[activity_name]["participants"]


def test_signup_for_activity_rejects_duplicate_registration(client):
    # Arrange
    activity_name = "Chess Club"
    student_email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={student_email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_for_unknown_activity_returns_404(client):
    # Arrange
    activity_name = "Does Not Exist"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email=student@mergington.edu")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_participant_removes_email_from_activity(client):
    # Arrange
    activity_name = "Chess Club"
    student_email = "michael@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{student_email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {student_email} from {activity_name}"
    assert student_email not in activities[activity_name]["participants"]


def test_unregister_participant_for_non_member_returns_404(client):
    # Arrange
    activity_name = "Chess Club"
    student_email = "notregistered@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{student_email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
