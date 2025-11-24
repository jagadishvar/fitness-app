// frontend/components/CameraScreen.js
import React, { useEffect, useRef, useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ActivityIndicator, Platform } from 'react-native';
import { Camera } from 'expo-camera';
import axios from 'axios';
import * as ImageManipulator from 'expo-image-manipulator';

// Replace with your backend address (your PC IP) when testing on phone.
const SERVER_URL = "http://<YOUR_BACKEND_IP>:8000/evaluate";

export default function CameraScreen() {
  const cameraRef = useRef(null);
  const [hasPermission, setHasPermission] = useState(null);
  const [evaluating, setEvaluating] = useState(false);
  const [feedback, setFeedback] = useState(null);

  useEffect(() => {
    (async () => {
      const { status } = await Camera.requestCameraPermissionsAsync();
      setHasPermission(status === 'granted');
    })();
  }, []);

  const captureAndSend = async () => {
    if (!cameraRef.current) return;
    setEvaluating(true);
    try {
      const photo = await cameraRef.current.takePictureAsync({ base64: false, quality: 0.6 });
      // Optionally resize/compress
      const manipResult = await ImageManipulator.manipulateAsync(photo.uri, [{ resize: { width: 640 } }], { compress: 0.7, format: ImageManipulator.SaveFormat.JPEG });
      const uri = manipResult.uri;

      const formData = new FormData();
      const filename = uri.split('/').pop();
      const match = /\.(\w+)$/.exec(filename);
      const type = match ? `image/${match[1]}` : `image/jpg`;

      formData.append('file', {
        uri,
        name: filename,
        type
      });
      formData.append('exercise', 'squat');

      const response = await axios.post(SERVER_URL, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 25000
      });

      if (response.data.ok) {
        setFeedback(response.data.result);
      } else {
        setFeedback({ error: response.data.error || 'Unknown error' });
      }

    } catch (err) {
      console.error(err);
      setFeedback({ error: 'Network or server error' });
    } finally {
      setEvaluating(false);
    }
  };

  if (hasPermission === null) return <View style={styles.center}><Text>Requesting camera permission...</Text></View>;
  if (hasPermission === false) return <View style={styles.center}><Text>No access to camera</Text></View>;

  return (
    <View style={{ flex: 1 }}>
      <Camera style={{ flex: 4 }} type={Camera.Constants.Type.front} ref={cameraRef} ratio="16:9" />
      <View style={{ flex: 3, padding: 12 }}>
        <TouchableOpacity style={styles.button} onPress={captureAndSend} disabled={evaluating}>
          <Text style={styles.buttonText}>{evaluating ? 'Evaluating...' : 'Capture & Evaluate'}</Text>
        </TouchableOpacity>
        {evaluating && <ActivityIndicator size="large" />}
        {feedback && (
          <View style={styles.feedback}>
            {feedback.error ? (
              <Text style={{ color: 'red' }}>{feedback.error}</Text>
            ) : (
              <>
                <Text>Exercise: {feedback.exercise}</Text>
                <Text>Score: {feedback.score}</Text>
                <Text>Left Knee: {feedback.left_knee_angle}°</Text>
                <Text>Right Knee: {feedback.right_knee_angle}°</Text>
                <Text>Torso Angle: {feedback.avg_torso_angle}°</Text>
                {feedback.mistakes && feedback.mistakes.map((m, i) => <Text key={i}>• {m}</Text>)}
                {feedback.suggestions && feedback.suggestions.map((s, i) => <Text key={i}>→ {s}</Text>)}
              </>
            )}
          </View>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  button: {
    backgroundColor: '#0E55B1',
    padding: 14,
    borderRadius: 10,
    alignItems: 'center',
    marginBottom: 10
  },
  buttonText: { color: 'white', fontWeight: '600' },
  feedback: { backgroundColor: '#f2f6fb', padding: 12, borderRadius: 8 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' }
});
