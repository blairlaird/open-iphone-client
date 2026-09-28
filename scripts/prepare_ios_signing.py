"""Validate an ad hoc iPhone profile and prepare Xcode's manual export settings."""
import datetime as dt
import hashlib
import os
import plistlib
import re
import sys
import uuid
from pathlib import Path


def signing_settings(profile, bundle_id, certificate_sha1, now=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    expiry = profile.get("ExpirationDate")
    if not isinstance(expiry, dt.datetime):
        raise ValueError("Profile has no expiration date.")
    if expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=dt.timezone.utc)
    if expiry <= now:
        raise ValueError("Provisioning profile has expired.")
    entitlements = profile.get("Entitlements", {})
    teams = profile.get("TeamIdentifier", [])
    if len(teams) != 1 or not re.fullmatch(r"[A-Z0-9]{10}", teams[0]):
        raise ValueError("Profile must contain one Apple team.")
    prefixes = profile.get("ApplicationIdentifierPrefix", [])
    if entitlements.get("application-identifier") not in [p + "." + bundle_id for p in prefixes]:
        raise ValueError("Profile does not match this app's exact bundle identifier.")
    if not profile.get("ProvisionedDevices") or profile.get("ProvisionsAllDevices") or entitlements.get("get-task-allow") is not False:
        raise ValueError("Use an ad hoc distribution profile containing the test iPhones.")
    if not re.fullmatch(r"[A-Fa-f0-9]{40}", certificate_sha1):
        raise ValueError("Expected one valid signing identity in the temporary keychain.")
    hashes = [hashlib.sha1(cert).hexdigest().upper() for cert in profile.get("DeveloperCertificates", [])]
    if certificate_sha1.upper() not in hashes:
        raise ValueError("Signing certificate is not included in this provisioning profile.")
    profile_id = profile["UUID"]
    if str(uuid.UUID(profile_id)).lower() != profile_id.lower():
        raise ValueError("Profile UUID must use canonical UUID format.")
    return {
        "method": "release-testing",
        "teamID": teams[0],
        "signingStyle": "manual",
        "signingCertificate": certificate_sha1.upper(),
        "provisioningProfiles": {bundle_id: profile_id},
        "manageAppVersionAndBuildNumber": False,
    }


if __name__ == "__main__":
    profile_path, bundle_id, certificate_sha1, output_dir = sys.argv[1:]
    with open(profile_path, "rb") as source:
        settings = signing_settings(plistlib.load(source), bundle_id, certificate_sha1)
    destination = Path(output_dir)
    with (destination / "ExportOptions.plist").open("wb") as target:
        plistlib.dump(settings, target)
    with open(os.environ["GITHUB_ENV"], "a", encoding="utf-8") as target:
        target.write("APPLE_TEAM_ID=" + settings["teamID"] + "\n")
        target.write("PROFILE_UUID=" + settings["provisioningProfiles"][bundle_id] + "\n")
        target.write("SIGNING_CERTIFICATE=" + settings["signingCertificate"] + "\n")
    print(settings["provisioningProfiles"][bundle_id])
