// frontend/App.js
import React from 'react';
import { SafeAreaView } from 'react-native';
import CameraScreen from './components/CameraScreen';

export default function App() {
  return (
    <SafeAreaView style={{ flex: 1 }}>
      <CameraScreen />
    </SafeAreaView>
  );
}
