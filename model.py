import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
import os

class TerrainRiskModel:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def generate_training_data(self, n_samples=5000):
        """Generate realistic synthetic terrain data for training"""
        np.random.seed(42)
        
        # Generate features
        slope = np.random.uniform(0, 60, n_samples)
        elevation = np.random.uniform(0, 5000, n_samples)
        ndvi = np.random.uniform(-0.5, 0.8, n_samples)
        water_distance = np.random.uniform(0, 5000, n_samples)
        road_distance = np.random.uniform(0, 10000, n_samples)
        rainfall = np.random.uniform(0, 400, n_samples)
        vegetation_density = np.random.uniform(0, 100, n_samples)
        
        # Calculate risk score based on rules
        risk_score = (
            (slope > 30) * 25 +
            (ndvi < 0.2) * 20 +
            (water_distance < 500) * 25 +
            (road_distance < 1000) * 15 +
            (rainfall > 200) * 15
        )
        
        # Add noise
        risk_score = risk_score + np.random.normal(0, 10, n_samples)
        risk_score = np.clip(risk_score, 0, 100)
        
        # Create binary labels (1 = High Risk > 50)
        labels = (risk_score > 50).astype(int)
        
        # Create DataFrame
        data = pd.DataFrame({
            'slope': slope,
            'elevation': elevation,
            'ndvi': ndvi,
            'water_distance_km': water_distance / 1000,
            'road_distance_km': road_distance / 1000,
            'rainfall_mm': rainfall,
            'vegetation_density': vegetation_density,
            'risk_score': risk_score,
            'risk_label': labels
        })
        
        return data
    
    def train(self):
        """Train the Random Forest model"""
        print("📊 Generating training data...")
        data = self.generate_training_data(5000)
        
        feature_cols = ['slope', 'elevation', 'ndvi', 'water_distance_km', 
                       'road_distance_km', 'rainfall_mm', 'vegetation_density']
        
        X = data[feature_cols].values
        y = data['risk_label'].values
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        print("🤖 Training Random Forest model...")
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        self.model.fit(X_train_scaled, y_train)
        
        # Calculate accuracy
        accuracy = self.model.score(X_test_scaled, y_test)
        self.is_trained = True
        
        print(f"✅ Model trained! Accuracy: {accuracy:.2%}")
        
        # Save model
        os.makedirs('models', exist_ok=True)
        joblib.dump(self.model, 'models/risk_model.pkl')
        joblib.dump(self.scaler, 'models/scaler.pkl')
        
        return accuracy
    
    def predict(self, features_dict):
        """Predict risk for a single location"""
        if not self.is_trained:
            self.train()
        
        # Extract features in correct order
        feature_order = ['slope', 'elevation', 'ndvi', 'water_distance_km', 
                        'road_distance_km', 'rainfall_mm', 'vegetation_density']
        
        features = np.array([[features_dict[f] for f in feature_order]])
        
        # Scale features
        features_scaled = self.scaler.transform(features)
        
        # Get prediction and probability
        risk_class = self.model.predict(features_scaled)[0]
        risk_probability = self.model.predict_proba(features_scaled)[0][1]
        risk_score = risk_probability * 100
        
        return {
            'risk_score': round(risk_score, 1),
            'risk_level': 'High' if risk_class == 1 else 'Low',
            'risk_probability': risk_probability
        }
    
    def predict_batch(self, features_list):
        """Predict risk for multiple locations"""
        results = []
        for features in features_list:
            results.append(self.predict(features))
        return results

# Create and train the model when this file is run
if __name__ == "__main__":
    print("🚀 Training GeoGuard AI Model...")
    model = TerrainRiskModel()
    model.train()
    print("\n✨ Model ready for predictions!")