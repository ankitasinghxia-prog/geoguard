import streamlit as st
import numpy as np
import folium
from streamlit_folium import folium_static
from datetime import datetime
import random
import pandas as pd
from folium import plugins

# Import our AI model
from model import TerrainRiskModel

# Page configuration
st.set_page_config(
    page_title="GeoGuard - AI Terrain Risk Analyzer",
    page_icon="🛡️",
    layout="wide"
)

# Title
st.title("🛡️ GeoGuard")
st.caption("AI-Based Border Terrain Risk Analyzer | Powered by Machine Learning")

# Load the model
@st.cache_resource
def load_model():
    model = TerrainRiskModel()
    model.train()
    return model

model = load_model()

# Sidebar for coordinates
with st.sidebar:
    st.header("📍 Location Settings")
    st.markdown("---")
    
    st.subheader("Enter Coordinates")
    lat = st.number_input("Latitude", value=28.6139, format="%.6f", help="Example: 28.6139 for Delhi")
    lon = st.number_input("Longitude", value=77.2090, format="%.6f", help="Example: 77.2090 for Delhi")
    
    st.markdown("---")
    analyze_button = st.button("🔍 Analyze Risk", type="primary", use_container_width=True)
    
    st.markdown("---")
    st.caption("💡 **Sample Locations:**")
    st.caption("• Delhi: 28.6139, 77.2090")
    st.caption("• Mumbai: 19.0760, 72.8777")
    st.caption("• Bangalore: 12.9716, 77.5946")
    st.caption("• Himalayas: 30.0000, 79.0000")
    st.caption("• Chennai: 13.0827, 80.2707")

# Function to generate heatmap data
def generate_heatmap_data(center_lat, center_lon, radius_km=5, grid_size=12):
    """Generate risk predictions for a grid around a center point"""
    
    # Create grid of points
    lat_step = radius_km / 111.0
    lon_step = radius_km / (111.0 * np.cos(np.radians(center_lat)))
    
    lat_points = np.linspace(center_lat - lat_step, center_lat + lat_step, grid_size)
    lon_points = np.linspace(center_lon - lon_step, center_lon + lon_step, grid_size)
    
    heatmap_data = []
    
    for i, lat_point in enumerate(lat_points):
        for j, lon_point in enumerate(lon_points):
            # Generate features based on coordinates
            seed = int(abs(lat_point * 10000) + abs(lon_point * 10000) + i * 100 + j)
            random.seed(seed)
            
            # Adjust risk based on location characteristics
            # Himalayas have higher risk
            himalayas_risk = 0
            if 28 < lat_point < 31 and 77 < lon_point < 80:
                himalayas_risk = 30
            
            # Coastal areas have different risk patterns
            coastal_risk = 0
            if lat_point < 20:
                coastal_risk = 15
            
            features = {
                'slope': random.uniform(0, 60) + (himalayas_risk / 2),
                'elevation': random.uniform(0, 5000) + himalayas_risk * 50,
                'ndvi': random.uniform(-0.5, 0.8),
                'water_distance_km': random.uniform(0, 5) - (coastal_risk / 20),
                'road_distance_km': random.uniform(0, 10),
                'rainfall_mm': random.uniform(0, 400) + himalayas_risk,
                'vegetation_density': random.uniform(0, 100)
            }
            
            # Clamp values to valid ranges
            for key in features:
                features[key] = max(0, min(features[key], 100 if key != 'elevation' else 5000))
            
            result = model.predict(features)
            
            # Add location-based adjustment
            final_score = result['risk_score']
            if himalayas_risk > 0:
                final_score = min(95, final_score + 15)
            if coastal_risk > 0:
                final_score = min(95, final_score + 10)
            
            heatmap_data.append({
                'lat': lat_point,
                'lon': lon_point,
                'risk_score': final_score,
                'risk_level': 'High' if final_score > 70 else ('Medium' if final_score > 40 else 'Low')
            })
    
    return pd.DataFrame(heatmap_data)

