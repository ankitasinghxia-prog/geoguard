import requests
import streamlit as st

class WeatherFetcher:
    def __init__(self):
        # Get API key from secrets or use directly (for now)
        self.api_key = st.secrets.get("WEATHER_API_KEY", "48bb965111d61f313c26377ec404e059")
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
    
    def get_weather(self, lat, lon):
        """Fetch current weather for coordinates"""
        try:
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric'  # Celsius
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                weather_info = {
                    'temperature': data['main']['temp'],
                    'humidity': data['main']['humidity'],
                    'wind_speed': data['wind']['speed'],
                    'weather_main': data['weather'][0]['main'],
                    'weather_description': data['weather'][0]['description'],
                    'rain': data.get('rain', {}).get('1h', 0),
                    'pressure': data['main']['pressure']
                }
                return weather_info
            else:
                return None
                
        except Exception as e:
            print(f"Weather API error: {e}")
            return None
    
    def get_weather_impact(self, weather_info):
        """Calculate risk adjustment based on weather"""
        if weather_info is None:
            return 0, "No weather data available"
        
        risk_boost = 0
        reasons = []
        
        # Rain impact
        if weather_info['rain'] > 0:
            risk_boost += 25
            reasons.append(f"🌧️ Rainfall: {weather_info['rain']}mm (high risk)")
        elif weather_info['weather_main'] == 'Rain':
            risk_boost += 20
            reasons.append("🌧️ Rainy conditions increase risk")
        
        # Fog impact
        if weather_info['weather_main'] == 'Fog' or weather_info['weather_main'] == 'Mist':
            risk_boost += 15
            reasons.append("🌫️ Fog/Mist reduces visibility")
        
        # Wind impact
        if weather_info['wind_speed'] > 15:
            risk_boost += 10
            reasons.append(f"💨 High winds: {weather_info['wind_speed']}km/h")
        elif weather_info['wind_speed'] > 25:
            risk_boost += 15
            reasons.append(f"💨 Very high winds: {weather_info['wind_speed']}km/h")
        
        # Temperature extremes
        if weather_info['temperature'] > 40:
            risk_boost += 15
            reasons.append(f"🔥 Extreme heat: {weather_info['temperature']}°C")
        elif weather_info['temperature'] < 0:
            risk_boost += 10
            reasons.append(f"❄️ Freezing temperature: {weather_info['temperature']}°C")
        
        # Thunderstorm
        if weather_info['weather_main'] == 'Thunderstorm':
            risk_boost += 30
            reasons.append("⛈️ Thunderstorm detected - high risk")
        
        return min(40, risk_boost), reasons

# Create a sample function to test
def test_weather():
    fetcher = WeatherFetcher()
    weather = fetcher.get_weather(28.6139, 77.2090)  # Delhi
    if weather:
        print(f"Temperature: {weather['temperature']}°C")
        print(f"Conditions: {weather['weather_description']}")
        impact, reasons = fetcher.get_weather_impact(weather)
        print(f"Risk boost: {impact}%")
        print(f"Reasons: {reasons}")
    else:
        print("Failed to fetch weather")

if __name__ == "__main__":
    test_weather()