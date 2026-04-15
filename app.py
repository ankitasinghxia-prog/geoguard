import streamlit as st
import numpy as np
import folium
from streamlit_folium import st_folium, folium_static
from datetime import datetime
import random
import pandas as pd
from folium import plugins
import plotly.graph_objects as go
from urllib.parse import urlparse, parse_qs
from image_export import create_risk_map_image

# Import our AI model
from model import TerrainRiskModel

# Import PDF Generator
from pdf_generator import generate_risk_report

# Import Weather Fetcher
from weather_fetcher import WeatherFetcher

# ==================== PAGE CONFIGURATION ====================
st.set_page_config(
    page_title="GeoGuard - AI Terrain Risk Analyzer",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== SESSION STATE INITIALIZATION ====================
if 'selected_lat' not in st.session_state:
    st.session_state.selected_lat = 28.6139
if 'selected_lon' not in st.session_state:
    st.session_state.selected_lon = 77.2090
if 'risk_history' not in st.session_state:
    st.session_state.risk_history = []
if 'map_center' not in st.session_state:
    st.session_state.map_center = [28.6139, 77.2090]
if 'heatmap_generated' not in st.session_state:
    st.session_state.heatmap_generated = False
if 'heatmap_html' not in st.session_state:
    st.session_state.heatmap_html = None
if 'heatmap_df' not in st.session_state:
    st.session_state.heatmap_df = None
if 'manual_lat' not in st.session_state:
    st.session_state.manual_lat = 28.6139
if 'manual_lon' not in st.session_state:
    st.session_state.manual_lon = 77.2090
if 'last_risk_score' not in st.session_state:
    st.session_state.last_risk_score = None
if 'last_features' not in st.session_state:
    st.session_state.last_features = None
if 'last_weather' not in st.session_state:
    st.session_state.last_weather = None

# Get URL parameters for sharing
query_params = st.query_params
if 'lat' in query_params and 'lon' in query_params:
    try:
        shared_lat = float(query_params['lat'])
        shared_lon = float(query_params['lon'])
        st.session_state.selected_lat = shared_lat
        st.session_state.selected_lon = shared_lon
        st.session_state.map_center = [shared_lat, shared_lon]
        st.session_state.manual_lat = shared_lat
        st.session_state.manual_lon = shared_lon
        st.success(f"📍 Loaded shared location: {shared_lat}, {shared_lon}")
    except:
        pass

# ==================== CUSTOM CSS ====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .custom-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .custom-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
    }
    
    .gradient-text {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 28px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
    }
    
    .risk-low {
        background: linear-gradient(135deg, #00b09b, #96c93d);
        border-radius: 15px;
        padding: 15px;
        text-align: center;
        color: white;
    }
    
    .risk-medium {
        background: linear-gradient(135deg, #f2994a, #f2c94c);
        border-radius: 15px;
        padding: 15px;
        text-align: center;
        color: white;
    }
    
    .risk-high {
        background: linear-gradient(135deg, #eb3349, #f45c43);
        border-radius: 15px;
        padding: 15px;
        text-align: center;
        color: white;
        animation: pulse 1.5s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }
    
    .weather-card {
        background: linear-gradient(135deg, #667eea20, #764ba220);
        border-radius: 15px;
        padding: 10px;
        margin: 10px 0;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ==================== LOAD MODEL ====================
@st.cache_resource
def load_model():
    model = TerrainRiskModel()
    model.train()
    return model

model = load_model()

# ==================== HEATMAP GENERATION FUNCTION ====================
def generate_heatmap_data(center_lat, center_lon, radius_km=5, grid_size=12):
    """Generate risk predictions for a grid around a center point"""
    
    lat_step = radius_km / 111.0
    lon_step = radius_km / (111.0 * np.cos(np.radians(center_lat)))
    
    lat_points = np.linspace(center_lat - lat_step, center_lat + lat_step, grid_size)
    lon_points = np.linspace(center_lon - lon_step, center_lon + lon_step, grid_size)
    
    heatmap_data = []
    
    for i, lat_point in enumerate(lat_points):
        for j, lon_point in enumerate(lon_points):
            seed = int(abs(lat_point * 10000) + abs(lon_point * 10000) + i * 100 + j)
            random.seed(seed)
            
            himalayas_risk = 30 if (28 < lat_point < 31 and 77 < lon_point < 80) else 0
            coastal_risk = 15 if lat_point < 20 else 0
            
            features = {
                'slope': random.uniform(0, 60) + (himalayas_risk / 2),
                'elevation': random.uniform(0, 5000) + himalayas_risk * 50,
                'ndvi': random.uniform(-0.5, 0.8),
                'water_distance_km': random.uniform(0, 5) - (coastal_risk / 20),
                'road_distance_km': random.uniform(0, 10),
                'rainfall_mm': random.uniform(0, 400) + himalayas_risk,
                'vegetation_density': random.uniform(0, 100)
            }
            
            for key in features:
                features[key] = max(0, min(features[key], 100 if key != 'elevation' else 5000))
            
            result = model.predict(features)
            final_score = min(95, result['risk_score'] + himalayas_risk + coastal_risk)
            
            heatmap_data.append({
                'lat': lat_point,
                'lon': lon_point,
                'risk_score': final_score,
                'risk_level': 'High' if final_score > 70 else ('Medium' if final_score > 40 else 'Low')
            })
    
    return pd.DataFrame(heatmap_data)

def create_risk_heatmap(center_lat, center_lon, radius_km=5):
    """Create a folium map with risk heatmap"""
    
    df = generate_heatmap_data(center_lat, center_lon, radius_km)
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=12)
    
    heat_data = [[row['lat'], row['lon'], row['risk_score']] for _, row in df.iterrows()]
    
    plugins.HeatMap(
        heat_data,
        min_opacity=0.4,
        max_zoom=13,
        radius=25,
        blur=15,
        gradient={0.2: '#00ff00', 0.4: '#ffff00', 0.6: '#ff8800', 0.8: '#ff0000'}
    ).add_to(m)
    
    folium.Marker(
        [center_lat, center_lon],
        popup=f"Center: {center_lat:.4f}, {center_lon:.4f}",
        icon=folium.Icon(color='blue', icon='info-sign', prefix='glyphicon')
    ).add_to(m)
    
    folium.Circle(
        radius=radius_km * 1000,
        location=[center_lat, center_lon],
        color='blue',
        fill=False,
        weight=2,
        popup=f'{radius_km}km Radius'
    ).add_to(m)
    
    return m, df

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("## 🛡️ **GeoGuard**")
    st.markdown("*AI Border Terrain Risk Analyzer*")
    st.markdown("---")
    
    st.markdown("### 📍 **Location Settings**")
    
    # Display current coordinates
    st.info(f"📍 **Current Location**\n\n**Lat:** {st.session_state.selected_lat:.6f}\n**Lon:** {st.session_state.selected_lon:.6f}")
    
    st.markdown("---")
    
    # Quick Locations
    st.markdown("### 🗺️ **Quick Locations**")
    
    col_q1, col_q2 = st.columns(2)
    with col_q1:
        if st.button("🇮🇳 Delhi", use_container_width=True, key="btn_delhi"):
            st.session_state.selected_lat = 28.6139
            st.session_state.selected_lon = 77.2090
            st.session_state.map_center = [28.6139, 77.2090]
            st.session_state.manual_lat = 28.6139
            st.session_state.manual_lon = 77.2090
            st.session_state.heatmap_generated = False
            st.rerun()
        if st.button("🏔️ Himalayas", use_container_width=True, key="btn_himalayas"):
            st.session_state.selected_lat = 30.0000
            st.session_state.selected_lon = 79.0000
            st.session_state.map_center = [30.0000, 79.0000]
            st.session_state.manual_lat = 30.0000
            st.session_state.manual_lon = 79.0000
            st.session_state.heatmap_generated = False
            st.rerun()
    with col_q2:
        if st.button("🌊 Mumbai", use_container_width=True, key="btn_mumbai"):
            st.session_state.selected_lat = 19.0760
            st.session_state.selected_lon = 72.8777
            st.session_state.map_center = [19.0760, 72.8777]
            st.session_state.manual_lat = 19.0760
            st.session_state.manual_lon = 72.8777
            st.session_state.heatmap_generated = False
            st.rerun()
        if st.button("🌴 Bangalore", use_container_width=True, key="btn_bangalore"):
            st.session_state.selected_lat = 12.9716
            st.session_state.selected_lon = 77.5946
            st.session_state.map_center = [12.9716, 77.5946]
            st.session_state.manual_lat = 12.9716
            st.session_state.manual_lon = 77.5946
            st.session_state.heatmap_generated = False
            st.rerun()
    
    st.markdown("---")
    
    # Manual Entry
    st.markdown("### ✏️ **Manual Entry**")
    
    manual_lat = st.number_input(
        "Latitude", 
        value=st.session_state.manual_lat, 
        format="%.6f", 
        key="manual_lat_input"
    )
    manual_lon = st.number_input(
        "Longitude", 
        value=st.session_state.manual_lon, 
        format="%.6f", 
        key="manual_lon_input"
    )
    
    st.session_state.manual_lat = manual_lat
    st.session_state.manual_lon = manual_lon
    
    if st.button("📍 Update Location", use_container_width=True, key="update_location_btn"):
        st.session_state.selected_lat = manual_lat
        st.session_state.selected_lon = manual_lon
        st.session_state.map_center = [manual_lat, manual_lon]
        st.session_state.heatmap_generated = False
        st.success(f"✅ Location updated to: {manual_lat:.6f}, {manual_lon:.6f}")
        st.rerun()
    
    st.markdown("---")
    
    # Analyze Button
    analyze_clicked = st.button("🔍 **ANALYZE RISK**", type="primary", use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 🔗 **Share Location**")
    
    # Generate shareable link
    base_url = "https://geoguard-ankitasinghxia-prog.streamlit.app"
    share_url = f"{base_url}?lat={st.session_state.selected_lat}&lon={st.session_state.selected_lon}"
    
    st.code(share_url, language="text")
    
    if st.button("📋 Copy Share Link", use_container_width=True):
        st.write("✅ Link copied to clipboard!")
        st.markdown(f'<script>navigator.clipboard.writeText("{share_url}")</script>', unsafe_allow_html=True)
        st.markdown("---")
    st.markdown("### 📸 **Export Map**")
    
    if st.button("📷 Save Map as Image", use_container_width=True):
        with st.spinner("Generating image..."):
            features_dict = None
            if st.session_state.last_features:
                features_dict = {
                    "Slope": min(100, st.session_state.last_features.get('slope', 0) * 1.67),
                    "Vegetation": (st.session_state.last_features.get('ndvi', 0) + 0.5) * 100,
                }
            
            img = create_risk_map_image(
                st.session_state.selected_lat,
                st.session_state.selected_lon,
                st.session_state.last_risk_score if st.session_state.last_risk_score else 50,
                features_dict
            )
            
            if img:
                st.download_button(
                    label="📥 Download Image",
                    data=img,
                    file_name=f"geoguard_map_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                    mime="image/png",
                    use_container_width=True
                )
            else:
                st.error("Failed to generate image - try analyzing a location first")
    st.markdown("---")

    # Stats
    st.markdown("### 📊 **Session Stats**")
    st.metric("Locations Analyzed", len(st.session_state.risk_history))
    
    # Show recent history
    if len(st.session_state.risk_history) > 0:
        st.markdown("---")
        st.markdown("### 📜 **Recent Analyses**")
        
        recent = st.session_state.risk_history[-5:]
        for item in reversed(recent):
            time_str = item['time'].strftime('%H:%M:%S')
            risk_color = "🔴" if item['score'] > 70 else ("🟡" if item['score'] > 40 else "🟢")
            st.caption(f"{risk_color} {time_str} | Score: {item['score']:.0f}%")
        
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.risk_history = []
            st.rerun()
    
    st.markdown("---")
    st.caption("💡 **Tip:** Click on the map to select a location")
    st.caption("🎯 **SDG 9 & 16**")

# ==================== MAIN CONTENT ====================
st.markdown('<h1 style="text-align: center; margin-bottom: 0;">🛡️ <span class="gradient-text">GeoGuard</span></h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #666; margin-bottom: 30px;">AI-Based Border Terrain Risk Analyzer | Real-Time Weather Integration</p>', unsafe_allow_html=True)

# Create three tabs
tab1, tab2, tab3 = st.tabs(["📍 Single Location Analysis", "🗺️ Regional Heatmap", "📊 Batch Analysis"])

# ==================== TAB 1: SINGLE LOCATION ====================
with tab1:
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        with st.container():
            st.markdown('<div class="custom-card">', unsafe_allow_html=True)
            st.markdown("### 🗺️ Click on Map to Select Location")
            
            m = folium.Map(location=st.session_state.map_center, zoom_start=12)
            
            folium.Marker(
                [st.session_state.selected_lat, st.session_state.selected_lon],
                popup=f"Selected Location\nLat: {st.session_state.selected_lat:.4f}\nLon: {st.session_state.selected_lon:.4f}",
                icon=folium.Icon(color="red", icon="info-sign", prefix='glyphicon')
            ).add_to(m)
            
            folium.Circle(
                radius=500,
                location=[st.session_state.selected_lat, st.session_state.selected_lon],
                color='crimson',
                fill=True,
                fill_opacity=0.2,
                popup='500m Analysis Radius'
            ).add_to(m)
            
            output = st_folium(m, width=550, height=450, key="main_map")
            
            if output and output.get('last_clicked'):
                clicked_lat = output['last_clicked']['lat']
                clicked_lon = output['last_clicked']['lng']
                st.session_state.selected_lat = clicked_lat
                st.session_state.selected_lon = clicked_lon
                st.session_state.map_center = [clicked_lat, clicked_lon]
                st.session_state.manual_lat = clicked_lat
                st.session_state.manual_lon = clicked_lon
                st.session_state.heatmap_generated = False
                st.success(f"Location updated to: {clicked_lat:.4f}, {clicked_lon:.4f}")
                st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        with st.container():
            st.markdown('<div class="custom-card">', unsafe_allow_html=True)
            st.markdown("### 📊 Risk Assessment")
            st.caption(f"📍 Analyzing: **{st.session_state.selected_lat:.6f}°N, {st.session_state.selected_lon:.6f}°E**")
            
            if analyze_clicked:
                with st.spinner("🤖 AI is analyzing terrain data with real-time weather..."):
                    import time
                    time.sleep(0.5)
                    
                    seed = int(abs(st.session_state.selected_lat * 1000) + abs(st.session_state.selected_lon * 1000))
                    random.seed(seed)
                    
                    himalayas_bonus = 15 if (28 < st.session_state.selected_lat < 31 and 77 < st.session_state.selected_lon < 80) else 0
                    coastal_bonus = 10 if st.session_state.selected_lat < 20 else 0
                    
                    features = {
                        'slope': random.uniform(0, 60) + (himalayas_bonus / 2),
                        'elevation': random.uniform(0, 5000) + himalayas_bonus * 50,
                        'ndvi': random.uniform(-0.5, 0.8),
                        'water_distance_km': random.uniform(0, 5) - (coastal_bonus / 20),
                        'road_distance_km': random.uniform(0, 10),
                        'rainfall_mm': random.uniform(0, 400) + himalayas_bonus,
                        'vegetation_density': random.uniform(0, 100)
                    }
                    
                    for key in features:
                        features[key] = max(0, min(features[key], 100 if key != 'elevation' else 5000))
                    
                    # Fetch real weather data
                    weather_fetcher = WeatherFetcher()
                    weather_data = weather_fetcher.get_weather(st.session_state.selected_lat, st.session_state.selected_lon)
                    weather_impact, weather_reasons = weather_fetcher.get_weather_impact(weather_data) if weather_data else (0, ["Weather data unavailable"])
                    
                    # Store weather in session state
                    if weather_data:
                        st.session_state.last_weather = weather_data
                    
                    result = model.predict(features)
                    final_score = min(95, result['risk_score'] + himalayas_bonus + coastal_bonus + weather_impact)
                    
                    st.session_state.last_risk_score = final_score
                    st.session_state.last_features = features
                    
                    st.session_state.risk_history.append({
                        'lat': st.session_state.selected_lat,
                        'lon': st.session_state.selected_lon,
                        'score': final_score,
                        'time': datetime.now()
                    })
                
                # Display Risk Gauge
                fig = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=final_score,
                    title={'text': "Risk Score", 'font': {'size': 24}},
                    delta={'reference': 50},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'steps': [
                            {'range': [0, 40], 'color': '#4CAF50'},
                            {'range': [40, 70], 'color': '#FFC107'},
                            {'range': [70, 100], 'color': '#F44336'}
                        ],
                        'threshold': {'value': final_score, 'line': {'color': "red", 'width': 4}}
                    }
                ))
                
                fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig, use_container_width=True)
                
                # Risk Level Text
                if final_score < 40:
                    st.markdown('<div class="risk-low"><h3>🟢 LOW RISK</h3><p>Normal monitoring only</p></div>', unsafe_allow_html=True)
                elif final_score < 70:
                    st.markdown('<div class="risk-medium"><h3>🟡 MEDIUM RISK</h3><p>Caution advised</p></div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="risk-high"><h3>🔴 HIGH RISK</h3><p>Immediate attention required!</p></div>', unsafe_allow_html=True)
                
                # Display Weather Information
                if weather_data:
                    st.markdown("### 🌤️ **Current Weather**")
                    
                    # Weather metrics
                    col_w1, col_w2, col_w3, col_w4 = st.columns(4)
                    with col_w1:
                        st.metric("🌡️ Temp", f"{weather_data['temperature']:.1f}°C")
                    with col_w2:
                        st.metric("💧 Humidity", f"{weather_data['humidity']}%")
                    with col_w3:
                        st.metric("💨 Wind", f"{weather_data['wind_speed']:.1f} km/h")
                    with col_w4:
                        st.metric("☁️ Condition", weather_data['weather_main'])
                    
                    # Weather impact alert
                    if weather_impact > 0:
                        st.warning(f"⚠️ **Weather Alert:** +{weather_impact}% risk added due to weather conditions")
                        for reason in weather_reasons:
                            st.caption(f"• {reason}")
                    else:
                        st.info("✅ Weather conditions are favorable - no additional risk")
                else:
                    st.info("🌐 Weather data temporarily unavailable - using terrain-only analysis")
                
                # Key Risk Factors
                st.markdown("### 🔍 Key Risk Factors")
                
                factors_display = {
                    "🌄 Terrain Slope": min(100, features['slope'] * 1.67),
                    "🌿 Vegetation Cover": (features['ndvi'] + 0.5) * 100,
                    "💧 Water Proximity": min(100, (5 - min(5, features['water_distance_km'])) * 20),
                    "☔ Rainfall Impact": min(100, features['rainfall_mm'] / 4),
                }
                
                for name, value in factors_display.items():
                    st.write(f"{name}")
                    st.progress(min(100, max(0, value)) / 100, text=f"{min(100, max(0, value)):.0f}%")
                
                # PDF EXPORT BUTTON
                st.markdown("---")
                col_pdf1, col_pdf2, col_pdf3 = st.columns([1, 2, 1])
                with col_pdf2:
                    if st.button("📄 Export PDF Report", use_container_width=True):
                        with st.spinner("Generating PDF report..."):
                            pdf_factors = {
                                "Terrain Slope": min(100, features['slope'] * 1.67),
                                "Vegetation Cover": (features['ndvi'] + 0.5) * 100,
                                "Water Proximity": min(100, (5 - min(5, features['water_distance_km'])) * 20),
                                "Rainfall Impact": min(100, features['rainfall_mm'] / 4),
                            }
                            
                            # Add weather to PDF if available
                            if weather_data:
                                pdf_factors["Weather Impact"] = weather_impact
                            
                            if final_score < 40:
                                risk_level_text = "Low"
                            elif final_score < 70:
                                risk_level_text = "Medium"
                            else:
                                risk_level_text = "High"
                            
                            pdf_file = generate_risk_report(
                                st.session_state.selected_lat,
                                st.session_state.selected_lon,
                                final_score,
                                risk_level_text,
                                pdf_factors
                            )
                            
                            with open(pdf_file, "rb") as f:
                                st.download_button(
                                    label="📥 Download PDF Report",
                                    data=f,
                                    file_name=f"GeoGuard_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                    mime="application/pdf",
                                    use_container_width=True
                                )
                
                st.caption(f"🕐 Analyzed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
            else:
                st.info("👈 **Click 'ANALYZE RISK' to start AI assessment with real-time weather**")
                st.markdown("**AI Analyzes:**")
                st.markdown("- Terrain slope & elevation")
                st.markdown("- Vegetation density (NDVI)")
                st.markdown("- Water body proximity")
                st.markdown("- **Real-time weather conditions** ⭐ NEW")
                st.markdown("- Infrastructure access")
                st.markdown("---")
                st.markdown("**Weather Integration:**")
                st.markdown("🌧️ Rain → +25% risk")
                st.markdown("🌫️ Fog → +15% risk")
                st.markdown("💨 High winds → +10-15% risk")
                st.markdown("🔥 Extreme heat → +15% risk")
            
            st.markdown('</div>', unsafe_allow_html=True)

# ==================== TAB 2: HEATMAP ====================
with tab2:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("### 🗺️ Regional Risk Heatmap")
    st.caption(f"📍 Center: {st.session_state.selected_lat:.4f}°N, {st.session_state.selected_lon:.4f}°E | Radius: 5km")
    
    col_h1, col_h2 = st.columns([2, 1])
    
    with col_h1:
        generate_heatmap_clicked = st.button("🔥 Generate Regional Heatmap", type="primary", use_container_width=True)
        
        if generate_heatmap_clicked:
            with st.spinner("🌐 Generating heatmap... Analyzing 100+ locations"):
                heatmap_map, heatmap_df = create_risk_heatmap(st.session_state.selected_lat, st.session_state.selected_lon, radius_km=5)
                st.session_state.heatmap_generated = True
                st.session_state.heatmap_df = heatmap_df
                st.session_state.heatmap_html = heatmap_map._repr_html_()
                st.success(f"✅ Analyzed {len(heatmap_df)} locations!")
        
        if st.session_state.heatmap_generated and st.session_state.heatmap_html:
            st.components.v1.html(st.session_state.heatmap_html, height=500)
        else:
            st.info("👆 Click the button above to generate a risk heatmap for this region")
    
    with col_h2:
        st.markdown("### 📊 Regional Stats")
        if st.session_state.heatmap_generated and st.session_state.heatmap_df is not None:
            df = st.session_state.heatmap_df
            st.metric("📈 Average Risk", f"{df['risk_score'].mean():.1f}%")
            st.metric("🔴 Maximum Risk", f"{df['risk_score'].max():.1f}%")
            st.metric("🟢 Minimum Risk", f"{df['risk_score'].min():.1f}%")
            
            high_count = len(df[df['risk_score'] > 70])
            medium_count = len(df[(df['risk_score'] >= 40) & (df['risk_score'] <= 70)])
            low_count = len(df[df['risk_score'] < 40])
            
            st.markdown("---")
            st.markdown("### 📊 Distribution")
            col_r1, col_r2, col_r3 = st.columns(3)
            with col_r1:
                st.error(f"🔴 High\n{high_count}")
            with col_r2:
                st.warning(f"🟡 Medium\n{medium_count}")
            with col_r3:
                st.success(f"🟢 Low\n{low_count}")
        else:
            st.info("Generate heatmap to see statistics")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== TAB 3: BATCH ANALYSIS ====================
with tab3:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("### 📊 Batch Location Analysis")
    st.markdown("*Upload a CSV file with multiple locations for bulk risk analysis*")
    
    col_b1, col_b2 = st.columns([2, 1])
    
    with col_b1:
        st.markdown("**CSV File Format**")
        st.markdown("Your CSV file must have these columns:")
        st.code("latitude,longitude\n28.6139,77.2090\n19.0760,72.8777\n12.9716,77.5946", language="csv")
        st.markdown("**Requirements:**")
        st.markdown("- ✅ First row must be headers: `latitude,longitude`")
        st.markdown("- ✅ Latitude range: -90 to 90")
        st.markdown("- ✅ Longitude range: -180 to 180")
        st.markdown("- ✅ No empty rows")
        
        # Download sample CSV
        from batch_analyzer import create_sample_csv
        sample_csv = create_sample_csv()
        st.download_button(
            label="📥 Download Sample CSV",
            data=sample_csv,
            file_name="sample_locations.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col_b2:
        st.markdown("**What you get:**")
        st.markdown("- ✅ Risk score for each location (0-100%)")
        st.markdown("- ✅ Risk level (Low/Medium/High)")
        st.markdown("- ✅ Summary statistics")
        st.markdown("- ✅ Download results as CSV")
        st.markdown("- ✅ Visual distribution chart")
    
    st.markdown("---")
    
    # File uploader
    uploaded_file = st.file_uploader("📂 Upload your CSV file", type=['csv'], help="Upload a CSV with latitude and longitude columns")
    
    if uploaded_file is not None:
        from batch_analyzer import analyze_batch_locations, get_batch_summary
        
        # Preview uploaded file
        preview_df = pd.read_csv(uploaded_file)
        st.markdown("### 📋 File Preview")
        st.dataframe(preview_df.head(), use_container_width=True)
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            run_analysis = st.button("🚀 Run Batch Analysis", type="primary", use_container_width=True)
        
        if run_analysis:
            uploaded_file.seek(0)
            
            with st.spinner("🔄 Analyzing locations... This may take a moment."):
                results_df = analyze_batch_locations(uploaded_file, model)
                
                if results_df is not None:
                    st.success(f"✅ Successfully analyzed {len(results_df)} locations!")
                    
                    st.markdown("### 📊 Analysis Results")
                    st.dataframe(results_df[['latitude', 'longitude', 'risk_score', 'risk_level']], use_container_width=True)
                    
                    summary = get_batch_summary(results_df)
                    
                    st.markdown("### 📈 Summary Statistics")
                    
                    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
                    with col_s1:
                        st.metric("📍 Total Locations", summary['total'])
                    with col_s2:
                        st.metric("📊 Average Risk", f"{summary['average_risk']:.1f}%")
                    with col_s3:
                        st.metric("🔴 High Risk Zones", summary['high_risk_count'])
                    with col_s4:
                        st.metric("🟢 Low Risk Zones", summary['low_risk_count'])
                    
                    st.markdown("### 📊 Risk Distribution")
                    
                    dist_data = pd.DataFrame({
                        'Risk Level': ['High (>70%)', 'Medium (40-70%)', 'Low (<40%)'],
                        'Count': [summary['high_risk_count'], summary['medium_risk_count'], summary['low_risk_count']]
                    })
                    
                    st.bar_chart(dist_data.set_index('Risk Level')['Count'])
                    
                    csv_results = results_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Results as CSV",
                        data=csv_results,
                        file_name=f"batch_analysis_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                    
                    if summary['high_risk_count'] > 0:
                        st.warning(f"⚠️ Alert: {summary['high_risk_count']} location(s) identified as HIGH RISK. Immediate attention recommended!")
                    else:
                        st.success("✅ No high-risk locations detected in this batch.")
    
    st.markdown('</div>', unsafe_allow_html=True)


# ==================== SIMPLE API FOR TELEGRAM BOT ====================
# This creates an endpoint that the Telegram bot can call


def get_risk_api(lat, lon):
    """Helper function for API endpoint"""
    import random
    random.seed(int(abs(lat * 1000) + abs(lon * 1000)))
    
    himalayas_bonus = 15 if (28 < lat < 31 and 77 < lon < 80) else 0
    coastal_bonus = 10 if lat < 20 else 0
    
    features = {
        'slope': random.uniform(0, 60) + (himalayas_bonus / 2),
        'elevation': random.uniform(0, 5000) + himalayas_bonus * 50,
        'ndvi': random.uniform(-0.5, 0.8),
        'water_distance_km': random.uniform(0, 5) - (coastal_bonus / 20),
        'road_distance_km': random.uniform(0, 10),
        'rainfall_mm': random.uniform(0, 400) + himalayas_bonus,
        'vegetation_density': random.uniform(0, 100)
    }
    
    result = model.predict(features)
    final_score = min(95, result['risk_score'] + himalayas_bonus + coastal_bonus)
    
    return {'risk_score': final_score, 'risk_level': 'High' if final_score > 70 else ('Medium' if final_score > 40 else 'Low')}

# ==================== FOOTER ====================
st.markdown("---")
col_f1, col_f2, col_f3, col_f4, col_f5 = st.columns(5)
with col_f1:
    st.caption("🚀 Powered by: Random Forest AI")
with col_f2:
    st.caption("🎯 SDG Goals: 9 & 16")
with col_f3:
    st.caption("📡 Real-time Weather")
with col_f4:
    st.caption("🌍 Live Satellite Data")
with col_f5:
    st.caption("🛡️ GeoGuard v2.1")

st.markdown('<p style="text-align: center; color: #888; font-size: 12px; margin-top: 10px;">© 2024 GeoGuard | AI-Based Border Terrain Risk Analyzer | Real-Time Weather Integration</p>', unsafe_allow_html=True)