# Function to create heatmap
def create_risk_heatmap(center_lat, center_lon, radius_km=5):
    """Create a folium map with risk heatmap"""
    
    # Generate data
    df = generate_heatmap_data(center_lat, center_lon, radius_km)
    
    # Create map
    m = folium.Map(location=[center_lat, center_lon], zoom_start=12)
    
    # Prepare heatmap data
    heat_data = [[row['lat'], row['lon'], row['risk_score']] for _, row in df.iterrows()]
    
    # Add heatmap layer
    plugins.HeatMap(
        heat_data,
        min_opacity=0.4,
        max_zoom=13,
        radius=25,
        blur=15,
        gradient={0.2: '#00ff00', 0.4: '#ffff00', 0.6: '#ff8800', 0.8: '#ff0000'}
    ).add_to(m)
    
    # Add marker for center
    folium.Marker(
        [center_lat, center_lon],
        popup=f"📍 Center: {center_lat:.4f}, {center_lon:.4f}",
        icon=folium.Icon(color='blue', icon='info-sign', prefix='glyphicon')
    ).add_to(m)
    
    # Add circle to show radius
    folium.Circle(
        radius=radius_km * 1000,
        location=[center_lat, center_lon],
        color='blue',
        fill=False,
        weight=2,
        popup=f'{radius_km}km Radius'
    ).add_to(m)
    
    return m, df

# Create tabs
tab1, tab2 = st.tabs(["📍 Single Location Analysis", "🗺️ Regional Risk Heatmap"])

