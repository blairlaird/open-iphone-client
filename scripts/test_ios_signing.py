import copy
import datetime as dt
import hashlib
import unittest

from prepare_ios_signing import signing_settings


class SigningChecks(unittest.TestCase):
    def test_profile_must_match_identity_app_devices_and_expiration(self):
        certificate = b"test certificate bytes"
        identity = hashlib.sha1(certificate).hexdigest()
        now = dt.datetime(2026, 9, 28, tzinfo=dt.timezone.utc)
        profile = {
            "UUID": "12345678-1234-4123-8123-123456789012",
            "ExpirationDate": dt.datetime(2027, 9, 28),
            "TeamIdentifier": ["ABCDEFGHIJ"],
            "ApplicationIdentifierPrefix": ["ABCDEFGHIJ"],
            "Entitlements": {"application-identifier": "ABCDEFGHIJ.com.example.app", "get-task-allow": False},
            "ProvisionedDevices": ["test-device"],
            "DeveloperCertificates": [certificate],
        }
        valid = signing_settings(profile, "com.example.app", identity, now)
        self.assertEqual(valid["method"], "release-testing")
        self.assertEqual(valid["signingCertificate"], identity.upper())
        self.assertFalse(valid["manageAppVersionAndBuildNumber"])
        invalid_profiles = [
            {"ExpirationDate": now},
            {"ProvisionedDevices": []},
            {"ProvisionsAllDevices": True},
            {"TeamIdentifier": ["bad\nteam"]},
            {"DeveloperCertificates": [b"different certificate"]},
            {"UUID": "bad\nvalue"},
            {"Entitlements": {"application-identifier": "ABCDEFGHIJ.*", "get-task-allow": False}},
            {"Entitlements": {"application-identifier": "ABCDEFGHIJ.com.example.app", "get-task-allow": True}},
        ]
        for change in invalid_profiles:
            with self.subTest(change=change), self.assertRaises((ValueError, KeyError)):
                signing_settings({**copy.deepcopy(profile), **change}, "com.example.app", identity, now)


if __name__ == "__main__":
    unittest.main()
