# backend/app/main.py
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import cv2
from io import BytesIO
from PIL import Image
from .utils import detect_pose_landmarks_from_bgr
from .pose_evaluator import evaluate_squat
import firebase_admin
try:
    from firebase_admin import credentials, firestore
except ImportError:
    credentials = None
    firestore = None
import os

app = FastAPI(title="Smart Fitness Trainer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Optional Firestore initialization (toggle with env var)
FIREBASE_ENABLED = os.environ.get("FIREBASE_ENABLED", "false").lower() == "true"
if FIREBASE_ENABLED:
    cred_path = os.environ.get("FIREBASE_CRED_JSON", "path/to/serviceAccount.json")
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
    db = firestore.client()

@app.post("/evaluate")
async def evaluate_image(file: UploadFile = File(...), exercise: str = Form("squat")):
    contents = await file.read()
    try:
        image = Image.open(BytesIO(contents)).convert("RGB")
    except Exception as e:
        return {"ok": False, "error": "Invalid image file"}

    image_bgr = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    landmarks = detect_pose_landmarks_from_bgr(image_bgr)
    if landmarks is None:
        return {"ok": False, "error": "No person detected"}

    if exercise == "squat":
        result = evaluate_squat(landmarks)
    else:
        result = {"ok": False, "error": f"Exercise '{exercise}' not implemented"}

    if FIREBASE_ENABLED:
        try:
            db.collection("workout_logs").add({
                "exercise": result.get("exercise"),
                "score": result.get("score"),
                "timestamp": firestore.SERVER_TIMESTAMP
            })
        except Exception as e:
            print("Firebase write failed:", e)

    return {"ok": True, "result": result}
