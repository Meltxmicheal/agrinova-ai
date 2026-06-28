import os
import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import LabelEncoder

# Create models directory if it doesn't exist
models_dir = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(models_dir, exist_ok=True)

print("Starting AgriNova AI Model Training...")

# =====================================================
# 1. Crop Recommendation Model
# =====================================================
print("Training Crop Recommendation Model...")
np.random.seed(42)
n_samples = 1500

# Generate N, P, K, temp, humidity, pH, rainfall
N = np.random.randint(10, 140, n_samples)
P = np.random.randint(5, 140, n_samples)
K = np.random.randint(5, 200, n_samples)
temp = np.random.uniform(15, 40, n_samples)
humidity = np.random.uniform(20, 100, n_samples)
ph = np.random.uniform(4.5, 8.5, n_samples)
rainfall = np.random.uniform(30, 300, n_samples)

crops = ["rice", "maize", "chickpea", "kidneybeans", "pigeonpeas", "mothbeans", 
         "mungbean", "blackgram", "lentil", "pomegranate", "banana", "mango", 
         "grapes", "watermelon", "muskmelon", "apple", "orange", "papaya", 
         "coconut", "cotton", "jute", "coffee"]

labels = []
for i in range(n_samples):
    # Rule-based synthetic logic for realistic distribution
    if rainfall[i] > 180 and temp[i] > 22 and humidity[i] > 70:
        labels.append("rice")
    elif rainfall[i] > 150 and temp[i] > 20 and N[i] > 80:
        labels.append("jute")
    elif rainfall[i] > 120 and temp[i] > 25 and humidity[i] > 60:
        labels.append("coconut")
    elif temp[i] > 28 and humidity[i] > 70 and rainfall[i] > 100:
        labels.append("papaya")
    elif temp[i] < 22 and rainfall[i] < 100 and humidity[i] < 50:
        labels.append("chickpea")
    elif N[i] > 60 and P[i] > 50 and K[i] > 50:
        labels.append("banana")
    elif K[i] > 100 and P[i] > 100:
        labels.append("grapes")
    elif rainfall[i] > 150 and temp[i] > 18:
        labels.append("coffee")
    elif temp[i] > 25 and humidity[i] < 60:
        labels.append("cotton")
    elif ph[i] < 5.5:
        labels.append("mango")
    else:
        labels.append(np.random.choice(crops))

df_crop = pd.DataFrame({
    "N": N, "P": P, "K": K, 
    "temperature": temp, "humidity": humidity, 
    "ph": ph, "rainfall": rainfall, "label": labels
})

X_crop = df_crop.drop("label", axis=1)
y_crop = df_crop["label"]

crop_model = RandomForestClassifier(n_estimators=50, random_state=42)
crop_model.fit(X_crop, y_crop)

with open(os.path.join(models_dir, "crop_recommendation.pkl"), "wb") as f:
    pickle.dump(crop_model, f)
print("Crop Recommendation Model saved!")


# =====================================================
# 2. Yield Prediction Model
# =====================================================
print("Training Yield Prediction Model...")
# Inputs: state, crop, season, area, rainfall, temp
states = ["Maharashtra", "Punjab", "Gujarat", "Karnataka", "Tamil Nadu", "Uttar Pradesh"]
seasons = ["Kharif", "Rabi", "Summer", "Whole Year"]

le_state = LabelEncoder()
le_crop = LabelEncoder()
le_season = LabelEncoder()

# Fit encoders on lists
le_state.fit(states)
le_crop.fit(crops)
le_season.fit(seasons)

# Generate synthetic yield data
state_col = np.random.choice(states, n_samples)
crop_col = np.random.choice(crops, n_samples)
season_col = np.random.choice(seasons, n_samples)
area = np.random.uniform(0.5, 20.0, n_samples) # hectares
rainfall_yield = np.random.uniform(50, 2500, n_samples) # mm
temp_yield = np.random.uniform(15, 38, n_samples) # celsius

