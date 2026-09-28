# Open iPhone Client

An MIT-licensed Expo SDK 57 development runtime. Build this public project on a
standard GitHub macOS runner, then load your own JavaScript project from a local
Windows computer. No EAS build, Expo subscription, private repository checkout,
or business application code is involved in building this runtime.

Two independently locked variants are provided: `field` (location/task manager,
NetInfo, screenshot support) and `customer` (document picker, clipboard, date picker).
Both include Stripe, camera/image selection, audio, notifications, secure storage,
WebView, Expo Router, and Expo's development launcher. Their package locks are the
native compatibility contract; match the resolved versions in your private app.
This is a development tool, not a production distribution or OTA update service.

## Free native compilation

Run **Build public runtime** in Actions. It compiles both simulator runtimes with
no signing credentials. Simulator output cannot be installed on an iPhone.
Workflows are manual, use standard `macos-26`, and refuse private repositories.
GitHub currently offers free standard runners for public repositories, subject to
its service limits and terms. This is not a guarantee of unlimited capacity.
There is no artifact upload for simulator checks and no paid runner configuration.

## Signed iPhone installation

Create GitHub environments named `field` and `customer`. In each environment set:

| Kind | Name | Value |
| --- | --- | --- |
| Variable | IOS_BUNDLE_ID | Exact bundle ID covered by your existing Apple profile |
| Variable | CLIENT_SCHEME | Your local project's URL scheme |
| Variable | APPLE_MERCHANT_ID | Existing Apple Pay merchant ID, if required |
| Variable | ASSOCIATED_DOMAIN | Associated domain hostname, if required |
| Secret | IOS_DISTRIBUTION_P12_BASE64 | Base64 distribution certificate with private key |
| Secret | IOS_DISTRIBUTION_P12_PASSWORD | Certificate password |
| Secret | IOS_ADHOC_PROFILE_BASE64 | Base64 ad hoc profile containing your test phones |
| Secret | ARTIFACT_PASSWORD | Unique random password, at least 32 characters |

Reuse existing Apple credentials. Never commit them. Run **Signed development client**
on `main` for the chosen runtime. It creates a Debug archive and validates the
profile's bundle ID, expiration, devices, and signing certificate. Apple membership,
provisioning expiration, and native entitlement rules still apply.

Signed IPA files contain device identifiers, so only an AES-256-GCM encrypted file
is uploaded to the public workflow. Artifact retention is one day. Download it,
set `ARTIFACT_PASSWORD` securely in your local environment, then from this repository:

```powershell
node scripts/seal.mjs unseal 'C:\Downloads\client.sealed' 'C:\Downloads\client.ipa'
uvx pymobiledevice3 apps install 'C:\Downloads\client.ipa'
```

Install Apple's Windows Mobile Device Support drivers first; connect, unlock and
trust the registered iPhone. Never remove an existing app containing unsynced data.
Using an existing bundle ID replaces that installation, so use a dedicated test phone.
Enable Developer Mode if requested. Authentication failures or damaged encrypted
files produce no decrypted output. Existing output files are never overwritten.

## Daily work on Windows

In your **private app's directory**, run `npm start -- --port 8081 --scheme YOUR_SCHEME`
(replace `YOUR_SCHEME` with the `CLIENT_SCHEME` configured above). Open the
development launcher on the phone and enter the displayed LAN URL, or scan the
QR code. The explicit scheme is required because this public runtime's generated
`exp+` scheme differs from your private project's slug. Use port 8082 for a second app.
Both devices must be on the same reachable network. No Expo login is required.
Restart Metro with `npm start -- --clear` and reconnect if the connection is stale.

JavaScript and TypeScript changes use the existing installed runtime. Adding or
upgrading native dependencies, changing native configuration or entitlements, or
renewing an expired profile requires another native build. Do not assume a matching
SDK number means all native dependency versions match. Notification registration,
Apple Pay, associated links, location behavior and authentication must be tested
against the actual signing identity and the private app on a physical device.

The generic welcome screen does not request permissions or connect to a backend.
The launcher can load development code with native privileges: only open trusted
projects, keep Metro on a trusted LAN, and do not expose its port to the internet.

## Sources

- [Expo development client](https://github.com/expo/expo/tree/main/packages/expo-dev-client)
- [Development workflow](https://docs.expo.dev/develop/development-builds/use-development-builds/)
- [GitHub runner pricing scope](https://docs.github.com/en/actions/how-tos/write-workflows/choose-where-workflows-run/choose-the-runner-for-a-job)
- [GitHub usage terms](https://docs.github.com/en/site-policy/github-terms/github-terms-for-additional-products-and-features#actions)
- [Fastlane](https://github.com/fastlane/fastlane)
- [Windows device tooling](https://github.com/doronz88/pymobiledevice3)

Dependency licenses remain their respective owners' licenses. MIT covers this
repository's original launcher, configuration and scripts.
