module.exports = variant => {
  const bundleIdentifier = process.env.IOS_BUNDLE_ID || `org.example.openclient.${variant}`;
  if (!/^[A-Za-z0-9]+(?:[.-][A-Za-z0-9]+)+$/.test(bundleIdentifier)) throw Error('Invalid IOS_BUNDLE_ID');
  const scheme = process.env.CLIENT_SCHEME || `openclient-${variant}`;
  if (!/^[a-z][a-z0-9+.-]*$/.test(scheme)) throw Error('Invalid CLIENT_SCHEME');
  const merchant = process.env.APPLE_MERCHANT_ID;
  if (merchant && !/^merchant\.[A-Za-z0-9.-]+$/.test(merchant)) throw Error('Invalid APPLE_MERCHANT_ID');
  return { expo: {
    name: `Open Client ${variant}`, slug: `open-client-${variant}`, version: '1.0.0',
    scheme, userInterfaceStyle: 'automatic',
    ios: { bundleIdentifier, supportsTablet: true, buildNumber: '1',
      associatedDomains: process.env.ASSOCIATED_DOMAIN ? [`applinks:${process.env.ASSOCIATED_DOMAIN}`] : [],
      infoPlist: { ITSAppUsesNonExemptEncryption: false,
        NSCameraUsageDescription: 'Allow the development project to use your camera.',
        NSMicrophoneUsageDescription: 'Allow the development project to use your microphone.',
        NSPhotoLibraryUsageDescription: 'Allow the development project to select photos.',
        NSLocalNetworkUsageDescription: 'Connect to your computer for local development.',
        UIBackgroundModes: variant === 'field' ? ['location', 'fetch'] : ['remote-notification'] }
    },
    plugins: ['expo-router', ['expo-dev-client', { launchMode: 'launcher' }],
      'expo-secure-store', 'expo-audio', 'expo-asset', 'expo-image-picker',
      ['expo-notifications', { color: '#0f766e' }],
      ['@stripe/stripe-react-native', merchant ? { merchantIdentifier: merchant } : {}],
      ...(variant === 'field' ? [['expo-location', {
        locationWhenInUsePermission: 'Allow the development project to use your location.',
        locationAlwaysAndWhenInUsePermission: 'Allow background location only while testing a feature with your consent.',
        isIosBackgroundLocationEnabled: true
      }]] : ['@react-native-community/datetimepicker'])],
    extra: { router: { origin: false } }
  }};
};