# Yield formula: proportional to area, rainfall, and fertilizer
yield_tonnes = area * (1.5 + (rainfall_yield / 1000) * 0.8 + (temp_yield / 30) * 0.4 + np.random.normal(0, 0.2, n_samples))
yield_tonnes = np.clip(yield_tonnes, 0.1, None)

df_yield = pd.DataFrame({
    "state": le_state.transform(state_col),
    "crop": le_crop.transform(crop_col),
    "season": le_season.transform(season_col),
    "area": area,
    "rainfall": rainfall_yield,
    "temperature": temp_yield
})

yield_model = RandomForestRegressor(n_estimators=50, random_state=42)
yield_model.fit(df_yield, yield_tonnes)

# Save model and encoders
yield_data = {
    "model": yield_model,
    "le_state": le_state,
    "le_crop": le_crop,
    "le_season": le_season
}
with open(os.path.join(models_dir, "yield_prediction.pkl"), "wb") as f:
    pickle.dump(yield_data, f)
print("Yield Prediction Model saved!")


# =====================================================
# 3. Fertilizer Recommendation Model
# =====================================================
print("Training Fertilizer Recommendation Model...")
soil_types = ["Sandy", "Loamy", "Clayey", "Black", "Red"]
fertilizers = ["Urea", "DAP", "MOP", "10-26-26", "19-19-19", "SSP", "20-20"]

le_soil = LabelEncoder()
le_crop_f = LabelEncoder()
le_soil.fit(soil_types)
le_crop_f.fit(crops)

soil_col = np.random.choice(soil_types, n_samples)
crop_f_col = np.random.choice(crops, n_samples)
nitrogen = np.random.randint(0, 150, n_samples)
phosphorus = np.random.randint(0, 150, n_samples)
potassium = np.random.randint(0, 150, n_samples)
moisture = np.random.uniform(10, 80, n_samples)

fert_labels = []
for i in range(n_samples):
    if nitrogen[i] < 30 and phosphorus[i] > 60:
        fert_labels.append("DAP")
    elif nitrogen[i] > 80 and phosphorus[i] < 40:
        fert_labels.append("Urea")
    elif potassium[i] > 80 and nitrogen[i] < 40:
        fert_labels.append("MOP")
    elif nitrogen[i] > 40 and phosphorus[i] > 40 and potassium[i] > 40:
        fert_labels.append("19-19-19")
    elif soil_col[i] == "Sandy" and moisture[i] < 30:
        fert_labels.append("SSP")
    else:
        fert_labels.append(np.random.choice(fertilizers))

df_fert = pd.DataFrame({
    "soil_type": le_soil.transform(soil_col),
    "crop_type": le_crop_f.transform(crop_f_col),
    "nitrogen": nitrogen,
    "phosphorus": phosphorus,
    "potassium": potassium,
    "moisture": moisture
})

fert_model = RandomForestClassifier(n_estimators=50, random_state=42)
fert_model.fit(df_fert, fert_labels)

fert_data = {
    "model": fert_model,
    "le_soil": le_soil,
    "le_crop": le_crop_f
}
with open(os.path.join(models_dir, "fertilizer_recommendation.pkl"), "wb") as f:
    pickle.dump(fert_data, f)
print("Fertilizer Recommendation Model saved!")


# =====================================================
# 4. Market Price Prediction Model
# =====================================================
print("Training Market Price Prediction Model...")
commodities = ["Rice", "Wheat", "Maize", "Cotton", "Jute", "Potato", "Tomato", "Onion"]
districts = ["Pune", "Nagpur", "Nashik", "Rajkot", "Surat", "Karnal", "Meerut"]

le_state_p = LabelEncoder()
le_dist_p = LabelEncoder()
le_comm_p = LabelEncoder()

le_state_p.fit(states)
le_dist_p.fit(districts)
le_comm_p.fit(commodities)

state_p_col = np.random.choice(states, n_samples)
dist_p_col = np.random.choice(districts, n_samples)
comm_p_col = np.random.choice(commodities, n_samples)
month_col = np.random.randint(1, 13, n_samples)

