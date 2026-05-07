# Cropify - Intelligent Crop & Soil Advisory Platform


## Overview
**Cropify** is an AI-powered agricultural advisory API built with FastAPI. Serves four machine learning models for crop recommendation, soil fertility analysis, irrigation advisory, Basic disease detection. Integrates with OpenWeatherMap for live weather data.

Frontend code is available [here](https://github.com/ujwals05/cropify-web-interface).

## Table of Contents
 
- [Project Structure](#project-structure)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Environment Variables](#environment-variables)
- [Installation and Setup](#installation-and-setup)
- [Running the Server](#running-the-server)
- [API Endpoints](#api-endpoints)

## Project Structure
 
```
cultivai-backend/
│
├── ml/
│   ├── models/
│   │   ├── soil_model.pkl              # Crop recommendation — Random Forest model
│   │   ├── scaler.pkl                  # Crop recommendation — StandardScaler
│   │   ├── label_encoder.pkl           # Crop recommendation — LabelEncoder
│   │   ├── soil_fertility_model.pkl    # Soil fertility — Random Forest model
│   │   ├── soil_scaler.pkl             # Soil fertility — StandardScaler
│   │   ├── irrigation_model.pkl        # Irrigation advisory — Random Forest model
│   │   ├── irrigation_scaler.pkl       # Irrigation advisory — StandardScaler
│   │   ├── irrigation_target_le.pkl    # Irrigation advisory — Target LabelEncoder
│   │   └── irrigation_le_dict.pkl      # Irrigation advisory — Categorical encoders dict
│   ├── crop_pipeline.py                # Crop prediction logic
│   ├── soil_pipeline.py                # Soil fertility prediction logic
│   └── irrigation_pipeline.py         # Irrigation prediction logic
│
├── routers/
│   ├── __init__.py
│   ├── crop.py                         # /api/crop routes
│   ├── weather.py                      # /api/weather routes
│   ├── soil.py                         # /api/soil routes
│   └── irrigation.py                   # /api/irrigation routes
│
├── services/
│   └── weather.py                      # OpenWeatherMap API integration
│
├── main.py                             # FastAPI app entry point
├── .env                                # Environment variables (not committed)
├── .gitignore
└── requirements.txt

```

## Features
 
- **Crop Recommendation** — Predicts the most suitable crop based on soil NPK values, pH, temperature, humidity, and rainfall using a trained Random Forest classifier
- **Soil Fertility Analysis** — Predicts soil fertility level (Low / Medium / High) from NDVI, soil moisture, and elevation using a Random Forest regressor
- **Irrigation Advisory** — Predicts irrigation need (High / Medium / Low) from 19 field parameters using a Random Forest classifier
- **Disease detection** — Based on the user uploaded image this will recognise the possible disease
- **Weather Integration** — Fetches live temperature, humidity, and rainfall from OpenWeatherMap by city name or GPS coordinates
- **Input Validation** — All endpoints enforce field-level range validation using Pydantic
- **Auto Documentation** — Swagger UI available at `/docs` for testing all endpoints interactively

---

## Tech Stack
 
| Technology | Purpose |
|---|---|
| FastAPI | Web framework and API server |
| Uvicorn | ASGI server to run FastAPI |
| Scikit-learn | Machine learning models (Random Forest) |
| Joblib / Pickle | Loading saved .pkl model files |
| NumPy | Input array preparation for models |
| Requests | Calling OpenWeatherMap API |
| Python-dotenv | Loading environment variables from .env |
| Pydantic | Request body validation |

---
 
## Prerequisites
 
- Python 3.10 or higher
- pip
- All trained `.pkl` model files exported from Jupyter notebooks
- OpenWeatherMap API key (free tier at [openweathermap.org](https://openweathermap.org))

---

## Environment Variables
 
Create a `.env` file in the root of the backend folder with the following:
 
```env
OPENWEATHER_API_KEY=your_openweathermap_api_key_here
```
 
### How to get the API key
 
1. Go to [openweathermap.org](https://openweathermap.org)
2. Sign up for a free account
3. Navigate to **API Keys** in your dashboard
4. Copy your key and paste it in the `.env` file
> The free tier provides 1000 API calls per day which is sufficient for development and demo use.
 
---

## Installation and Setup
 
### Step 1 — Clone the repository
 
```bash
git clone https://github.com/your-username/cultivai-backend.git
cd cultivai-backend
```
 
### Step 2 — Create and activate virtual environment
 
```bash
# Create virtual environment
python -m venv venv
 
# Activate — Windows
venv\Scripts\activate
 
# Activate — Mac/Linux
source venv/bin/activate
```
 
### Step 3 — Install dependencies
 
```bash
pip install -r requirements.txt
```
 
If you face timeout issues on slow connections, install with an increased timeout:
 
```bash
pip install -r requirements.txt --timeout 120
```
 
### Step 4 — Add ML model files
 
Place all trained `.pkl` files inside `ml/models/`. The following files are required:
 
```
ml/models/
├── soil_model.pkl
├── scaler.pkl
├── label_encoder.pkl
├── soil_fertility_model.pkl
├── soil_scaler.pkl
├── irrigation_model.pkl
├── irrigation_scaler.pkl
├── irrigation_target_le.pkl
└── irrigation_le_dict.pkl
```
 
These files are generated by running the training notebooks. They are not committed to the repository due to file size. See the [ML Models](#ml-models) section for export instructions.
 
### Step 5 — Create the .env file
 
```bash
# Create .env file
echo OPENWEATHER_API_KEY=your_key_here > .env
```
 
Or create it manually and paste your key.
 
---
 
## Running the Server
 
```bash
uvicorn main:app --reload
```
 
The server starts at `http://127.0.0.1:8000`
 
Visit `http://127.0.0.1:8000/docs` to open the interactive Swagger UI and test all endpoints.
 
---

## API Endpoints
 
Check for all the api end points at `http://127.0.0.1:8000/docs`

## .gitignore
 
Make sure your `.gitignore` includes the following so model files and secrets are not committed:
 
```
venv/
__pycache__/
*.pkl
.env
*.pyc
.DS_Store
```
 
---



## Future Enhancements

- Advanced deep learning-based disease detection
- IoT sensor integration for real-time monitoring
- Satellite and remote sensing support
- Farmer dashboard and analytics
- Multilingual voice assistant for rural accessibility
- Cloud deployment and model optimization




