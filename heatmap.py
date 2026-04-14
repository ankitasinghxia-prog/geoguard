import numpy as np
import pandas as pd
import folium
from folium import plugins
from model import TerrainRiskModel
import random

def generate_heatmap_data(center_lat, center_lon, radius_km=5, grid_size=10):
    """
    Generate risk predictions for a grid around a center point
    """
    model = TerrainRiskModel()
    model.train()
    
    # Create grid of points
    lat_step = radius_km / 111.0  # 1 degree lat ≈ 111 km
    lon_step = radius_km / (111.0 * np.cos(np.radians(center_lat)))
    
    lat_points = np.linspace(center_lat - lat_step, center_lat + lat_step, grid_size)
    lon_points = np.linspace(center_lon - lon_step, center_lon + lon_step, grid_size)
    
    heatmap_data = []
    
    for lat in lat_points:
        for lon in lon_points:
            # Generate features based on coordinates
            seed = int(abs(lat * 1000) + abs(lon * 1000))
            random.seed(seed)
            
            features = {
                'slope': random.uniform(0, 60),
                'elevation': random.uniform(0, 5000),
                'ndvi': random.uniform(-0.5, 0.8),
                'water_distance_km': random.uniform(0, 5),
                'road_distance_km': random.uniform(0, 10),
                'rainfall_mm': random.uniform(0, 400),
                'vegetation_density': random.uniform(0, 100)
            }
            
            result = model.predict(features)
            
            heatmap_data.append({
                'lat': lat,
                'lon': lon,
                'risk_score': result['risk_score'],
                'risk_level': result['risk_level']
            })
    
    return pd.DataFrame(heatmap_data)

def create_risk_heatmap(center_lat, center_lon, radius_km=5):
    """
    Create a folium map with risk heatmap
    """
    # Generate data
    df = generate_heatmap_data(center_lat, center_lon, radius_km)
    
    # Create map
    m = folium.Map(location=[center_lat, center_lon], zoom_start=11)
    
    # Add heatmap
    heat_data = [[row['lat'], row['lon'], row['risk_score']] 
                 for _, row in df.iterrows()]
    
    plugins.HeatMap(heat_data, 
                    min_opacity=0.4,
                    max_zoom=13,
                    radius=25,
                    blur=15,
                    gradient={0.2: 'green', 0.5: 'yellow', 0.8: 'red'}).add_to(m)
    
    # Add marker for center
    folium.Marker(
        [center_lat, center_lon],
        popup=f"Center: {center_lat}, {center_lon}",
        icon=folium.Icon(color='blue', icon='info-sign')
    ).add_to(m)
    
    return m, df

if __name__ == "__main__":
    # Test the heatmap
    m, df = create_risk_heatmap(28.6139, 77.2090, radius_km=5)
    print(f"Generated {len(df)} risk points")
    print(f"Average risk: {df['risk_score'].mean():.1f}%")
    print(f"Max risk: {df['risk_score'].max():.1f}%")
    print(f"Min risk: {df['risk_score'].min():.1f}%")