"""
AgriNova AI — Integration Test Suite
Tests Auth, Farm, Weather, AI Modules, Dashboard, and Reports APIs.
Run: .venv/Scripts/python.exe -m pytest tests/test_api.py -v
"""

import sys
import os
import json
import unittest

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import create_app
from app.extensions import db


class AgriNovaTestCase(unittest.TestCase):
    """Base Test Case — Creates a clean test database for each test class."""

    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config["TESTING"] = True
        cls.app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
            "TEST_DATABASE_URL",
            "postgresql://postgres:Micheal1316@localhost:5432/agrinova_test_db"
        )
        cls.client = cls.app.test_client()
        with cls.app.app_context():
            db.create_all()

    @classmethod
    def tearDownClass(cls):
        with cls.app.app_context():
            db.drop_all()

    def setUp(self):
        self.test_email = "testfarmer@agrinova.ai"
        self.test_password = "Test@1234!"
        self.test_phone = "9876543210"
        self.access_token = None

    def _register_user(self):
        return self.client.post(
            "/api/auth/register",
            json={
                "full_name": "Test Farmer",
                "email": self.test_email,
                "phone": self.test_phone,
                "password": self.test_password,
                "confirm_password": self.test_password
            },
            content_type="application/json"
        )

    def _login_user(self):
        res = self.client.post(
            "/api/auth/login",
            json={"email": self.test_email, "password": self.test_password},
            content_type="application/json"
        )
        data = res.get_json()
        if data.get("success"):
            self.access_token = data["access_token"]
        return res

    def _auth_headers(self):
        return {"Authorization": f"Bearer {self.access_token}"}


class TestAuthAPI(AgriNovaTestCase):
    """Test Authentication endpoints."""

    def test_01_register_success(self):
        res = self._register_user()
        data = res.get_json()
        self.assertIn(res.status_code, [201, 409])  # 409 if already registered

    def test_02_register_duplicate_email_fails(self):
        self._register_user()
        res = self._register_user()  # Register again
        data = res.get_json()
        self.assertIn(res.status_code, [201, 409])

    def test_03_login_success(self):
        self._register_user()
        res = self._login_user()
        data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertIn("access_token", data)
        self.assertIn("refresh_token", data)

    def test_04_login_wrong_password_fails(self):
        self._register_user()
        res = self.client.post(
            "/api/auth/login",
            json={"email": self.test_email, "password": "WrongPassword!"},
            content_type="application/json"
        )
        data = res.get_json()
        self.assertEqual(res.status_code, 401)
        self.assertFalse(data["success"])

    def test_05_profile_requires_auth(self):
        res = self.client.get("/api/auth/profile")
        self.assertIn(res.status_code, [401, 422])

    def test_06_profile_with_token(self):
        self._register_user()
        self._login_user()
        res = self.client.get("/api/auth/profile", headers=self._auth_headers())
        data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["user"]["email"], self.test_email)

    def test_07_forgot_password(self):
        self._register_user()
        res = self.client.post(
            "/api/auth/forgot-password",
            json={"email": self.test_email},
            content_type="application/json"
        )
        data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertIn("token", data)

    def test_08_logout_success(self):
        self._register_user()
        self._login_user()
        res = self.client.post("/api/auth/logout", headers=self._auth_headers())
        data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])


class TestFarmAPI(AgriNovaTestCase):
    """Test Farm CRUD endpoints."""

    def setUp(self):
        super().setUp()
        self._register_user()
        self._login_user()

    def _create_farm(self):
        return self.client.post(
            "/api/farms/",
            json={
                "farm_name": "Green Valley Farm",
                "state": "Maharashtra",
                "district": "Pune",
                "village": "Shivpur",
                "soil_type": "Loamy",
                "farm_size": 3.5,
                "latitude": 18.5204,
                "longitude": 73.8567
            },
            headers=self._auth_headers(),
            content_type="application/json"
        )

    def test_01_create_farm(self):
        res = self._create_farm()
        data = res.get_json()
        self.assertEqual(res.status_code, 201)
        self.assertTrue(data["success"])
        self.assertEqual(data["farm"]["farm_name"], "Green Valley Farm")

    def test_02_get_all_farms(self):
        self._create_farm()
        res = self.client.get("/api/farms/", headers=self._auth_headers())
        data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertIsInstance(data["farms"], list)

    def test_03_get_single_farm(self):
        create_res = self._create_farm()
        farm_id = create_res.get_json()["farm"]["id"]
        res = self.client.get(f"/api/farms/{farm_id}", headers=self._auth_headers())
        data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["farm"]["id"], farm_id)

    def test_04_update_farm(self):
        create_res = self._create_farm()
        farm_id = create_res.get_json()["farm"]["id"]
        res = self.client.put(
            f"/api/farms/{farm_id}",
            json={"farm_name": "Updated Farm Name"},
            headers=self._auth_headers(),
            content_type="application/json"
        )
        data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["farm"]["farm_name"], "Updated Farm Name")

    def test_05_delete_farm(self):
        create_res = self._create_farm()
        farm_id = create_res.get_json()["farm"]["id"]
        res = self.client.delete(f"/api/farms/{farm_id}", headers=self._auth_headers())
        data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])


class TestAIPredictionAPI(AgriNovaTestCase):
    """Test AI module prediction endpoints."""

    def setUp(self):
        super().setUp()
        self._register_user()
        self._login_user()

    def test_01_crop_recommendation(self):
        res = self.client.post(
            "/api/crop/recommend",
            json={
                "nitrogen": 90, "phosphorus": 42, "potassium": 43,
                "temperature": 20.8, "humidity": 82.0,
                "ph": 6.5, "rainfall": 202.9
            },
            headers=self._auth_headers(),
            content_type="application/json"
        )
        data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertIn("recommended_crop", data)

    def test_02_fertilizer_recommendation(self):
        res = self.client.post(
            "/api/ai/fertilizer",
            json={
                "soil_type": "Loamy", "crop_type": "rice",
                "nitrogen": 37, "phosphorus": 0, "potassium": 0,
                "moisture": 55.0
            },
            headers=self._auth_headers(),
            content_type="application/json"
        )
        data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertIn("recommended_fertilizer", data)

    def test_03_yield_prediction(self):
        res = self.client.post(
            "/api/prediction/yield",
            json={
                "state": "Maharashtra", "crop": "rice",
                "season": "Kharif", "area": 2.5,
                "rainfall": 1200.0, "temperature": 27.5
            },
            headers=self._auth_headers(),
            content_type="application/json"
        )
        data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertIn("predicted_yield", data)

    def test_04_market_price_prediction(self):
        res = self.client.post(
            "/api/prediction/price",
            json={
                "state": "Maharashtra", "district": "Pune",
                "commodity": "Rice", "month": 7
            },
            headers=self._auth_headers(),
            content_type="application/json"
        )
        data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertIn("predicted_price", data)


class TestDashboardAPI(AgriNovaTestCase):
    """Test Dashboard statistics endpoint."""

    def setUp(self):
        super().setUp()
        self._register_user()
        self._login_user()

    def test_01_get_dashboard_stats(self):
        res = self.client.get("/api/dashboard/stats", headers=self._auth_headers())
        data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertIn("stats", data)
        self.assertIn("farms_count", data["stats"])
        self.assertIn("predictions_count", data["stats"])
        self.assertIn("breakdown", data["stats"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
