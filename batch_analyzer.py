import pandas as pd
import random
import streamlit as st

def analyze_batch_locations(uploaded_file, model):
    """Analyze multiple locations from CSV file"""
    
    # Read the CSV file
    df = pd.read_csv(uploaded_file)
    
    # Check required columns (case insensitive)
    df.columns = df.columns.str.lower().str.strip()
    
    if 'latitude' not in df.columns or 'longitude' not in df.columns:
        st.error("❌ CSV must have 'latitude' and 'longitude' columns")
        st.info("📋 Example format:\nlatitude,longitude\n28.6139,77.2090\n19.0760,72.8777")
        return None
    
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, row in df.iterrows():
        lat = row['latitude']
        lon = row['longitude']
        
        status_text.text(f"📍 Analyzing {idx+1}/{len(df)}: {lat:.4f}, {lon:.4f}")
        
        # Generate features based on location
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
        
        # Determine risk level
        if final_score < 40:
            risk_level = "Low"
            risk_color = "🟢"
        elif final_score < 70:
            risk_level = "Medium"
            risk_color = "🟡"
        else:
            risk_level = "High"
            risk_color = "🔴"
        
        results.append({
            'latitude': lat,
            'longitude': lon,
            'risk_score': round(final_score, 1),
            'risk_level': risk_level,
            'indicator': risk_color
        })
        
        # Update progress
        progress_bar.progress((idx + 1) / len(df))
    
    status_text.text("✅ Analysis complete!")
    return pd.DataFrame(results)


def create_sample_csv():
    """Create a sample CSV file for users to download"""
    sample_data = {
        'latitude': [28.6139, 19.0760, 12.9716, 30.0000, 13.0827],
        'longitude': [77.2090, 72.8777, 77.5946, 79.0000, 80.2707]
    }
    df = pd.DataFrame(sample_data)
    return df.to_csv(index=False)


def get_batch_summary(results_df):
    """Generate summary statistics from batch results"""
    summary = {
        'total': len(results_df),
        'average_risk': results_df['risk_score'].mean(),
        'high_risk_count': len(results_df[results_df['risk_score'] > 70]),
        'medium_risk_count': len(results_df[(results_df['risk_score'] >= 40) & (results_df['risk_score'] <= 70)]),
        'low_risk_count': len(results_df[results_df['risk_score'] < 40]),
        'max_risk': results_df['risk_score'].max(),
        'min_risk': results_df['risk_score'].min(),
        'highest_risk_location': results_df.loc[results_df['risk_score'].idxmax()] if len(results_df) > 0 else None
    }
    return summary