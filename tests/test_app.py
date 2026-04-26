"""
Comprehensive tests for the Mergington High School Activities API
Following the AAA (Arrange-Act-Assert) pattern for test structure
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_success(self, client):
        """
        ARRANGE: No explicit setup needed
        ACT: Make GET request to /activities
        ASSERT: Verify response status and structure
        """
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        assert isinstance(response.json(), dict)

    def test_get_activities_includes_all_activities(self, client):
        """
        ARRANGE: No setup needed (default activities are loaded)
        ACT: Fetch all activities
        ASSERT: Verify all activities are present
        """
        # Act
        response = client.get("/activities")
        activities_data = response.json()

        # Assert
        assert "Chess Club" in activities_data
        assert "Programming Class" in activities_data
        assert "Gym Class" in activities_data

    def test_get_activities_includes_required_fields(self, client):
        """
        ARRANGE: No setup needed
        ACT: Fetch activities
        ASSERT: Verify each activity has required fields (description, schedule, max_participants, participants)
        """
        # Act
        response = client.get("/activities")
        activities_data = response.json()

        # Assert
        for activity_name, activity_details in activities_data.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_successful_for_new_student(self, client):
        """
        ARRANGE: Prepare an email for a new student
        ACT: Sign up the student for Chess Club
        ASSERT: Verify response indicates success
        """
        # Arrange
        new_email = "newstudent@mergington.edu"
        activity_name = "Chess Club"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={new_email}"
        )

        # Assert
        assert response.status_code == 200
        assert "message" in response.json()
        assert new_email in response.json()["message"]

    def test_signup_adds_participant_to_activity(self, client):
        """
        ARRANGE: Prepare a new student email
        ACT: Sign up the student and then fetch activities
        ASSERT: Verify participant list includes the new student
        """
        # Arrange
        new_email = "alice@mergington.edu"
        activity_name = "Programming Class"

        # Act
        client.post(f"/activities/{activity_name}/signup?email={new_email}")
        response = client.get("/activities")

        # Assert
        participants = response.json()[activity_name]["participants"]
        assert new_email in participants

    def test_signup_fails_for_nonexistent_activity(self, client):
        """
        ARRANGE: Prepare an email and a non-existent activity name
        ACT: Try to sign up for fake activity
        ASSERT: Verify response includes 404 error
        """
        # Arrange
        email = "student@mergington.edu"
        fake_activity = "Nonexistent Club"

        # Act
        response = client.post(
            f"/activities/{fake_activity}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_fails_for_duplicate_registration(self, client):
        """
        ARRANGE: Pick an already-registered student and activity
        ACT: Try to sign up the same student again
        ASSERT: Verify response indicates already signed up
        """
        # Arrange
        email = "michael@mergington.edu"  # Already in Chess Club
        activity_name = "Chess Club"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_with_special_characters_in_email(self, client):
        """
        ARRANGE: Prepare an email with special characters and proper URL encoding
        ACT: Sign up with special character email using proper encoding
        ASSERT: Verify signup succeeds with correct encoding
        """
        # Arrange
        import urllib.parse
        email = "student+test@mergington.edu"
        activity_name = "Drama Club"
        encoded_email = urllib.parse.quote(email)

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={encoded_email}"
        )

        # Assert
        assert response.status_code == 200
        assert email in response.json()["message"]

    def test_signup_multiple_students_to_same_activity(self, client):
        """
        ARRANGE: Prepare multiple student emails
        ACT: Sign up multiple students to the same activity
        ASSERT: Verify all are added to participants list
        """
        # Arrange
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        activity_name = "Art Studio"

        # Act
        for email in emails:
            client.post(f"/activities/{activity_name}/signup?email={email}")

        response = client.get("/activities")

        # Assert
        participants = response.json()[activity_name]["participants"]
        for email in emails:
            assert email in participants


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_successful_for_registered_student(self, client):
        """
        ARRANGE: Pick a student already registered in an activity
        ACT: Unregister the student
        ASSERT: Verify response indicates success
        """
        # Arrange
        email = "michael@mergington.edu"  # Already in Chess Club
        activity_name = "Chess Club"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # Assert
        assert response.status_code == 200
        assert "message" in response.json()

    def test_unregister_removes_participant_from_activity(self, client):
        """
        ARRANGE: Pick a registered student
        ACT: Unregister and fetch activities
        ASSERT: Verify participant is removed from list
        """
        # Arrange
        email = "emma@mergington.edu"  # Already in Programming Class
        activity_name = "Programming Class"

        # Act
        client.delete(f"/activities/{activity_name}/unregister?email={email}")
        response = client.get("/activities")

        # Assert
        participants = response.json()[activity_name]["participants"]
        assert email not in participants

    def test_unregister_fails_for_nonexistent_activity(self, client):
        """
        ARRANGE: Prepare an email and fake activity name
        ACT: Try to unregister from fake activity
        ASSERT: Verify 404 error
        """
        # Arrange
        email = "student@mergington.edu"
        fake_activity = "Ghost Club"

        # Act
        response = client.delete(
            f"/activities/{fake_activity}/unregister?email={email}"
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_fails_for_non_registered_student(self, client):
        """
        ARRANGE: Prepare an email not registered in an activity
        ACT: Try to unregister someone not signed up
        ASSERT: Verify error response
        """
        # Arrange
        email = "unknown@mergington.edu"
        activity_name = "Chess Club"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # Assert
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]

    def test_unregister_then_signup_again(self, client):
        """
        ARRANGE: Pick a registered student
        ACT: Unregister then sign up again
        ASSERT: Verify student is back in participants list
        """
        # Arrange
        email = "alex@mergington.edu"  # Already in Tennis Club
        activity_name = "Tennis Club"

        # Act - unregister
        client.delete(f"/activities/{activity_name}/unregister?email={email}")

        # Act - verify removed
        response_after_unregister = client.get("/activities")
        assert email not in response_after_unregister.json()[activity_name]["participants"]

        # Act - sign up again
        client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert - verify back in list
        response_after_signup = client.get("/activities")
        assert email in response_after_signup.json()[activity_name]["participants"]


class TestIntegrationScenarios:
    """Integration tests combining multiple operations"""

    def test_participant_count_updates_correctly(self, client):
        """
        ARRANGE: Get initial participant count
        ACT: Sign up new student and check count
        ASSERT: Verify count increased by 1
        """
        # Arrange
        activity_name = "Science Club"
        new_email = "newparticipant@mergington.edu"

        response_before = client.get("/activities")
        count_before = len(response_before.json()[activity_name]["participants"])

        # Act
        client.post(f"/activities/{activity_name}/signup?email={new_email}")
        response_after = client.get("/activities")

        # Assert
        count_after = len(response_after.json()[activity_name]["participants"])
        assert count_after == count_before + 1

    def test_signup_unregister_cycle_maintains_data_integrity(self, client):
        """
        ARRANGE: Pick an activity and new student
        ACT: Sign up → verify → unregister → verify → sign up again
        ASSERT: Activity maintains data integrity throughout
        """
        # Arrange
        activity_name = "Debate Team"
        email = "debate.student@mergington.edu"

        # Act & Assert - signup
        response_signup = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        assert response_signup.status_code == 200

        response_check1 = client.get("/activities")
        assert email in response_check1.json()[activity_name]["participants"]

        # Act & Assert - unregister
        response_unregister = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        assert response_unregister.status_code == 200

        response_check2 = client.get("/activities")
        assert email not in response_check2.json()[activity_name]["participants"]

        # Act & Assert - signup again
        response_signup2 = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        assert response_signup2.status_code == 200

        response_check3 = client.get("/activities")
        assert email in response_check3.json()[activity_name]["participants"]

    def test_multiple_concurrent_signups(self, client):
        """
        ARRANGE: Prepare multiple unique emails
        ACT: Sign up multiple students to various activities
        ASSERT: Verify all signups succeeded and data is consistent
        """
        # Arrange
        operations = [
            ("Basketball Team", "player1@mergington.edu"),
            ("Basketball Team", "player2@mergington.edu"),
            ("Tennis Club", "player3@mergington.edu"),
            ("Drama Club", "actor1@mergington.edu"),
        ]

        # Act & Assert - all signups succeed
        for activity_name, email in operations:
            response = client.post(
                f"/activities/{activity_name}/signup?email={email}"
            )
            assert response.status_code == 200

        # Assert - verify all were added
        response = client.get("/activities")
        activities_data = response.json()

        assert "player1@mergington.edu" in activities_data["Basketball Team"]["participants"]
        assert "player2@mergington.edu" in activities_data["Basketball Team"]["participants"]
        assert "player3@mergington.edu" in activities_data["Tennis Club"]["participants"]
        assert "actor1@mergington.edu" in activities_data["Drama Club"]["participants"]
