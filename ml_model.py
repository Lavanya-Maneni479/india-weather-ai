import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

def generate_training_data():
    """
    Generate realistic historical weather 
    training data for Indian cities
    """
    np.random.seed(42)
    
    # Simulate 2 years of daily data
    # for training the model
    n_samples = 730
    
    # Features
    months = np.random.randint(1, 13, n_samples)
    humidity = np.random.uniform(20, 95, n_samples)
    wind_speed = np.random.uniform(1, 12, n_samples)
    pressure = np.random.uniform(990, 1020, n_samples)
    cloud_cover = np.random.uniform(0, 100, n_samples)
    
    # Realistic temperature based on month
    # India seasonal pattern
    base_temps = {
        1: 18, 2: 21, 3: 27, 4: 33,
        5: 37, 6: 35, 7: 32, 8: 31,
        9: 31, 10: 28, 11: 23, 12: 19
    }
    
    temperatures = []
    for i in range(n_samples):
        base = base_temps[months[i]]
        # Add realistic variations
        temp = (base 
                + np.random.normal(0, 3)
                - (humidity[i] - 50) * 0.05
                + wind_speed[i] * 0.2
                - cloud_cover[i] * 0.05
                + np.random.normal(0, 1))
        temperatures.append(round(temp, 1))
    
    df = pd.DataFrame({
        'month': months,
        'humidity': humidity,
        'wind_speed': wind_speed,
        'pressure': pressure,
        'cloud_cover': cloud_cover,
        'temperature': temperatures
    })
    
    return df

def train_model():
    """Train Random Forest model"""
    df = generate_training_data()
    
    features = ['month', 'humidity', 
                'wind_speed', 'pressure',
                'cloud_cover']
    target = 'temperature'
    
    X = df[features]
    y = df[target]
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        random_state=42
    )
    model.fit(X_scaled, y)
    
    return model, scaler, features

def predict_7_days(current_weather, model, 
                   scaler, features):
    """
    Predict temperature for next 7 days
    based on current weather conditions
    """
    from datetime import datetime, timedelta
    
    predictions = []
    today = datetime.now()
    
    # Base values from current weather
    base_humidity = current_weather['humidity']
    base_wind = current_weather['wind']
    base_pressure = current_weather.get(
        'pressure', 1005)
    base_cloud = current_weather.get(
        'clouds', 20)
    
    for day in range(1, 8):
        future_date = today + timedelta(days=day)
        month = future_date.month
        
        # Add small daily variations
        humidity_var = base_humidity + np.random.normal(0, 5)
        humidity_var = max(10, min(100, humidity_var))
        
        wind_var = base_wind + np.random.normal(0, 1)
        wind_var = max(0, wind_var)
        
        pressure_var = base_pressure + np.random.normal(0, 2)
        cloud_var = base_cloud + np.random.normal(0, 10)
        cloud_var = max(0, min(100, cloud_var))
        
        # Create feature vector
        features_dict = {
            'month': month,
            'humidity': humidity_var,
            'wind_speed': wind_var,
            'pressure': pressure_var,
            'cloud_cover': cloud_var
        }
        
        X_pred = pd.DataFrame([features_dict])
        X_scaled = scaler.transform(X_pred)
        
        temp_pred = model.predict(X_scaled)[0]
        
        # Adjust for El Nino effect
        elnino_factor = 1.15
        temp_pred = round(temp_pred * elnino_factor, 1)
        
        predictions.append({
            'date': future_date.strftime('%d %b'),
            'day': future_date.strftime('%A'),
            'predicted_temp': temp_pred,
            'humidity': round(humidity_var, 1),
            'condition': get_condition(
                temp_pred, humidity_var)
        })
    
    return predictions

def get_condition(temp, humidity):
    """Get weather condition from temp/humidity"""
    if humidity > 80:
        return "Humid & Hot" if temp > 30 else "Humid"
    elif temp > 40:
        return "Extreme Heat"
    elif temp > 35:
        return "Very Hot"
    elif temp > 30:
        return "Hot"
    elif temp > 25:
        return "Warm"
    elif temp > 20:
        return "Pleasant"
    else:
        return "Cool"