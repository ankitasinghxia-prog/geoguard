\# 🛡️ GeoGuard - AI Based Border Terrain Risk Analyzer





\## 📌 Project Overview



\*\*GeoGuard\*\* is an AI-powered geospatial risk analysis system that transforms raw satellite and terrain data into actionable risk intelligence. Designed for border security, disaster management, and infrastructure planning, GeoGuard uses Machine Learning to predict high-risk zones in real-time.



\### 🎯 Live Demo

👉 \*\*Try it now:\*\* \[geoguard-ankitasinghxia-prog.streamlit.app](https://geoguard-hh3hdkkpflx9nbnwtjeqdp.streamlit.app/)



\### 🤖 Telegram Bot

👉 \*\*Chat with bot:\*\* \[@geoguard\_risk\_bot](https://web.telegram.org/k/#@geoguard\_risk\_bot)



\---



\## 🚀 Features



\### Web Application (Streamlit)

| Feature | Description |

|---------|-------------|

| 📍 \*\*Single Location Analysis\*\* | Click on map or enter coordinates for instant risk assessment |

| 🗺️ \*\*Regional Heatmap\*\* | Generate color-coded risk maps for 5km radius |

| 📊 \*\*Batch Analysis\*\* | Upload CSV with multiple locations for bulk processing |

| 📄 \*\*PDF Reports\*\* | Download professional risk assessment reports |

| 🌤️ \*\*Real-time Weather\*\* | Live weather data affecting risk scores |

| 📜 \*\*Risk History\*\* | Track previously analyzed locations |



\### Telegram Bot

| Command | Description |

|---------|-------------|

| `/risk lat lon` | Get AI risk score for any location |

| `/weather lat lon` | Get current weather conditions |

| `/help` | Show all available commands |



\---



\## 🛠️ Tech Stack



| Category | Technologies |

|----------|--------------|

| \*\*Frontend\*\* | Streamlit, HTML/CSS, Folium |

| \*\*Backend\*\* | Python, FastAPI |

| \*\*Machine Learning\*\* | Scikit-learn, Random Forest, XGBoost |

| \*\*Geospatial\*\* | Folium, Rasterio, GeoPandas |

| \*\*Visualization\*\* | Plotly, Streamlit-Folium |

| \*\*API Integration\*\* | OpenWeatherMap, Telegram Bot API |

| \*\*Deployment\*\* | Streamlit Cloud, GitHub |



\---



\## 📊 Risk Analysis Factors



The AI model evaluates multiple factors to calculate risk scores (0-100%):



| Factor | Impact |

|--------|--------|

| 🌄 \*\*Terrain Slope\*\* | Steeper slopes = higher risk |

| 🌿 \*\*Vegetation Density (NDVI)\*\* | Sparse vegetation = higher risk |

| 💧 \*\*Water Proximity\*\* | Closer to water = higher risk |

| ☔ \*\*Rainfall Patterns\*\* | Higher rainfall = higher risk |

| 🌤️ \*\*Real-time Weather\*\* | Rain/fog/wind increase risk |



\---



\## 🏗️ System Architecture



┌─────────────────────────────────────────────────────┐

│ DATA LAYER │

│ Satellite Imagery | DEM | Weather | Vegetation │

└─────────────────────────────────────────────────────┘

↓

┌─────────────────────────────────────────────────────┐

│ FEATURE ENGINEERING │

│ Slope | NDVI | Water Distance | Elevation Variance │

└─────────────────────────────────────────────────────┘

↓

┌─────────────────────────────────────────────────────┐

│ AI MODEL │

│ Random Forest Classifier (85% accuracy) │

└─────────────────────────────────────────────────────┘

↓

┌─────────────────────────────────────────────────────┐

│ VISUALIZATION LAYER │

│ Interactive Maps | Heatmaps | Risk Dashboard │

└─────────────────────────────────────────────────────┘



\---



\## 🚀 Quick Start



\### Prerequisites

\- Python 3.11 or higher

\- Git



\### Installation



```bash

\# Clone repository

git clone https://github.com/ankitasinghxia-prog/geoguard.git

cd geoguard



\# Create virtual environment

python -m venv venv

source venv/bin/activate  # Linux/Mac

venv\\Scripts\\activate     # Windows



\# Install dependencies

pip install -r requirements.txt



\# Run the app

streamlit run app.py

Environment Variables (Optional)

Create .streamlit/secrets.toml for API keys:



toml

WEATHER\_API\_KEY = "your\_openweathermap\_api\_key"

📱 Usage Examples

Web App

Open the live demo link



Click anywhere on the map or enter coordinates



Click "Analyze Risk" for AI assessment



Generate heatmaps or export PDF reports



Telegram Bot

Search @geoguard\_risk\_bot on Telegram



Send /start to begin



Try /risk 28.6139 77.2090 for Delhi



Use /weather 28.6139 77.2090 for current weather



🎯 SDG Alignment

SDG	Contribution

SDG 9 - Industry, Innovation \& Infrastructure	AI-powered monitoring for smart infrastructure

SDG 16 - Peace, Justice \& Strong Institutions	Enhanced border security and situational awareness

SDG 13 - Climate Action	Environmental risk detection

SDG 15 - Life on Land	Terrain and ecosystem monitoring





📁 Project Structure

text

geoguard/

├── app.py                 # Main Streamlit dashboard

├── model.py              # AI/ML model training

├── heatmap.py            # Heatmap generation

├── pdf\_generator.py      # PDF report export

├── batch\_analyzer.py     # CSV batch analysis

├── weather\_fetcher.py    # Real-time weather API

├── telegram\_bot.py       # Telegram bot

├── requirements.txt      # Dependencies

├── .streamlit/

│   └── secrets.toml      # API keys (local only)



👩‍💻 Author

Ankita Singh



GitHub: @ankitasinghxia-prog



Email: \[ankitasinghxia@gmail.com]





🙏 Acknowledgments



OpenWeatherMap for weather API



Streamlit for deployment platform



Telegram Bot API for bot integration



🔧 Future Enhancements



Real-time satellite data (Sentinel-2 integration)



Mobile app (React Native)



Multi-language support (Hindi, Punjabi)



Email/SMS alerts for high-risk zones



Historical risk trend analysis



Drone flight path generation











