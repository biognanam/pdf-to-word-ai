"""Unit tests for authentication service."""

import logging
import unittest

from services.auth_service import AuthService


class AuthServiceTestCase(unittest.TestCase):
    """Authentication tests."""

    def setUp(self) -> None:
        logger = logging.getLogger("tests.auth")
        config = "admin|Admin@123|Admin,user|User@123|User"
        self.service = AuthService(auth_users_config=config, logger=logger)

    def test_authenticate_success(self) -> None:
        identity = self.service.authenticate("admin", "Admin@123")
        self.assertIsNotNone(identity)
        self.assertEqual(identity.username, "admin")
        self.assertEqual(identity.role, "Admin")

    def test_authenticate_failure(self) -> None:
        identity = self.service.authenticate("admin", "wrong")
        self.assertIsNone(identity)


if __name__ == "__main__":
    unittest.main()
