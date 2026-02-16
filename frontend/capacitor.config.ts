import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'works.aasirbad.app',
  appName: 'आसिर्बाद',
  webDir: 'out',
  server: {
    // Point to your live backend for API calls
    url: 'https://aasirbad.works',
    cleartext: false,
  },
  ios: {
    scheme: 'Aasirbad',
    contentInset: 'automatic',
    backgroundColor: '#451a03', // amber-950 to match theme
    preferredContentMode: 'mobile',
  },
  plugins: {
    Keyboard: {
      resize: 'body',
      resizeOnFullScreen: true,
    },
    StatusBar: {
      style: 'dark',
      backgroundColor: '#451a03',
    },
    Haptics: {
      // Available for feedback on record/training actions
    },
  },
};

export default config;
