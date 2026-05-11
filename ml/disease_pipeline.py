import json
import numpy as np
from pathlib import Path
from PIL import Image
import io

# TensorFlow loaded lazily to avoid slow startup
import tensorflow as tf

BASE_DIR = Path(__file__).resolve().parent

# Load model and class names once at startup
model = tf.keras.models.load_model(BASE_DIR / "models" / "plant_disease_model.h5")

with open(BASE_DIR / "models" / "class_names.json", "r") as f:
    class_names = json.load(f)


def format_class_name(raw_name: str) -> dict:
    # Class names from PlantVillage look like:
    # "Tomato___Late_blight" or "Apple___Apple_scab"
    # Split into plant and disease
    parts = raw_name.replace("___", "|").replace("_", " ").split("|")

    if len(parts) == 2:
        plant = parts[0].strip().title()
        disease = parts[1].strip().title()
    else:
        plant = "Unknown"
        disease = raw_name.replace("_", " ").title()

    is_healthy = "healthy" in disease.lower()

    return {
        "plant": plant,
        "disease": disease,
        "is_healthy": is_healthy
    }


def get_treatment(disease: str, is_healthy: bool) -> str:
    if is_healthy:
        return "Your plant appears healthy. Continue regular watering, appropriate fertilization, and monitor for early signs of disease."

    disease_lower = disease.lower()

    treatments = {
        "late blight": "Apply copper-based fungicide every 7-10 days. Remove and destroy infected leaves. Avoid overhead watering. Ensure good air circulation.",
        "early blight": "Remove affected leaves immediately. Apply chlorothalonil or mancozeb fungicide. Water at soil level to keep foliage dry.",
        "leaf curl": "Apply insecticidal soap to control aphids and whiteflies. Remove severely infected leaves. Use reflective mulch to deter insects.",
        "powdery mildew": "Apply sulfur-based fungicide or neem oil. Improve air circulation. Avoid overhead watering. Remove heavily infected parts.",
        "rust": "Apply fungicide containing tebuconazole or propiconazole. Remove infected plant material. Avoid wetting leaves.",
        "bacterial spot": "Apply copper-based bactericide. Avoid working with plants when wet. Remove infected plant debris.",
        "mosaic": "No cure available for viral mosaic. Remove and destroy infected plants. Control insect vectors with insecticidal soap.",
        "scab": "Apply fungicide at early signs. Remove infected fruit and leaves. Improve air circulation through pruning.",
        "rot": "Improve drainage. Reduce watering frequency. Apply fungicide containing mefenoxam. Remove severely infected plants.",
        "blight": "Apply copper-based fungicide. Remove infected plant parts. Avoid overhead irrigation. Rotate crops next season.",
    }

    for keyword, treatment in treatments.items():
        if keyword in disease_lower:
            return treatment

    return "Consult your local agriculture department for specific treatment. Generally, remove infected plant parts, improve air circulation, and apply appropriate fungicide or pesticide based on the disease type."


def predict_disease(image_bytes: bytes) -> dict:
    # Step 1 — Open image from bytes
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    # Step 2 — Resize to 224x224 exactly as during training
    img = img.resize((224, 224))

    # Step 3 — Convert to array and normalize exactly as training
    # Training used rescale=1./255
    img_array = np.array(img) / 255.0

    # Step 4 — Add batch dimension
    img_array = np.expand_dims(img_array, axis=0)

    # Step 5 — Predict
    predictions = model.predict(img_array)

    # Step 6 — Get top 3 results
    top3_indices = predictions[0].argsort()[-3:][::-1]

    top3 = []
    for i in top3_indices:
        raw_name = class_names[i]
        formatted = format_class_name(raw_name)
        top3.append({
            "plant": formatted["plant"],
            "disease": formatted["disease"],
            "confidence": round(float(predictions[0][i]), 4),
            "is_healthy": formatted["is_healthy"]
        })

    # Primary result
    primary = top3[0]
    treatment = get_treatment(primary["disease"], primary["is_healthy"])

    return {
        "plant": primary["plant"],
        "disease": primary["disease"],
        "confidence": primary["confidence"],
        "is_healthy": primary["is_healthy"],
        "treatment": treatment,
        "top_3": top3
    }