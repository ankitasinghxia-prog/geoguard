import streamlit as st
from PIL import Image
import io
import numpy as np
import folium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import tempfile
import os

def export_map_as_image(map_object, filename="risk_map.png"):
    """Export folium map as PNG image"""
    try:
        # Save map as HTML
        temp_html = tempfile.NamedTemporaryFile(delete=False, suffix='.html')
        map_object.save(temp_html.name)
        
        # Setup headless browser
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=options)
        driver.get(f'file://{temp_html.name}')
        
        # Take screenshot
        driver.save_screenshot(filename)
        driver.quit()
        
        # Clean up temp file
        os.unlink(temp_html.name)
        
        return filename
    except Exception as e:
        st.error(f"Screenshot failed: {e}")
        return None

def create_simple_map_image(center_lat, center_lon, risk_score):
    """Create a simple map screenshot alternative using matplotlib"""
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    
    # Add map features
    ax.add_feature(cfeature.LAND, color='lightgray')
    ax.add_feature(cfeature.OCEAN, color='lightblue')
    ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax.add_feature(cfeature.BORDERS, linewidth=0.5)
    
    # Plot the point
    ax.plot(center_lon, center_lat, 'ro', markersize=10, transform=ccrs.PlateCarree())
    ax.text(center_lon + 0.5, center_lat + 0.5, f'Risk: {risk_score}%', 
            transform=ccrs.PlateCarree(), fontsize=12, fontweight='bold')
    
    # Set extent (5km radius)
    lat_offset = 0.045  # ~5km
    lon_offset = 0.045 / np.cos(np.radians(center_lat))
    ax.set_extent([center_lon - lon_offset, center_lon + lon_offset,
                   center_lat - lat_offset, center_lat + lat_offset])
    
    ax.set_title(f'GeoGuard Risk Analysis\nLocation: {center_lat:.4f}, {center_lon:.4f}')
    
    plt.tight_layout()
    
    # Save to bytes
    img_bytes = io.BytesIO()
    plt.savefig(img_bytes, format='PNG', dpi=150, bbox_inches='tight')
    plt.close()
    
    img_bytes.seek(0)
    return Image.open(img_bytes)