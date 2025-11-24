# backend/app/pose_evaluator.py
import numpy as np

def angle_between_points(a, b, c):
    a = np.array(a); b = np.array(b); c = np.array(c)
    ba = a - b
    bc = c - b
    denom = (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-8)
    cos_angle = np.dot(ba, bc) / denom
    cos_angle = float(np.clip(cos_angle, -1.0, 1.0))
    angle = float(np.degrees(np.arccos(cos_angle)))
    return angle

def evaluate_squat(landmarks):
    mistakes = []
    left_knee_angle = angle_between_points(landmarks['left_hip'], landmarks['left_knee'], landmarks['left_ankle'])
    right_knee_angle = angle_between_points(landmarks['right_hip'], landmarks['right_knee'], landmarks['right_ankle'])
    avg_knee = (left_knee_angle + right_knee_angle) / 2.0

    left_torso_angle = angle_between_points((landmarks['left_hip'][0], landmarks['left_hip'][1]+1),
                                           landmarks['left_hip'],
                                           landmarks['left_shoulder'])
    right_torso_angle = angle_between_points((landmarks['right_hip'][0], landmarks['right_hip'][1]+1),
                                            landmarks['right_hip'],
                                            landmarks['right_shoulder'])
    avg_torso = (left_torso_angle + right_torso_angle) / 2.0

    desired_knee = 90.0
    knee_diff = abs(avg_knee - desired_knee)
    score = 100.0
    score -= min(knee_diff * 0.8, 40)
    torso_penalty = max(0, (avg_torso - 10.0)) * 1.5
    score -= min(torso_penalty, 30)

    if avg_knee > 110:
        mistakes.append("Not squat low enough: bend knees more")
    elif avg_knee < 65:
        mistakes.append("Knees bent too much")

    if avg_torso > 15:
        mistakes.append("Torso leaning forward: keep back straight")

    score = max(0.0, min(100.0, score))
    suggestions = []
    if knee_diff > 10:
        suggestions.append("Aim for thighs parallel to the ground.")
    if avg_torso > 12:
        suggestions.append("Keep chest up to reduce forward lean.")

    return {
        "exercise": "squat",
        "score": round(score, 1),
        "left_knee_angle": round(left_knee_angle, 1),
        "right_knee_angle": round(right_knee_angle, 1),
        "avg_torso_angle": round(avg_torso, 1),
        "mistakes": mistakes,
        "suggestions": suggestions
    }
