# Smart Fitness Trainer

## Backend (FastAPI)
1. Create venv:
   python -m venv venv
   source venv/bin/activate   # windows: venv\Scripts\activate
2. Install requirements:
   pip install -r backend/app/requirements.txt
3. Run:
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Open http://127.0.0.1:8000/docs to test API.

## Frontend (Expo)
1. cd frontend
2. npm install
3. Update SERVER_URL in components/CameraScreen.js to your backend IP (e.g., http://192.168.1.100:8000/evaluate)
4. expo start
5. Use Expo Go app on phone to test.

## Notes
- Use Python 3.10 on backend for best compatibility with mediapipe.
- In production, prefer on-device inference (TF Lite) to avoid sending images across network.
