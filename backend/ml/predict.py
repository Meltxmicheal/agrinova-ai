import os
import pickle
import numpy as np
import pandas as pd
from PIL import Image

# Get models path
models_dir = os.path.join(os.path.dirname(__file__), "models")

class MLInferenceService:
    """
    ML Inference Service
    Exposes static methods to perform inference using trained models.
    """

    _crop_model = None
    _yield_data = None
    _fertilizer_data = None
    _price_data = None
    _disease_model = None

    @classmethod
    def _get_crop_model(cls):
        if cls._crop_model is None:
            path = os.path.join(models_dir, "crop_recommendation.pkl")
            with open(path, "rb") as f:
                cls._crop_model = pickle.load(f)
        return cls._crop_model

    @classmethod
    def _get_yield_data(cls):
        if cls._yield_data is None:
            path = os.path.join(models_dir, "yield_prediction.pkl")
            with open(path, "rb") as f:
                cls._yield_data = pickle.load(f)
        return cls._yield_data

    @classmethod
    def _get_fertilizer_data(cls):
        if cls._fertilizer_data is None:
            path = os.path.join(models_dir, "fertilizer_recommendation.pkl")
            with open(path, "rb") as f:
                cls._fertilizer_data = pickle.load(f)
        return cls._fertilizer_data

    @classmethod
    def _get_price_data(cls):
        if cls._price_data is None:
            path = os.path.join(models_dir, "market_price_prediction.pkl")
            with open(path, "rb") as f:
                cls._price_data = pickle.load(f)
        return cls._price_data

    @classmethod
    def _get_disease_model(cls):
        if cls._disease_model is None:
            path = os.path.join(models_dir, "disease_detection.pkl")
            with open(path, "rb") as f:
                cls._disease_model = pickle.load(f)
        return cls._disease_model

    @classmethod
    def recommend_crop(cls, N: int, P: int, K: int, temperature: float, humidity: float, ph: float, rainfall: float) -> str:
        """
        Predict the best crop to grow.
        """
        model = cls._get_crop_model()
        features = pd.DataFrame([[N, P, K, temperature, humidity, ph, rainfall]], 
                                columns=["N", "P", "K", "temperature", "humidity", "ph", "rainfall"])
        prediction = model.predict(features)[0]
        return str(prediction)

    @classmethod
    def predict_yield(cls, state: str, crop: str, season: str, area: float, rainfall: float, temperature: float) -> float:
        """
        Predict crop yield in tonnes.
        """
        data = cls._get_yield_data()
        model = data["model"]
        le_state = data["le_state"]
        le_crop = data["le_crop"]
        le_season = data["le_season"]

        # Handle unseen categories gracefully
        try:
            state_val = le_state.transform([state])[0]
        except ValueError:
            state_val = le_state.transform([le_state.classes_[0]])[0]

        try:
            crop_val = le_crop.transform([crop])[0]
        except ValueError:
            crop_val = le_crop.transform([le_crop.classes_[0]])[0]

        try:
            season_val = le_season.transform([season])[0]
        except ValueError:
            season_val = le_season.transform([le_season.classes_[0]])[0]

        features = pd.DataFrame([[state_val, crop_val, season_val, area, rainfall, temperature]], 
                                columns=["state", "crop", "season", "area", "rainfall", "temperature"])
        prediction = model.predict(features)[0]
        return float(round(prediction, 2))

    @classmethod
    def recommend_fertilizer(cls, soil_type: str, crop_type: str, nitrogen: int, phosphorus: int, potassium: int, moisture: float) -> str:
        """
        Recommend fertilizer based on soil nutrient levels.
        """
        data = cls._get_fertilizer_data()
        model = data["model"]
        le_soil = data["le_soil"]
        le_crop = data["le_crop"]

        try:
            soil_val = le_soil.transform([soil_type])[0]
        except ValueError:
            soil_val = le_soil.transform([le_soil.classes_[0]])[0]

        try:
            crop_val = le_crop.transform([crop_type])[0]
        except ValueError:
            crop_val = le_crop.transform([le_crop.classes_[0]])[0]

        features = pd.DataFrame([[soil_val, crop_val, nitrogen, phosphorus, potassium, moisture]], 
                                columns=["soil_type", "crop_type", "nitrogen", "phosphorus", "potassium", "moisture"])
        prediction = model.predict(features)[0]
        return str(prediction)

    @classmethod
    def predict_market_price(cls, state: str, district: str, commodity: str, month: int) -> float:
        """
        Predict commodity market price (INR per quintal).
        """
        data = cls._get_price_data()
        model = data["model"]
        le_state = data["le_state"]
        le_dist = data["le_dist"]
        le_comm = data["le_comm"]

        try:
            state_val = le_state.transform([state])[0]
        except ValueError:
            state_val = le_state.transform([le_state.classes_[0]])[0]

        try:
            dist_val = le_dist.transform([district])[0]
        except ValueError:
            dist_val = le_dist.transform([le_dist.classes_[0]])[0]

        try:
            comm_val = le_comm.transform([commodity])[0]
        except ValueError:
            comm_val = le_comm.transform([le_comm.classes_[0]])[0]

        features = pd.DataFrame([[state_val, dist_val, comm_val, month]], 
                                columns=["state", "district", "commodity", "month"])
        prediction = model.predict(features)[0]
        return float(round(prediction, 2))

    @classmethod
    def detect_disease(cls, image_path: str) -> dict:
        """
        Analyze uploaded image statistics to classify plant disease.
        """
        model = cls._get_disease_model()
        
        # Load image and compute channel statistics (mean and std)
        try:
            img = Image.open(image_path).convert("RGB")
            img_arr = np.array(img)
            
            r_mean = float(np.mean(img_arr[:, :, 0]))
            g_mean = float(np.mean(img_arr[:, :, 1]))
            b_mean = float(np.mean(img_arr[:, :, 2]))
            
            r_std = float(np.std(img_arr[:, :, 0]))
            g_std = float(np.std(img_arr[:, :, 1]))
            b_std = float(np.std(img_arr[:, :, 2]))
            
            features = pd.DataFrame([[r_mean, g_mean, b_mean, r_std, g_std, b_std]], 
                                    columns=["R_mean", "G_mean", "B_mean", "R_std", "G_std", "B_std"])
            
            # Predict disease and fetch probability/confidence
            prediction = model.predict(features)[0]
            probs = model.predict_proba(features)[0]
            class_idx = np.where(model.classes_ == prediction)[0][0]
            confidence = float(round(probs[class_idx], 2))
            
            parts = prediction.split("___")
            crop = parts[0]
            disease = parts[1].replace("_", " ")
            
            # Formulate action recommendations
            treatments = {
                "Apple scab": "Apply fungicide sprays containing captan or sulfur during bud break. Remove fallen leaves in autumn.",
                "Black rot": "Prune infected twigs and burn them. Clean pruning tools. Spray copper-based fungicides.",
                "Early blight": "Ensure crop rotation. Avoid overhead watering. Use copper soap fungicides or chlorothalonil.",
                "Late blight": "Destroy infected plants. Ensure good airflow. Apply preventative chlorothalonil or copper fungicides.",
                "Bacterial spot": "Use disease-free seed. Spray copper fungicides mixed with mancozeb. Avoid water splash.",
                "Target Spot": "Apply protectant fungicides. Mulch the soil to prevent spores from splashing up.",
                "Healthy": "No treatment required. Maintain current water, nutrient, and soil care schedules."
            }
            
            treatment = treatments.get(disease, "Inspect foliage regularly, ensure proper plant spacing, and apply preventive copper fungicide if symptoms expand.")
            
            pesticide = "Chlorothalonil or Copper-based fungicides" if not "Healthy" in prediction else "None"
            organic = "Neem oil spray, compost tea, or Bacillus subtilis" if not "Healthy" in prediction else "None"
            
            return {
                "disease_name": disease,
                "confidence": confidence,
                "treatment": treatment,
                "pesticide_recommendation": pesticide,
                "organic_alternative": organic
            }
            
        except Exception as e:
            raise ValueError(f"Failed to process image: {str(e)}")