# Formula based pricing
base_prices = {"Rice": 2200, "Wheat": 2100, "Maize": 1800, "Cotton": 6000, "Jute": 4500, "Potato": 1200, "Tomato": 1500, "Onion": 1600}
modal_prices = []
for i in range(n_samples):
    comm = comm_p_col[i]
    base = base_prices.get(comm, 2000)
    # Seasonal price variation (tomato/onion peaks in summer, etc.)
    seasonal_factor = 1.0 + 0.15 * np.sin(2 * np.pi * month_col[i] / 12)
    price = base * seasonal_factor + np.random.normal(0, 100)
    modal_prices.append(np.clip(price, 500, None))

df_price = pd.DataFrame({
    "state": le_state_p.transform(state_p_col),
    "district": le_dist_p.transform(dist_p_col),
    "commodity": le_comm_p.transform(comm_p_col),
    "month": month_col
})

price_model = RandomForestRegressor(n_estimators=50, random_state=42)
price_model.fit(df_price, modal_prices)

price_data = {
    "model": price_model,
    "le_state": le_state_p,
    "le_dist": le_dist_p,
    "le_comm": le_comm_p
}
with open(os.path.join(models_dir, "market_price_prediction.pkl"), "wb") as f:
    pickle.dump(price_data, f)
print("Market Price Prediction Model saved!")


# =====================================================
# 5. Crop Disease Detection Model
# =====================================================
print("Training Crop Disease Detection Model...")
# Let's create an image classifier based on color statistics (mean & std of R, G, B channels)
# Inputs: R_mean, G_mean, B_mean, R_std, G_std, B_std
# Output: Class label representing crop and disease (e.g. Potato___Early_blight, Tomato___Healthy, etc.)
disease_classes = [
    "Apple___Apple_scab", "Apple___Black_rot", "Apple___Healthy",
    "Potato___Early_blight", "Potato___Late_blight", "Potato___Healthy",
    "Tomato___Bacterial_spot", "Tomato___Early_blight", "Tomato___Late_blight", "Tomato___Target_Spot", "Tomato___Healthy"
]

n_disease_samples = 1000
X_disease = []
y_disease = []

for i in range(n_disease_samples):
    disease = np.random.choice(disease_classes)
    y_disease.append(disease)
    
    # Generate realistic color statistics depending on the disease
    if "Healthy" in disease:
        # Greenish leaves (higher green channel, lower red/blue)
        r_mean = np.random.uniform(40, 80)
        g_mean = np.random.uniform(120, 180)
        b_mean = np.random.uniform(40, 80)
    elif "Late_blight" in disease or "rot" in disease:
        # Dark brown/black spots (low overall intensities, darker color)
        r_mean = np.random.uniform(50, 90)
        g_mean = np.random.uniform(50, 90)
        b_mean = np.random.uniform(30, 60)
    elif "Early_blight" in disease or "spot" in disease:
        # Yellowish/brown spots (moderate red and green, lower blue)
        r_mean = np.random.uniform(100, 150)
        g_mean = np.random.uniform(90, 130)
        b_mean = np.random.uniform(40, 80)
    else:
        r_mean = np.random.uniform(70, 110)
        g_mean = np.random.uniform(90, 130)
        b_mean = np.random.uniform(50, 90)
        
    r_std = np.random.uniform(10, 40)
    g_std = np.random.uniform(10, 40)
    b_std = np.random.uniform(10, 40)
    
    X_disease.append([r_mean, g_mean, b_mean, r_std, g_std, b_std])

df_disease = pd.DataFrame(X_disease, columns=["R_mean", "G_mean", "B_mean", "R_std", "G_std", "B_std"])
disease_model = RandomForestClassifier(n_estimators=50, random_state=42)
disease_model.fit(df_disease, y_disease)

with open(os.path.join(models_dir, "disease_detection.pkl"), "wb") as f:
    pickle.dump(disease_model, f)
print("Crop Disease Detection Model saved!")

print("All ML models successfully trained and serialized!")