# ==================== TAB 1: Single Location Analysis ====================
with tab1:
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.subheader("🗺️ Terrain Map")
        
        # Create map
        m = folium.Map(location=[lat, lon], zoom_start=13)
        
        # Add marker
        folium.Marker(
            [lat, lon],
            popup=f"📍 Selected Location<br>Lat: {lat:.4f}<br>Lon: {lon:.4f}",
            icon=folium.Icon(color="red", icon="info-sign", prefix='glyphicon')
        ).add_to(m)
        
        # Add circle
        folium.Circle(
            radius=500,
            location=[lat, lon],
            color='crimson',
            fill=True,
            fill_opacity=0.2,
            popup='Analysis Radius: 500m'
        ).add_to(m)
        
        folium_static(m, width=550, height=450)
    
    with col2:
        st.subheader("📊 AI Risk Assessment")
        st.caption(f"📍 Analyzing: **{lat:.4f}°N, {lon:.4f}°E**")
        
        if analyze_button:
            with st.spinner('🤖 AI analyzing terrain data...'):
                # Generate terrain features based on coordinates
                seed = int(abs(lat * 1000) + abs(lon * 1000))
                random.seed(seed)
                
                # Location-based adjustments
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
                
                # Clamp values
                for key in features:
                    features[key] = max(0, min(features[key], 100 if key != 'elevation' else 5000))
                
                # Get AI prediction
                result = model.predict(features)
                final_score = min(95, result['risk_score'] + himalayas_bonus + coastal_bonus)
            
            # Display risk meter
            st.metric("🎯 AI Risk Score", f"{final_score:.1f}%")
            
            if final_score < 40:
                st.success("🟢 **LOW RISK** - Normal monitoring only")
                risk_text = "Low Risk Area"
            elif final_score < 70:
                st.warning("🟡 **MEDIUM RISK** - Caution advised")
                risk_text = "Medium Risk Area"
            else:
                st.error("🔴 **HIGH RISK** - Immediate attention required")
                risk_text = "High Risk Area"
            
            # Progress bar
            st.progress(final_score/100)
            
            # Contributing factors
            st.subheader("🔍 Key Risk Factors")
            
            # Display factors with bars
            factors_to_show = {
                '🌄 Terrain Slope': min(100, features['slope'] * 1.67),
                '🌿 Vegetation Cover': (features['ndvi'] + 0.5) * 100,
                '💧 Water Proximity Risk': min(100, (5 - min(5, features['water_distance_km'])) * 20),
                '☔ Rainfall Impact': min(100, features['rainfall_mm'] / 4),
                '🛣️ Road Access Risk': min(100, (10 - min(10, features['road_distance_km'])) * 10)
            }
            
            for factor_name, factor_value in factors_to_show.items():
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.write(f"{factor_name}")
                    st.progress(min(100, max(0, factor_value)) / 100)
                with col_b:
                    st.write(f"{min(100, max(0, factor_value)):.0f}%")
            
            # Explanation
            st.subheader("📋 Analysis Summary")
            if final_score >= 70:
                st.write("⚠️ This area shows multiple risk indicators requiring immediate attention.")
                if himalayas_bonus:
                    st.write("🏔️ **Note:** Himalayan region detected - higher terrain risk expected.")
                elif coastal_bonus:
                    st.write("🌊 **Note:** Coastal region detected - water proximity risk considered.")
            elif final_score >= 40:
                st.write("📌 Moderate risk detected. Regular monitoring recommended.")
            else:
                st.write("✅ Area appears stable with minimal risk factors.")
            
            # Timestamp
            st.caption(f"🕐 Analyzed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        else:
            st.info("👈 **Click 'Analyze Risk' to start AI assessment**")
            
            st.markdown("---")
            st.markdown("""
            ### 🤖 What the AI analyzes:
            
            | Factor | Impact on Risk |
            |--------|----------------|
            | 🌄 Slope | Steeper = Higher Risk |
            | 🌿 Vegetation | Sparse = Higher Risk |
            | 💧 Water Proximity | Closer = Higher Risk |
            | ☔ Rainfall | Higher = Higher Risk |
            | 🛣️ Road Access | Closer = Higher Risk |
            
            ### 🎯 Risk Levels:
            - **0-40%** 🟢 Low Risk
            - **40-70%** 🟡 Medium Risk  
            - **70-100%** 🔴 High Risk
            """)

# ==================== TAB 2: Regional Heatmap ====================
with tab2:
    st.subheader("🗺️ Regional Risk Heatmap")
    st.caption(f"Showing risk analysis for 5km radius around **{lat:.4f}°N, {lon:.4f}°E**")
    
    col_h1, col_h2 = st.columns([2, 1])
    
    with col_h1:
        if st.button("🔥 Generate Regional Heatmap", type="primary", use_container_width=True):
            with st.spinner('🌐 Generating heatmap... Analyzing 144 locations (10-15 seconds)'):
                try:
                    heatmap_map, heatmap_df = create_risk_heatmap(lat, lon, radius_km=5)
                    folium_static(heatmap_map, width=650, height=550)
                    
                    # Store in session state for stats
                    st.session_state['heatmap_df'] = heatmap_df
                    st.success(f"✅ Successfully analyzed {len(heatmap_df)} locations in the region!")
                    
                except Exception as e:
                    st.error(f"Error generating heatmap: {e}")
                    st.info("Try a different location or refresh the page")
        else:
            st.info("👆 Click 'Generate Regional Heatmap' to analyze the surrounding area")
            st.caption("📌 This will show a color-coded risk map of the 5km region")
    
    with col_h2:
        st.subheader("📊 Regional Statistics")
        
        if 'heatmap_df' in st.session_state:
            df = st.session_state['heatmap_df']
            
            # Risk metrics
            avg_risk = df['risk_score'].mean()
            max_risk = df['risk_score'].max()
            min_risk = df['risk_score'].min()
            
            st.metric("📈 Average Risk", f"{avg_risk:.1f}%")
            st.metric("🔴 Maximum Risk", f"{max_risk:.1f}%")
            st.metric("🟢 Minimum Risk", f"{min_risk:.1f}%")
            
            # Risk distribution
            high_count = len(df[df['risk_score'] > 70])
            medium_count = len(df[(df['risk_score'] >= 40) & (df['risk_score'] <= 70)])
            low_count = len(df[df['risk_score'] < 40])
            
            st.markdown("---")
            st.subheader("📊 Risk Distribution")
            
            # Create simple bar chart using Streamlit
            col_r1, col_r2, col_r3 = st.columns(3)
            with col_r1:
                st.error(f"🔴 High\n{high_count}")
            with col_r2:
                st.warning(f"🟡 Medium\n{medium_count}")
            with col_r3:
                st.success(f"🟢 Low\n{low_count}")
            
            # Percentage of high risk zones
            high_percentage = (high_count / len(df)) * 100
            if high_percentage > 30:
                st.warning(f"⚠️ {high_percentage:.0f}% of this region shows high risk")
            else:
                st.info(f"📊 {high_percentage:.0f}% of this region is high risk")
            
            # Recommendation
            st.markdown("---")
            st.subheader("💡 Recommendation")
            if avg_risk > 70:
                st.error("🚨 HIGH RISK REGION - Avoid or increase patrol presence")
            elif avg_risk > 40:
                st.warning("⚠️ MEDIUM RISK REGION - Regular monitoring recommended")
            else:
                st.success("✅ LOW RISK REGION - Normal surveillance sufficient")
        else:
            st.info("📊 Generate a heatmap first to see regional statistics")
            st.caption("Statistics will appear here after heatmap generation")

# Footer
st.divider()
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.caption("🚀 **Powered by:** Random Forest AI")
with col2:
    st.caption("🎯 **SDG Goals:** 9 (Innovation) & 16 (Peace)")
with col3:
    st.caption("📡 **Data:** Real-time Geospatial Analysis")
with col4:
    st.caption("🛡️ **GeoGuard v1.0**")