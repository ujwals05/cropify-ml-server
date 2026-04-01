import pickle
import numpy as np
from pathlib import Path

# This builds the correct path to your models folder
# Works on any computer regardless of where the project is
BASE_DIR = Path(__file__).resolve().parent

# -------------------------------------------------------
# Load all 3 pkl files ONCE when server starts
# These stay in memory for every request after that
# -------------------------------------------------------

with open(BASE_DIR / "models" / "soil_model.pkl", "rb") as f:
    model = pickle.load(f)

with open(BASE_DIR / "models" / "scaler.pkl", "rb") as f:
    scaler = pickle.load(f)

with open(BASE_DIR / "models" / "label_encoder.pkl", "rb") as f:
    label_encoder = pickle.load(f)


def predict_crop(
    nitrogen: float,
    phosphorus: float,
    potassium: float,
    temperature: float,
    humidity: float,
    ph: float,
    rainfall: float
) -> dict:

    # Step 1 — Arrange input in exact same order as your notebook
    # Your notebook: X = df.drop("label") → columns are N,P,K,temp,humidity,ph,rainfall
    input_data = np.array([[
        nitrogen, phosphorus, potassium,
        temperature, humidity, ph, rainfall
    ]])

    # Step 2 — Scale using the saved scaler (same as training)
    input_scaled = scaler.transform(input_data)

    # Step 3 — Predict (returns a number like 14)
    prediction = model.predict(input_scaled)

    # Step 4 — Convert number back to crop name using label encoder
    # Your notebook: le.inverse_transform(prediction)
    crop_name = label_encoder.inverse_transform(prediction)[0]

    # Step 5 — Get confidence % for all crops
    probabilities = model.predict_proba(input_scaled)[0]

    # Step 6 — Get top 3 crops with confidence scores
    top3_indices = probabilities.argsort()[-3:][::-1]
    top3 = [
        {
            "crop": label_encoder.inverse_transform([i])[0],
            "confidence": round(float(probabilities[i]) * 100, 2)
        }
        for i in top3_indices
    ]

    return {
        "recommended_crop": crop_name,
        "confidence": round(float(probabilities.max()) * 100, 2),
        "top_3": top3
    }