import folium
import json

def create_india_weather_map(weather_df):
    """
    Create interactive Folium map of India
    with weather data for each city
    """
    
    # City coordinates
    city_coords = {
        "Hyderabad": (17.3850, 78.4867),
        "Bangalore": (12.9716, 77.5946),
        "Chennai": (13.0827, 80.2707),
        "Kochi": (9.9312, 76.2673),
        "Visakhapatnam": (17.6868, 83.2185),
        "Coimbatore": (11.0168, 76.9558),
        "Mysore": (12.2958, 76.6394),
        "Thiruvananthapuram": (8.5241, 76.9366),
        "Delhi": (28.7041, 77.1025),
        "Jaipur": (26.9124, 75.7873),
        "Lucknow": (26.8467, 80.9462),
        "Chandigarh": (30.7333, 76.7794),
        "Amritsar": (31.6340, 74.8723),
        "Jodhpur": (26.2389, 73.0243),
        "Agra": (27.1767, 78.0081),
        "Varanasi": (25.3176, 82.9739),
        "Mumbai": (19.0760, 72.8777),
        "Pune": (18.5204, 73.8567),
        "Ahmedabad": (23.0225, 72.5714),
        "Surat": (21.1702, 72.8311),
        "Nagpur": (21.1458, 79.0882),
        "Goa": (15.2993, 74.1240),
        "Vadodara": (22.3072, 73.1812),
        "Kolkata": (22.5726, 88.3639),
        "Bhubaneswar": (20.2961, 85.8245),
        "Patna": (25.5941, 85.1376),
        "Ranchi": (23.3441, 85.3096),
        "Guwahati": (26.1445, 91.7362),
        "Bhopal": (23.2599, 77.4126),
        "Indore": (22.7196, 75.8577),
        "Raipur": (21.2514, 81.6296),
        "Shimla": (31.1048, 77.1734),
        "Manali": (32.2432, 77.1892),
        "Dehradun": (30.3165, 78.0322),
        "Srinagar": (34.0837, 74.7973),
        "Darjeeling": (27.0360, 88.2627),
        "Gangtok": (27.3389, 88.6065),
        "Shillong": (25.5788, 91.8933),
        "Imphal": (24.8170, 93.9368),
        "Agartala": (23.8315, 91.2868),
        "Aizawl": (23.7307, 92.7173)
    }
    
    # Create base map centered on India
    india_map = folium.Map(
        location=[22.5, 82.0],
        zoom_start=5,
        tiles='CartoDB positron'
    )
    
    # Add title
    title_html = '''
    <div style="position: fixed; 
                top: 10px; left: 50%;
                transform: translateX(-50%);
                z-index: 1000;
                background-color: rgba(30,60,114,0.9);
                color: white;
                padding: 10px 20px;
                border-radius: 10px;
                font-family: Arial;
                font-size: 16px;
                font-weight: bold;
                text-align: center;">
        India Weather AI 2026<br>
        <span style="font-size:12px;">
        Super El Nino Intelligence Platform
        </span>
    </div>
    '''
    india_map.get_root().html.add_child(
        folium.Element(title_html))
    
    # Add markers for each city
    for _, row in weather_df.iterrows():
        city = row['City']
        if city not in city_coords:
            continue
            
        lat, lon = city_coords[city]
        temp = row['Temperature']
        humidity = row['Humidity']
        condition = row['Condition']
        deviation = row['El_Nino_Deviation']
        
        # Color based on temperature
        if temp > 42:
            color = 'darkred'
            icon_color = 'white'
        elif temp > 38:
            color = 'red'
            icon_color = 'white'
        elif temp > 34:
            color = 'orange'
            icon_color = 'white'
        elif temp > 28:
            color = 'green'
            icon_color = 'white'
        else:
            color = 'blue'
            icon_color = 'white'
        
        # Create popup content
        popup_html = f"""
        <div style="font-family: Arial; 
                    width: 200px;
                    padding: 10px;">
            <h3 style="color: #1e3c72; 
                       margin: 0 0 10px 0;">
                {city}
            </h3>
            <table style="width:100%; 
                         font-size:13px;">
                <tr>
                    <td>Temperature:</td>
                    <td><b>{temp}°C</b></td>
                </tr>
                <tr>
                    <td>Humidity:</td>
                    <td><b>{humidity}%</b></td>
                </tr>
                <tr>
                    <td>Condition:</td>
                    <td><b>{condition}</b></td>
                </tr>
                <tr>
                    <td>El Nino:</td>
                    <td><b style="color:red;">
                        +{deviation}°C
                    </b></td>
                </tr>
            </table>
            <div style="margin-top:8px;
                        padding:5px;
                        background:#f0f0f0;
                        border-radius:5px;
                        font-size:11px;">
                {get_map_alert(temp)}
            </div>
        </div>
        """
        
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(
                popup_html, max_width=220),
            tooltip=f"{city}: {temp}°C",
            icon=folium.Icon(
                color=color,
                icon_color=icon_color,
                icon='thermometer-half',
                prefix='fa'
            )
        ).add_to(india_map)
        
        # Add circle for heat intensity
        folium.CircleMarker(
            location=[lat, lon],
            radius=temp/5,
            color=get_circle_color(temp),
            fill=True,
            fill_opacity=0.2,
            weight=1
        ).add_to(india_map)
    
    # Add legend
    legend_html = '''
    <div style="position: fixed;
                bottom: 30px; right: 10px;
                z-index: 1000;
                background-color: white;
                padding: 15px;
                border-radius: 10px;
                border: 2px solid #1e3c72;
                font-family: Arial;
                font-size: 13px;">
        <b>Temperature Legend</b><br>
        <div style="margin-top:8px;">
            <span style="color:darkred;">●</span>
            Extreme > 42°C<br>
            <span style="color:red;">●</span>
            Very Hot 38-42°C<br>
            <span style="color:orange;">●</span>
            Hot 34-38°C<br>
            <span style="color:green;">●</span>
            Warm 28-34°C<br>
            <span style="color:blue;">●</span>
            Cool < 28°C<br>
        </div>
        <div style="margin-top:8px;
                    font-size:11px;
                    color:#666;">
            Circle size = heat intensity<br>
            Click marker for details
        </div>
    </div>
    '''
    india_map.get_root().html.add_child(
        folium.Element(legend_html))
    
    return india_map

def get_circle_color(temp):
    """Get circle color for heat intensity"""
    if temp > 42:
        return '#8B0000'
    elif temp > 38:
        return '#FF0000'
    elif temp > 34:
        return '#FF8C00'
    elif temp > 28:
        return '#FFD700'
    else:
        return '#00BFFF'

def get_map_alert(temp):
    """Get alert text for map popup"""
    if temp > 42:
        return "EXTREME HEAT EMERGENCY"
    elif temp > 38:
        return "HIGH HEAT WARNING"
    elif temp > 34:
        return "Heat Advisory Active"
    elif temp > 28:
        return "Normal Conditions"
    else:
        return "Cool & Pleasant"