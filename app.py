import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from ml_model import train_model, predict_7_days
from india_map import create_india_weather_map
from streamlit_folium import folium_static

# ============================================
# PAGE CONFIGURATION
# ============================================

st.set_page_config(
    page_title="India Weather AI 2026",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CUSTOM CSS STYLING
# ============================================

st.markdown("""
<style>
    .main {
        background-color: #0E1117;
    }
    .metric-card {
        background: linear-gradient(
            135deg, #1e3c72, #2a5298);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin: 5px;
    }
    .warning-red {
        background: linear-gradient(
            135deg, #c0392b, #e74c3c);
        padding: 15px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
    }
    .warning-orange {
        background: linear-gradient(
            135deg, #d35400, #e67e22);
        padding: 15px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
    }
    .warning-green {
        background: linear-gradient(
            135deg, #1e8449, #27ae60);
        padding: 15px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
    }
    .crop-card {
        background: linear-gradient(
            135deg, #1a472a, #2d6a4f);
        padding: 15px;
        border-radius: 10px;
        color: white;
        margin: 5px 0;
    }
    .vacation-card {
        background: linear-gradient(
            135deg, #154360, #1a5276);
        padding: 15px;
        border-radius: 10px;
        color: white;
        margin: 5px 0;
    }
    .chat-message {
        padding: 10px 15px;
        border-radius: 10px;
        margin: 5px 0;
    }
    .user-message {
        background-color: #1e3c72;
        color: white;
        text-align: right;
    }
    .bot-message {
        background-color: #1a1a2e;
        color: white;
        text-align: left;
        border-left: 3px solid #00BFFF;
    }
    h1, h2, h3 {
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# API KEY & CONSTANTS
# ============================================

API_KEY = "397b9b15f0aa5b00394aeefd2a2e3bd9"

INDIAN_CITIES = [
    "Hyderabad", "Bangalore", "Chennai",
    "Mumbai", "Delhi", "Kolkata",
    "Jaipur", "Ahmedabad", "Pune",
    "Lucknow", "Chandigarh", "Kochi",
    "Visakhapatnam", "Nagpur", "Indore",
    "Bhopal", "Patna", "Bhubaneswar",
    "Guwahati", "Srinagar", "Shimla",
    "Manali", "Darjeeling", "Goa",
    "Varanasi", "Agra", "Amritsar",
    "Jodhpur", "Udaipur", "Mysore"
]

# ============================================
# HELPER FUNCTIONS
# ============================================

@st.cache_data(ttl=1800)
def get_weather(city):
    """Fetch weather for a city"""
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': f"{city},IN",
            'appid': API_KEY,
            'units': 'metric'
        }
        response = requests.get(url, params=params)
        data = response.json()

        if response.status_code == 200:
            return {
                'city': city,
                'temp': round(data['main']['temp'], 1),
                'feels_like': round(
                    data['main']['feels_like'], 1),
                'humidity': data['main']['humidity'],
                'wind': data['wind']['speed'],
                'condition': data['weather'][0][
                    'description'].title(),
                'min_temp': round(
                    data['main']['temp_min'], 1),
                'max_temp': round(
                    data['main']['temp_max'], 1),
                'pressure': data['main']['pressure'],
                'clouds': data['clouds']['all'],
                'icon': data['weather'][0]['icon']
            }
    except:
        return None

@st.cache_data(ttl=1800)
def get_forecast(city):
    """Get 5-day forecast"""
    try:
        url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {
            'q': f"{city},IN",
            'appid': API_KEY,
            'units': 'metric',
            'cnt': 40
        }
        response = requests.get(url, params=params)
        data = response.json()

        forecasts = []
        if response.status_code == 200:
            for item in data['list']:
                forecasts.append({
                    'datetime': item['dt_txt'],
                    'temp': item['main']['temp'],
                    'humidity': item['main']['humidity'],
                    'condition': item['weather'][0][
                        'description'].title(),
                    'wind': item['wind']['speed']
                })
        return pd.DataFrame(forecasts)
    except:
        return None

def get_crop_recommendation(temp, humidity, condition):
    """Crop recommendations based on weather"""
    crops = []
    tips = []

    if temp < 15:
        crops = ["Wheat", "Mustard", "Peas",
                 "Potato", "Spinach", "Carrot"]
        tips = ["Perfect rabi season",
                "Ensure frost protection for seedlings",
                "Good time for root vegetables"]
    elif temp < 25:
        crops = ["Rice", "Maize", "Soybean",
                 "Groundnut", "Tomato", "Onion"]
        tips = ["Ideal growing conditions",
                "Monitor for pest activity",
                "Regular irrigation recommended"]
    elif temp < 35:
        crops = ["Cotton", "Sugarcane",
                 "Jowar", "Bajra", "Turmeric",
                 "Ginger"]
        tips = ["Kharif season crops doing well",
                "Ensure adequate water supply",
                "Watch for heat stress signs"]
    else:
        crops = ["Bitter Gourd", "Okra", "Drumstick",
                 "Curry Leaf", "Aloe Vera"]
        tips = ["Extreme heat — use shade nets",
                "Early morning irrigation only",
                "Drought resistant varieties preferred",
                "El Nino impact — water conservation critical"]

    if humidity > 80:
        crops.extend(["Tea", "Coffee", "Cardamom"])
        tips.append("High humidity — watch for fungal disease")
    elif humidity < 30:
        crops.extend(["Millets", "Sorghum", "Pearl Millet"])
        tips.append("Low humidity — drip irrigation recommended")

    return crops, tips

def get_health_precautions(temp, humidity, condition):
    """Health precautions based on weather"""
    if temp > 42:
        level = "EXTREME HEAT EMERGENCY"
        color = "warning-red"
        precautions = [
            "Stay indoors 11AM to 5PM strictly",
            "Drink 4-5 litres water daily",
            "Wear light loose cotton clothes",
            "Never leave children or pets in cars",
            "Watch for heat stroke: no sweating,",
            "confusion, high body temp = emergency!",
            "Keep wet cloth on head if going out"
        ]
        foods = [
            "Coconut water every 2-3 hours",
            "Watermelon and cucumber",
            "Aam Panna (raw mango drink)",
            "Sattu with water and salt",
            "Buttermilk (Chaas) 3x daily",
            "AVOID: Tea, coffee, alcohol",
            "AVOID: Spicy and fried foods"
        ]
    elif temp > 37:
        level = "HIGH HEAT WARNING"
        color = "warning-orange"
        precautions = [
            "Limit outdoor activities in afternoon",
            "Stay hydrated throughout the day",
            "Use umbrella or hat outside",
            "Apply sunscreen SPF 50+",
            "Check on elderly family members"
        ]
        foods = [
            "Fresh lime water with salt",
            "Watermelon and melons",
            "Coconut water",
            "Light meals — avoid heavy food",
            "AVOID: Heavy non-veg meals"
        ]
    elif 'rain' in condition.lower():
        level = "MONSOON PRECAUTIONS"
        color = "warning-orange"
        precautions = [
            "Carry umbrella always",
            "Avoid flooded roads and areas",
            "Check for mosquito breeding",
            "Wear waterproof footwear",
            "Keep medicines dry",
            "Avoid street food"
        ]
        foods = [
            "Hot ginger tea 2x daily",
            "Turmeric milk at night",
            "Garlic in all cooking",
            "Hot soups and dal",
            "Tulsi kadha for immunity",
            "AVOID: Raw salads, cut fruits"
        ]
    else:
        level = "NORMAL CONDITIONS"
        color = "warning-green"
        precautions = [
            "Good weather for outdoor activities",
            "Stay active and exercise regularly",
            "Maintain regular sleep schedule",
            "Keep weather app handy for updates"
        ]
        foods = [
            "Balanced seasonal meals",
            "Regular water intake",
            "Fresh seasonal fruits",
            "Include vegetables in every meal"
        ]

    return level, color, precautions, foods

def get_vacation_spots(temp, humidity, condition):
    """Vacation recommendations"""
    spots = []

    if temp > 38:
        spots = [
            {"name": "Manali, Himachal Pradesh",
             "why": "Cool mountain air 15-20C",
             "best_for": "Trekking, skiing, river rafting",
             "distance": "From Delhi: 570 km"},
            {"name": "Ooty, Tamil Nadu",
             "why": "Nilgiri hills, 18-22C",
             "best_for": "Tea gardens, boat ride, nature walks",
             "distance": "From Bangalore: 270 km"},
            {"name": "Munnar, Kerala",
             "why": "Tea plantations, cool climate",
             "best_for": "Trekking, wildlife, tea tasting",
             "distance": "From Kochi: 130 km"},
            {"name": "Coorg, Karnataka",
             "why": "Coffee plantation, misty hills",
             "best_for": "Coffee tours, waterfalls, spa",
             "distance": "From Bangalore: 250 km"}
        ]
    elif 'rain' in condition.lower():
        spots = [
            {"name": "Coorg, Karnataka",
             "why": "Beautiful waterfalls in monsoon",
             "best_for": "Nature, coffee, waterfalls",
             "distance": "From Bangalore: 250 km"},
            {"name": "Meghalaya",
             "why": "Living root bridges, misty hills",
             "best_for": "Photography, caves, trekking",
             "distance": "From Guwahati: 100 km"},
            {"name": "Kerala Backwaters",
             "why": "Lush green in monsoon",
             "best_for": "Houseboat, Ayurveda, nature",
             "distance": "From Kochi: 50 km"}
        ]
    else:
        spots = [
            {"name": "Goa",
             "why": "Perfect beach weather",
             "best_for": "Beach, water sports, heritage",
             "distance": "From Mumbai: 600 km"},
            {"name": "Jaipur, Rajasthan",
             "why": "Best time to visit forts",
             "best_for": "Forts, culture, desert safari",
             "distance": "From Delhi: 280 km"},
            {"name": "Andaman Islands",
             "why": "Crystal clear waters",
             "best_for": "Snorkelling, scuba, beach",
             "distance": "Flight from Chennai: 2 hrs"},
            {"name": "Rishikesh, Uttarakhand",
             "why": "Adventure capital of India",
             "best_for": "Rafting, yoga, camping",
             "distance": "From Delhi: 240 km"}
        ]

    return spots

def weather_chatbot(question, weather_data):
    """Simple rule-based weather chatbot"""
    question = question.lower()

    if not weather_data:
        return "Please search for a city first!"

    city = weather_data['city']
    temp = weather_data['temp']
    humidity = weather_data['humidity']
    condition = weather_data['condition']
    wind = weather_data['wind']

    # Temperature questions
    if any(word in question for word in
           ['temperature', 'temp', 'hot', 'cold', 'warm']):
        if temp > 40:
            return (f"It is extremely hot in {city} "
                    f"at {temp}C! This is dangerous heat. "
                    f"Stay indoors and drink lots of water. "
                    f"Super El Nino is causing these extreme "
                    f"temperatures across India in 2026!")
        elif temp > 35:
            return (f"It is very warm in {city} at {temp}C. "
                    f"Avoid going out in the afternoon. "
                    f"Stay hydrated!")
        else:
            return (f"Temperature in {city} is {temp}C. "
                    f"Conditions are {condition}. "
                    f"Fairly comfortable weather!")

    # Rain questions
    elif any(word in question for word in
             ['rain', 'umbrella', 'wet', 'monsoon']):
        if 'rain' in condition.lower():
            return (f"Yes it is raining in {city}! "
                    f"Condition: {condition}. "
                    f"Please carry an umbrella and "
                    f"avoid flooded areas. "
                    f"Avoid street food during rain!")
        else:
            return (f"No rain currently in {city}. "
                    f"Condition is {condition}. "
                    f"But check the 5-day forecast "
                    f"for rain predictions!")

    # Crop questions
    elif any(word in question for word in
             ['crop', 'farm', 'agriculture', 'plant', 'grow']):
        crops, tips = get_crop_recommendation(
            temp, humidity, condition)
        return (f"For {city}'s current weather "
                f"({temp}C, {humidity}% humidity), "
                f"best crops are: "
                f"{', '.join(crops[:4])}. "
                f"Key tip: {tips[0]}")

    # Health questions
    elif any(word in question for word in
             ['health', 'sick', 'disease', 'precaution',
              'safe', 'food', 'eat']):
        level, _, precautions, foods = \
            get_health_precautions(temp, humidity, condition)
        return (f"Health status for {city}: {level}. "
                f"Top precaution: {precautions[0]}. "
                f"Recommended food: {foods[0]}. "
                f"Stay safe!")

    # Vacation questions
    elif any(word in question for word in
             ['vacation', 'travel', 'visit', 'trip',
              'holiday', 'tour']):
        spots = get_vacation_spots(temp, humidity, condition)
        top = spots[0]
        return (f"Given {city}'s weather ({temp}C, "
                f"{condition}), I recommend visiting "
                f"{top['name']}! {top['why']}. "
                f"Best for: {top['best_for']}. "
                f"{top['distance']}.")

    # Humidity questions
    elif any(word in question for word in
             ['humid', 'humidity', 'dry', 'moisture']):
        if humidity > 80:
            return (f"Very high humidity in {city} "
                    f"at {humidity}%! "
                    f"Feels uncomfortable and muggy. "
                    f"Use light breathable clothes.")
        elif humidity < 30:
            return (f"Very dry in {city} - "
                    f"only {humidity}% humidity! "
                    f"Drink extra water. "
                    f"Use moisturiser for skin care.")
        else:
            return (f"Humidity in {city} is {humidity}%. "
                    f"Fairly comfortable conditions!")

    # El Nino questions
    elif any(word in question for word in
             ['el nino', 'elnino', 'climate', 'global',
              'warming']):
        return (f"Super El Nino 2026 is significantly "
                f"impacting India! "
                f"India's average temperature is 33.1C, "
                f"well above normal. "
                f"{city} is at {temp}C. "
                f"Expect hotter summers, erratic rainfall, "
                f"and drought conditions in some regions. "
                f"Water conservation is critical!")

    # Wind questions
    elif any(word in question for word in
             ['wind', 'breeze', 'storm', 'cyclone']):
        if wind > 8:
            return (f"Strong winds in {city} "
                    f"at {wind} m/s! "
                    f"Avoid outdoor activities. "
                    f"Secure loose objects.")
        else:
            return (f"Wind speed in {city} "
                    f"is {wind} m/s. "
                    f"Normal conditions.")

    # General greeting
    elif any(word in question for word in
             ['hello', 'hi', 'hey', 'namaste']):
        return (f"Namaste! I am your India Weather AI "
                f"assistant for 2026! "
                f"Currently showing weather for {city}. "
                f"Ask me about temperature, rain, crops, "
                f"health, or vacation spots!")

    else:
        return (f"I can answer questions about: "
                f"Temperature, Rain, Crops, "
                f"Health precautions, Vacation spots, "
                f"Humidity, Wind, and El Nino impact. "
                f"Current weather in {city}: "
                f"{temp}C, {condition}. "
                f"What would you like to know?")

# ============================================
# MAIN APP LAYOUT
# ============================================

# Header
st.markdown("""
<div style='text-align: center; 
            padding: 20px 0;
            background: linear-gradient(
                135deg, #1e3c72, #2a5298);
            border-radius: 15px;
            margin-bottom: 20px;'>
    <h1 style='color: white; font-size: 2.5em;'>
        India Weather AI 2026
    </h1>
    <p style='color: #AED6F1; font-size: 1.2em;'>
        Super El Nino Intelligence Platform
    </p>
    <p style='color: #85C1E9;'>
        Live Weather | Crop Advisory | 
        Health Alerts | Vacation Planner | AI Chatbot
    </p>
</div>
""", unsafe_allow_html=True)

# El Nino Alert Banner
st.markdown("""
<div style='background: linear-gradient(
                135deg, #922B21, #C0392B);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 20px;
            color: white;'>
    <b>SUPER EL NINO ALERT 2026:</b>
    India average temperature 33.1C — 
    above normal by 3-5C | 
    Extreme heat warnings in 15+ states | 
    Water conservation critical
</div>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("Search Weather")
st.sidebar.markdown("---")

selected_city = st.sidebar.selectbox(
    "Select Indian City",
    INDIAN_CITIES,
    index=0
)

custom_city = st.sidebar.text_input(
    "Or type any city name:",
    placeholder="e.g. Tirupati, Nashik..."
)

if custom_city:
    search_city = custom_city
else:
    search_city = selected_city

search_btn = st.sidebar.button(
    "Get Weather",
    type="primary",
    use_container_width=True
)

st.sidebar.markdown("---")
st.sidebar.markdown("""
**About this app:**
- Live weather data
- Super El Nino analysis
- ML weather prediction
- Interactive India map
- Crop recommendations
- Health precautions
- Vacation planning
- AI weather chatbot

**ML Model:** Random Forest
**Data:** OpenWeatherMap API
**Made by:** Lavanya Maneni
**Year:** 2026
""")

# Initialize session state
if 'weather_data' not in st.session_state:
    st.session_state.weather_data = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'forecast_data' not in st.session_state:
    st.session_state.forecast_data = None

# Fetch weather on button click
if search_btn:
    with st.spinner(f"Fetching weather for "
                    f"{search_city}..."):
        st.session_state.weather_data = \
            get_weather(search_city)
        st.session_state.forecast_data = \
            get_forecast(search_city)

# Display weather if available
if st.session_state.weather_data:
    w = st.session_state.weather_data

    # Main tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "Current Weather",
    "5-Day Forecast",
    "ML Prediction",
    "India Map",
    "Crop Advisory",
    "Health & Safety",
    "Vacation Planner",
    "AI Chatbot"
])

    # ==================
    # TAB 1: CURRENT WEATHER
    # ==================
    with tab1:
        st.subheader(f"Current Weather — {w['city']}")
        st.caption(f"Last updated: "
                   f"{datetime.now().strftime('%d %b %Y, %I:%M %p')}")

        # Metric cards
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric("Temperature",
                      f"{w['temp']}C",
                      f"Feels {w['feels_like']}C")
        with col2:
            st.metric("Humidity",
                      f"{w['humidity']}%",
                      "Moisture level")
        with col3:
            st.metric("Wind Speed",
                      f"{w['wind']} m/s",
                      "Wind")
        with col4:
            st.metric("Condition",
                      w['condition'],
                      "Sky")
        with col5:
            st.metric("Cloud Cover",
                      f"{w['clouds']}%",
                      "Clouds")

        st.markdown("---")

        # Temperature gauge
        col1, col2 = st.columns(2)

        with col1:
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=w['temp'],
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Temperature (C)",
                       'font': {'color': 'white'}},
                delta={'reference': 28,
                       'increasing': {'color': "red"},
                       'decreasing': {'color': "blue"}},
                gauge={
                    'axis': {'range': [0, 50],
                             'tickcolor': "white"},
                    'bar': {'color': "darkred"},
                    'bgcolor': "gray",
                    'bordercolor': "white",
                    'steps': [
                        {'range': [0, 15],
                         'color': '#00BFFF'},
                        {'range': [15, 25],
                         'color': '#00FF7F'},
                        {'range': [25, 35],
                         'color': '#FFD700'},
                        {'range': [35, 50],
                         'color': '#FF4500'}
                    ],
                    'threshold': {
                        'line': {'color': "white",
                                 'width': 4},
                        'thickness': 0.75,
                        'value': 40
                    }
                }
            ))
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font={'color': 'white'}
            )
            st.plotly_chart(fig, 
                           use_container_width=True)

        with col2:
            fig2 = go.Figure(go.Indicator(
                mode="gauge+number",
                value=w['humidity'],
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Humidity (%)",
                       'font': {'color': 'white'}},
                gauge={
                    'axis': {'range': [0, 100],
                             'tickcolor': "white"},
                    'bar': {'color': "#45B7D1"},
                    'bgcolor': "gray",
                    'bordercolor': "white",
                    'steps': [
                        {'range': [0, 30],
                         'color': '#FF6B35'},
                        {'range': [30, 60],
                         'color': '#4ECDC4'},
                        {'range': [60, 100],
                         'color': '#45B7D1'}
                    ]
                }
            ))
            fig2.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font={'color': 'white'}
            )
            st.plotly_chart(fig2,
                           use_container_width=True)

        # El Nino context
        st.markdown("---")
        st.subheader("Super El Nino Impact Analysis")

        normal_temp = 28.5
        diff = round(w['temp'] - normal_temp, 1)

        if diff > 5:
            st.error(
                f"CRITICAL: {w['city']} is {diff}C ABOVE "
                f"normal! Severe El Nino impact detected!")
        elif diff > 2:
            st.warning(
                f"WARNING: {w['city']} is {diff}C above "
                f"normal. Moderate El Nino impact.")
        else:
            st.success(
                f"INFO: {w['city']} temperature is "
                f"relatively normal. "
                f"Difference from average: {diff}C")

    # ==================
    # TAB 2: 5-DAY FORECAST
    # ==================
    with tab2:
        st.subheader(f"5-Day Forecast — {w['city']}")

        if st.session_state.forecast_data is not None:
            df_forecast = st.session_state.forecast_data

            # Temperature forecast line chart
            fig = px.line(
                df_forecast,
                x='datetime',
                y='temp',
                title=f'Temperature Forecast — {w["city"]}',
                labels={'temp': 'Temperature (C)',
                        'datetime': 'Date & Time'},
                color_discrete_sequence=['#FF4500']
            )
            fig.add_hline(
                y=40,
                line_dash="dash",
                line_color="red",
                annotation_text="Heat Wave Threshold 40C"
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(14,17,23,0.8)',
                font_color='white'
            )
            st.plotly_chart(fig,
                           use_container_width=True)

            # Humidity forecast
            fig2 = px.area(
                df_forecast,
                x='datetime',
                y='humidity',
                title=f'Humidity Forecast — {w["city"]}',
                labels={'humidity': 'Humidity (%)',
                        'datetime': 'Date & Time'},
                color_discrete_sequence=['#45B7D1']
            )
            fig2.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(14,17,23,0.8)',
                font_color='white'
            )
            st.plotly_chart(fig2,
                           use_container_width=True)

            # Forecast table
            st.subheader("Detailed Forecast Table")
            st.dataframe(
                df_forecast.style.background_gradient(
                    subset=['temp'],
                    cmap='RdYlBu_r'
                ),
                use_container_width=True
            )
    # ==================
    # TAB 3: ML PREDICTION
    # ==================
    with tab3:
        st.subheader(
            f"ML Weather Prediction — {w['city']}")
        st.caption(
            "Random Forest model predicting "
            "next 7 days temperature")

        with st.spinner("Training ML model..."):
            model, scaler, features = train_model()
            predictions = predict_7_days(
                w, model, scaler, features)

        st.markdown("### 7-Day Temperature Forecast")

        dates = [p['date'] for p in predictions]
        temps = [p['predicted_temp']
                 for p in predictions]

        fig_ml = go.Figure()

        fig_ml.add_trace(go.Scatter(
            x=dates,
            y=temps,
            mode='lines+markers+text',
            name='Predicted Temperature',
            line=dict(color='#FF4500', width=3),
            marker=dict(size=10),
            text=[f"{t}C" for t in temps],
            textposition='top center'
        ))

        fig_ml.add_hline(
            y=w['temp'],
            line_dash="dash",
            line_color="blue",
            annotation_text=f"Current: {w['temp']}C"
        )

        fig_ml.add_hline(
            y=40,
            line_dash="dot",
            line_color="red",
            annotation_text="Heat Wave 40C"
        )

        fig_ml.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(14,17,23,0.8)',
            font_color='white',
            title=f'7-Day ML Prediction — {w["city"]}',
            xaxis_title='Date',
            yaxis_title='Temperature (C)'
        )

        st.plotly_chart(fig_ml,
                        use_container_width=True)

        pred_df = pd.DataFrame(predictions)
        st.markdown("### Detailed Predictions")
        st.dataframe(
            pred_df.style.background_gradient(
                subset=['predicted_temp'],
                cmap='RdYlBu_r'
            ),
            use_container_width=True
        )

        st.caption(
            "Model: Random Forest Regressor | "
            "Features: Month, Humidity, Wind, "
            "Pressure, Cloud Cover | "
            "El Nino factor: +15%")

    # ==================
    # TAB 4: INDIA MAP
    # ==================
    with tab4:
        st.subheader("India Weather Map 2026")
        st.caption(
            "Interactive map — click any city "
            "for detailed weather info")

        map_data = {
            'City': ['Hyderabad', 'Bangalore',
                     'Chennai', 'Kochi', 'Delhi',
                     'Mumbai', 'Kolkata', 'Jaipur',
                     'Agra', 'Manali', 'Darjeeling',
                     'Guwahati', 'Bhopal', 'Pune',
                     'Ahmedabad', 'Visakhapatnam',
                     'Lucknow', 'Chandigarh',
                     'Jodhpur', 'Shimla',
                     'Srinagar', 'Patna',
                     'Bhubaneswar', 'Nagpur',
                     'Indore', 'Raipur', 'Ranchi',
                     'Imphal', 'Shillong', 'Aizawl'],
            'Temperature': [37.2, 32.1, 38.5, 31.2,
                            41.5, 34.0, 36.5, 42.8,
                            44.2, 37.7, 16.3, 32.5,
                            38.9, 35.8, 41.2, 36.8,
                            40.2, 38.9, 43.1, 28.5,
                            29.8, 38.2, 37.8, 39.8,
                            39.5, 37.2, 35.2, 24.5,
                            22.4, 19.8],
            'Humidity': [36, 52, 68, 78, 46, 59,
                         65, 22, 8, 46, 50, 75,
                         35, 45, 28, 55, 35, 28,
                         18, 45, 55, 42, 70, 32,
                         28, 48, 55, 68, 72, 94],
            'Condition': ['Few Clouds', 'Partly Cloudy',
                          'Clear Sky', 'Scattered Clouds',
                          'Haze', 'Haze',
                          'Partly Cloudy', 'Clear Sky',
                          'Clear Sky', 'Broken Clouds',
                          'Clear Sky', 'Scattered Clouds',
                          'Clear Sky', 'Scattered Clouds',
                          'Haze', 'Clear Sky',
                          'Haze', 'Few Clouds',
                          'Clear Sky', 'Clear Sky',
                          'Few Clouds', 'Clear Sky',
                          'Scattered Clouds', 'Clear Sky',
                          'Haze', 'Clear Sky',
                          'Scattered Clouds', 'Partly Cloudy',
                          'Scattered Clouds', 'Overcast'],
            'El_Nino_Deviation': [8.7, 3.6, 10.0, 2.7,
                                   13.0, 5.5, 8.0, 14.3,
                                   15.7, 9.2, -12.2, 4.0,
                                   10.4, 7.3, 12.7, 8.3,
                                   11.7, 10.4, 14.6, 0.0,
                                   1.3, 9.7, 9.3, 11.3,
                                   11.0, 8.7, 6.7, -4.0,
                                   -6.1, -8.7]
        }

        map_df = pd.DataFrame(map_data)
        india_map = create_india_weather_map(map_df)
        folium_static(india_map,
                      width=900, height=600)

        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Cities Mapped", "30")
        with col2:
            avg_temp = sum(
                map_data['Temperature'])/len(
                map_data['Temperature'])
            st.metric("Avg Temperature",
                      f"{avg_temp:.1f}C")
        with col3:
            extreme = sum(
                1 for t in map_data['Temperature']
                if t > 40)
            st.metric("Extreme Heat Cities",
                      str(extreme))
        with col4:
            st.metric("El Nino Impact",
                      "+6.4C above normal")

    # ==================
    # TAB 5: CROP ADVISORY
    # ==================
    with tab5:
        st.subheader(f"Crop Advisory — {w['city']}")
        st.caption(
            f"Based on: {w['temp']}C, "
            f"{w['humidity']}% humidity, "
            f"{w['condition']}")

        crops, tips = get_crop_recommendation(
            w['temp'], w['humidity'], w['condition'])

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Recommended Crops")
            for crop in crops:
                st.markdown(f"""
                <div class='crop-card'>
                    <b>{crop}</b>
                </div>
                """, unsafe_allow_html=True)

        with col2:
            st.markdown("### Farming Tips")
            for tip in tips:
                st.info(tip)

        # El Nino farming alert
        if w['temp'] > 38:
            st.error(
                "SUPER EL NINO FARMING ALERT: "
                "Extreme heat affecting crop yield! "
                "Use mulching to retain soil moisture. "
                "Shift to drought-resistant varieties. "
                "Irrigate during early morning only. "
                "Consider crop insurance immediately!"
            )

    # ==================
    # TAB 6: HEALTH & SAFETY
    # ==================
    with tab6:
        st.subheader(f"Health & Safety — {w['city']}")

        level, color, precautions, foods = \
            get_health_precautions(
                w['temp'],
                w['humidity'],
                w['condition']
            )

        st.markdown(f"""
        <div class='{color}'>
            <h3>Status: {level}</h3>
            <p>Temperature: {w['temp']}C | 
               Humidity: {w['humidity']}%</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Precautions")
            for p in precautions:
                st.warning(p)

        with col2:
            st.markdown("### Recommended Foods")
            for f in foods:
                if "AVOID" in f:
                    st.error(f)
                else:
                    st.success(f)

    # ==================
    # TAB 7: VACATION PLANNER
    # ==================
    with tab7:
        st.subheader("Vacation Recommendations")
        st.caption(
            f"Based on current weather in {w['city']}: "
            f"{w['temp']}C, {w['condition']}")

        spots = get_vacation_spots(
            w['temp'],
            w['humidity'],
            w['condition']
        )

        for spot in spots:
            st.markdown(f"""
            <div class='vacation-card'>
                <h3>{spot['name']}</h3>
                <p><b>Why visit now:</b> {spot['why']}</p>
                <p><b>Best for:</b> {spot['best_for']}</p>
                <p><b>Distance:</b> {spot['distance']}</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("")

    # ==================
    # TAB 8: AI CHATBOT
    # ==================
    with tab8:
        st.subheader("India Weather AI Chatbot")
        st.caption(
            "Ask me anything about weather, "
            "crops, health, or vacation!")

        # Chat display
        chat_container = st.container()

        with chat_container:
            for chat in st.session_state.chat_history:
                if chat['role'] == 'user':
                    st.markdown(f"""
                    <div class='chat-message user-message'>
                        You: {chat['message']}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class='chat-message bot-message'>
                        AI: {chat['message']}
                    </div>
                    """, unsafe_allow_html=True)

        # Input
        col1, col2 = st.columns([4, 1])

        with col1:
            user_input = st.text_input(
                "Ask a question:",
                placeholder=(
                    "e.g. Is it safe to go outside? "
                    "What crops should I grow? "
                    "Where should I travel?"),
                key="chat_input"
            )

        with col2:
            send_btn = st.button(
                "Ask",
                type="primary",
                use_container_width=True
            )
            clear_btn = st.button(
                "Clear",
                use_container_width=True
            )

        if send_btn and user_input:
            response = weather_chatbot(
                user_input,
                st.session_state.weather_data
            )
            st.session_state.chat_history.append(
                {'role': 'user',
                 'message': user_input}
            )
            st.session_state.chat_history.append(
                {'role': 'bot',
                 'message': response}
            )
            st.rerun()

        if clear_btn:
            st.session_state.chat_history = []
            st.rerun()

        # Quick question buttons
        st.markdown("### Quick Questions:")
        qcol1, qcol2, qcol3 = st.columns(3)

        with qcol1:
            if st.button("How hot is it?"):
                response = weather_chatbot(
                    "temperature",
                    st.session_state.weather_data
                )
                st.session_state.chat_history.append(
                    {'role': 'user',
                     'message': "How hot is it?"}
                )
                st.session_state.chat_history.append(
                    {'role': 'bot',
                     'message': response}
                )
                st.rerun()

        with qcol2:
            if st.button("Best crops to grow?"):
                response = weather_chatbot(
                    "crops",
                    st.session_state.weather_data
                )
                st.session_state.chat_history.append(
                    {'role': 'user',
                     'message': "Best crops to grow?"}
                )
                st.session_state.chat_history.append(
                    {'role': 'bot',
                     'message': response}
                )
                st.rerun()

        with qcol3:
            if st.button("Where to travel?"):
                response = weather_chatbot(
                    "vacation",
                    st.session_state.weather_data
                )
                st.session_state.chat_history.append(
                    {'role': 'user',
                     'message': "Where to travel?"}
                )
                st.session_state.chat_history.append(
                    {'role': 'bot',
                     'message': response}
                )
                st.rerun()

else:
    # Welcome screen
    st.markdown("""
    <div style='text-align: center; 
                padding: 60px 20px;'>
        <h2 style='color: #AED6F1;'>
            Welcome to India Weather AI 2026
        </h2>
        <p style='color: #85C1E9; font-size: 1.2em;'>
            Search for any Indian city to get:
        </p>
        <br>
        <div style='display: grid; 
                    grid-template-columns: 
                        repeat(3, 1fr); 
                    gap: 20px; 
                    max-width: 800px; 
                    margin: 0 auto;'>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("Live weather data for 30+ cities")
        st.info("5-day forecast with charts")
    with col2:
        st.success("Crop recommendations")
        st.success("Health & safety alerts")
    with col3:
        st.warning("Vacation spot suggestions")
        st.warning("AI weather chatbot")

    st.markdown("---")
    st.markdown(
        "**Search for a city in the sidebar to begin!**"
    )
    