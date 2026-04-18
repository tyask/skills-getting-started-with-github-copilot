"""
Comprehensive test suite for Mergington High School Activities API.

Tests cover:
- Integration tests for all 4 endpoints (GET /, GET /activities, POST /signup, DELETE /unregister)
- Unit tests for validation logic
- Success and error scenarios
- State verification
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Provide a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test."""
    # Reset the activities dictionary to known state
    from src import app as app_module
    
    initial_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball league and training",
            "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis skills and participate in matches",
            "schedule": "Wednesdays and Saturdays, 10:00 AM - 11:30 AM",
            "max_participants": 10,
            "participants": ["jessica@mergington.edu", "david@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in theater productions and develop acting skills",
            "schedule": "Tuesdays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["rachel@mergington.edu", "alex@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and sculpture techniques",
            "schedule": "Mondays and Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["maya@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop argumentation and public speaking skills through competitive debate",
            "schedule": "Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["christopher@mergington.edu", "lauren@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["noah@mergington.edu", "ava@mergington.edu"]
        }
    }
    
    # Clear and reset the activities dictionary
    app_module.activities.clear()
    app_module.activities.update(initial_activities)
    
    yield
    
    # Clean up after test
    app_module.activities.clear()
    app_module.activities.update(initial_activities)


# ============================================================================
# INTEGRATION TESTS FOR GET / (Root Redirect)
# ============================================================================

class TestRootEndpoint:
    """Test suite for GET / endpoint."""
    
    def test_root_redirect_returns_307(self, client, reset_activities):
        """Test that root endpoint returns 307 redirect status."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
    
    def test_root_redirect_location(self, client, reset_activities):
        """Test that root endpoint redirects to /static/index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.headers["location"] == "/static/index.html"


# ============================================================================
# INTEGRATION TESTS FOR GET /activities (List Activities)
# ============================================================================

class TestGetActivitiesEndpoint:
    """Test suite for GET /activities endpoint."""
    
    def test_get_activities_returns_200(self, client, reset_activities):
        """Test that /activities endpoint returns 200 OK."""
        response = client.get("/activities")
        assert response.status_code == 200
    
    def test_get_activities_returns_all_nine_activities(self, client, reset_activities):
        """Test that /activities returns all 9 activities."""
        response = client.get("/activities")
        activities = response.json()
        assert len(activities) == 9
    
    def test_get_activities_returns_correct_activity_names(self, client, reset_activities):
        """Test that /activities contains expected activity names."""
        response = client.get("/activities")
        activities = response.json()
        expected_names = [
            "Chess Club", "Programming Class", "Gym Class", "Basketball Team",
            "Tennis Club", "Drama Club", "Art Studio", "Debate Team", "Science Club"
        ]
        assert set(activities.keys()) == set(expected_names)
    
    def test_get_activities_has_correct_structure(self, client, reset_activities):
        """Test that each activity has required fields."""
        response = client.get("/activities")
        activities = response.json()
        
        required_fields = {"description", "schedule", "max_participants", "participants"}
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data, dict)
            assert required_fields.issubset(set(activity_data.keys()))
    
    def test_get_activities_participants_is_list(self, client, reset_activities):
        """Test that participants field is always a list."""
        response = client.get("/activities")
        activities = response.json()
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["participants"], list)
    
    def test_chess_club_initial_participants(self, client, reset_activities):
        """Test Chess Club has initial participants."""
        response = client.get("/activities")
        activities = response.json()
        chess = activities["Chess Club"]
        assert len(chess["participants"]) == 2
        assert "michael@mergington.edu" in chess["participants"]
        assert "daniel@mergington.edu" in chess["participants"]


# ============================================================================
# INTEGRATION TESTS FOR POST /signup (Student Signup)
# ============================================================================

class TestSignupEndpoint:
    """Test suite for POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_success_adds_participant(self, client, reset_activities):
        """Test that signup successfully adds new student to activity."""
        response = client.post(
            "/activities/Programming Class/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
    
    def test_signup_success_appears_in_activities_list(self, client, reset_activities):
        """Test that signed up student appears in subsequent GET request."""
        # Sign up new student
        signup_response = client.post(
            "/activities/Programming Class/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert signup_response.status_code == 200
        
        # Verify student appears in GET /activities
        get_response = client.get("/activities")
        activities = get_response.json()
        assert "newstudent@mergington.edu" in activities["Programming Class"]["participants"]
    
    def test_signup_invalid_activity_returns_404(self, client, reset_activities):
        """Test that signup to non-existent activity returns 404."""
        response = client.post(
            "/activities/Nonexistent Club/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_signup_duplicate_email_returns_400(self, client, reset_activities):
        """Test that signing up with already-enrolled email returns 400."""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}  # Already in Chess Club
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()
    
    def test_signup_activity_full_returns_400(self, client, reset_activities):
        """Test that signing up for full activity returns 400."""
        # Tennis Club has max 10 participants and already has 2
        # We need to fill it up to max first
        from src.app import activities
        
        # Fill Tennis Club to capacity
        tennis_club = activities["Tennis Club"]
        for i in range(tennis_club["max_participants"] - len(tennis_club["participants"])):
            tennis_club["participants"].append(f"student{i}@test.edu")
        
        # Now try to add one more
        response = client.post(
            "/activities/Tennis Club/signup",
            params={"email": "onemorestudent@merged.edu"}
        )
        assert response.status_code == 400
        assert "full" in response.json()["detail"].lower()
    
    def test_signup_missing_email_param_returns_error(self, client, reset_activities):
        """Test that signup without email parameter returns error."""
        response = client.post("/activities/Chess Club/signup")
        assert response.status_code >= 400  # Should be 422 validation error
    
    def test_signup_to_large_activity_succeeds(self, client, reset_activities):
        """Test signup succeeds for activity with large capacity."""
        # Gym Class has max 30 participants, should have room
        response = client.post(
            "/activities/Gym Class/signup",
            params={"email": "newgym@mergington.edu"}
        )
        assert response.status_code == 200
    
    def test_signup_multiple_students_to_same_activity(self, client, reset_activities):
        """Test multiple different students can sign up for same activity."""
        activity = "Drama Club"
        
        # Sign up first student
        response1 = client.post(
            f"/activities/{activity}/signup",
            params={"email": "student1@test.edu"}
        )
        assert response1.status_code == 200
        
        # Sign up second student
        response2 = client.post(
            f"/activities/{activity}/signup",
            params={"email": "student2@test.edu"}
        )
        assert response2.status_code == 200
        
        # Verify both appeared
        get_response = client.get("/activities")
        activities_list = get_response.json()
        assert "student1@test.edu" in activities_list[activity]["participants"]
        assert "student2@test.edu" in activities_list[activity]["participants"]


# ============================================================================
# INTEGRATION TESTS FOR DELETE /unregister (Student Unregister)
# ============================================================================

class TestUnregisterEndpoint:
    """Test suite for DELETE /activities/{activity_name}/unregister endpoint."""
    
    def test_unregister_success_removes_participant(self, client, reset_activities):
        """Test that unregister successfully removes student from activity."""
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
    
    def test_unregister_success_removed_from_activities_list(self, client, reset_activities):
        """Test that unregistered student no longer appears in GET /activities."""
        # Unregister student
        unregister_response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        assert unregister_response.status_code == 200
        
        # Verify student no longer in GET /activities
        get_response = client.get("/activities")
        activities = get_response.json()
        assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]
    
    def test_unregister_invalid_activity_returns_404(self, client, reset_activities):
        """Test that unregister from non-existent activity returns 404."""
        response = client.delete(
            "/activities/Nonexistent Club/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_unregister_non_enrolled_student_returns_400(self, client, reset_activities):
        """Test that unregistering non-enrolled student returns 400."""
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "notmember@mergington.edu"}
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"].lower()
    
    def test_unregister_from_activity_student_not_in_returns_400(self, client, reset_activities):
        """Test unregister fails for student not in that specific activity."""
        # michael is in Chess Club but not in Programming Class
        response = client.delete(
            "/activities/Programming Class/unregister",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"].lower()
    
    def test_unregister_missing_email_param_returns_error(self, client, reset_activities):
        """Test that unregister without email parameter returns error."""
        response = client.delete("/activities/Chess Club/unregister")
        assert response.status_code >= 400  # Should be 422 validation error
    
    def test_unregister_reduces_participant_count(self, client, reset_activities):
        """Test that unregister reduces participant count by 1."""
        # Get initial count
        get1 = client.get("/activities")
        initial_count = len(get1.json()["Debate Team"]["participants"])
        
        # Unregister a student
        client.delete(
            "/activities/Debate Team/unregister",
            params={"email": "christopher@mergington.edu"}
        )
        
        # Get updated count
        get2 = client.get("/activities")
        updated_count = len(get2.json()["Debate Team"]["participants"])
        
        assert updated_count == initial_count - 1


# ============================================================================
# INTEGRATION TESTS FOR SIGNUP/UNREGISTER STATE FLOW
# ============================================================================

class TestSignupUnregisterFlow:
    """Test complete signup and unregister state flows."""
    
    def test_signup_then_unregister_full_flow(self, client, reset_activities):
        """Test full flow: signup, verify in list, unregister, verify removed."""
        test_email = "flowtest@mergington.edu"
        activity = "Science Club"
        
        # Step 1: Signup
        signup_resp = client.post(
            f"/activities/{activity}/signup",
            params={"email": test_email}
        )
        assert signup_resp.status_code == 200
        
        # Step 2: Verify in list
        get1 = client.get("/activities")
        assert test_email in get1.json()[activity]["participants"]
        
        # Step 3: Unregister
        unreg_resp = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": test_email}
        )
        assert unreg_resp.status_code == 200
        
        # Step 4: Verify removed
        get2 = client.get("/activities")
        assert test_email not in get2.json()[activity]["participants"]
    
    def test_signup_unregister_multiple_activities_independent(self, client, reset_activities):
        """Test signup/unregister operations on different activities are independent."""
        test_email = "multi@mergington.edu"
        
        # Sign up for two activities
        client.post("/activities/Chess Club/signup", params={"email": test_email})
        client.post("/activities/Drama Club/signup", params={"email": test_email})
        
        # Verify in both
        get1 = client.get("/activities")
        assert test_email in get1.json()["Chess Club"]["participants"]
        assert test_email in get1.json()["Drama Club"]["participants"]
        
        # Unregister from Chess Club only
        client.delete("/activities/Chess Club/unregister", params={"email": test_email})
        
        # Verify removed from Chess Club but not Drama Club
        get2 = client.get("/activities")
        assert test_email not in get2.json()["Chess Club"]["participants"]
        assert test_email in get2.json()["Drama Club"]["participants"]
    
    def test_signup_after_unregister_readdition(self, client, reset_activities):
        """Test student can sign up again after being unregistered."""
        test_email = "retest@mergington.edu"
        activity = "Art Studio"
        
        # Sign up
        client.post(f"/activities/{activity}/signup", params={"email": test_email})
        get1 = client.get("/activities")
        assert test_email in get1.json()[activity]["participants"]
        
        # Unregister
        client.delete(f"/activities/{activity}/unregister", params={"email": test_email})
        get2 = client.get("/activities")
        assert test_email not in get2.json()[activity]["participants"]
        
        # Sign up again
        response = client.post(f"/activities/{activity}/signup", params={"email": test_email})
        assert response.status_code == 200
        get3 = client.get("/activities")
        assert test_email in get3.json()[activity]["participants"]


# ============================================================================
# UNIT TESTS FOR VALIDATION LOGIC
# ============================================================================

class TestValidationLogic:
    """Unit tests for validation and business logic."""
    
    def test_participant_list_maintains_order(self, client, reset_activities):
        """Test that participant list maintains insertion order."""
        from src.app import activities
        
        activity = activities["Programming Class"]
        initial_participants = activity["participants"].copy()
        
        # Add a new participant
        client.post(
            "/activities/Programming Class/signup",
            params={"email": "ordered@test.edu"}
        )
        
        get_response = client.get("/activities")
        updated_participants = get_response.json()["Programming Class"]["participants"]
        
        # Check new participant is appended (not inserted randomly)
        assert updated_participants[-1] == "ordered@test.edu"
    
    def test_email_parameter_is_case_sensitive(self, client, reset_activities):
        """Test that email parameters are treated case-sensitively."""
        # Sign up with lowercase
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newperson@test.edu"}
        )
        assert response1.status_code == 200
        
        # Try to sign up with different case - should succeed (different email)
        response2 = client.post(
            "/activities/Chess Club/signup",
            params={"email": "NewPerson@test.edu"}
        )
        assert response2.status_code == 200  # Should succeed as different string
    
    def test_max_participants_constraint(self, client, reset_activities):
        """Test that max_participants constraint is properly enforced."""
        from src.app import activities
        
        # Find an activity with small max_participants
        tennis = activities["Tennis Club"]
        max_cap = tennis["max_participants"]
        current_count = len(tennis["participants"])
        
        # Fill remaining slots
        for i in range(max_cap - current_count):
            response = client.post(
                "/activities/Tennis Club/signup",
                params={"email": f"filler{i}@test.edu"}
            )
            assert response.status_code == 200
        
        # One more should fail
        response = client.post(
            "/activities/Tennis Club/signup",
            params={"email": "shouldfail@test.edu"}
        )
        assert response.status_code == 400
        assert "full" in response.json()["detail"].lower()
    
    def test_participant_removal_actually_removes(self, client, reset_activities):
        """Test that participant removal actually deletes the entry, not just marks it."""
        test_email = "testremoval@test.edu"
        activity = "Gym Class"
        
        # Add participant
        client.post(f"/activities/{activity}/signup", params={"email": test_email})
        get1 = client.get("/activities")
        count_with_student = len(get1.json()[activity]["participants"])
        
        # Remove participant
        client.delete(f"/activities/{activity}/unregister", params={"email": test_email})
        get2 = client.get("/activities")
        count_without_student = len(get2.json()[activity]["participants"])
        
        # Verify actual removal
        assert count_without_student == count_with_student - 1
        assert get2.json()[activity]["participants"].count(test_email) == 0
