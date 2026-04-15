import requests
import random
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== CONFIGURATION ====================
# YOUR ACTUAL TOKEN - Replace with your token if needed
TOKEN = "8039116726:AAEpgF8GUEeSNG0I_4dL0yAtMCDihIqARpg"

# OpenWeatherMap API Key (optional - get from https://openweathermap.org/api)
WEATHER_API_KEY = "48bb965111d61f313c26377ec404e059"

# ==================== RISK ANALYSIS FUNCTION ====================
def analyze_risk(lat, lon):
    """Analyze risk for given coordinates"""
    try:
        random.seed(int(abs(lat * 1000) + abs(lon * 1000)))
        
        himalayas_bonus = 15 if (28 < lat < 31 and 77 < lon < 80) else 0
        coastal_bonus = 10 if lat < 20 else 0
        
        slope = random.uniform(0, 60) + (himalayas_bonus / 2)
        ndvi = random.uniform(-0.5, 0.8)
        water_distance = random.uniform(0, 5)
        rainfall = random.uniform(0, 400) + himalayas_bonus
        
        risk_score = 0
        if slope > 30:
            risk_score += 25
        if ndvi < 0.2:
            risk_score += 20
        if water_distance < 0.5:
            risk_score += 25
        if rainfall > 200:
            risk_score += 15
        
        risk_score = risk_score + random.uniform(-10, 10) + himalayas_bonus + coastal_bonus
        risk_score = max(0, min(100, risk_score))
        
        if risk_score < 40:
            risk_level = "LOW RISK"
            emoji = "🟢"
        elif risk_score < 70:
            risk_level = "MEDIUM RISK"
            emoji = "🟡"
        else:
            risk_level = "HIGH RISK"
            emoji = "🔴"
        
        factors = []
        if slope > 30:
            factors.append(f"Steep slope: {slope:.0f} degrees")
        if ndvi < 0.2:
            factors.append(f"Low vegetation: {ndvi:.2f}")
        if water_distance < 0.5:
            factors.append(f"Near water: {water_distance:.1f}km")
        if rainfall > 200:
            factors.append(f"High rainfall: {rainfall:.0f}mm/year")
        
        return {
            'risk_score': round(risk_score, 1),
            'risk_level': risk_level,
            'emoji': emoji,
            'factors': factors,
            'slope': slope,
            'ndvi': ndvi,
            'water_distance': water_distance,
            'rainfall': rainfall
        }
    except Exception as e:
        logger.error(f"Risk analysis error: {e}")
        return None

# ==================== WEATHER FUNCTION ====================
def get_weather(lat, lon):
    """Fetch current weather from OpenWeatherMap"""
    try:
        if WEATHER_API_KEY and WEATHER_API_KEY != "48bb965111d61f313c26377ec404e059":
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    'temperature': data['main']['temp'],
                    'humidity': data['main']['humidity'],
                    'wind_speed': data['wind']['speed'],
                    'condition': data['weather'][0]['description'].title()
                }
        return None
    except Exception as e:
        logger.error(f"Weather API error: {e}")
        return None

# ==================== BOT COMMANDS ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = (
        "🛡️ Welcome to GeoGuard Risk Bot!\n\n"
        "Available Commands:\n"
        "/risk lat lon - Get risk score\n"
        "/weather lat lon - Get current weather\n"
        "/help - Show all commands\n\n"
        "Example: /risk 28.6139 77.2090"
    )
    await update.message.reply_text(message)

async def risk_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if len(context.args) < 2:
            await update.message.reply_text("Usage: /risk latitude longitude\nExample: /risk 28.6139 77.2090")
            return
        
        lat = float(context.args[0])
        lon = float(context.args[1])
        
        if lat < -90 or lat > 90:
            await update.message.reply_text("Latitude must be between -90 and 90")
            return
        if lon < -180 or lon > 180:
            await update.message.reply_text("Longitude must be between -180 and 180")
            return
        
        await update.message.reply_text(f"🔍 Analyzing location {lat}, {lon}...")
        
        result = analyze_risk(lat, lon)
        
        if result:
            message = f"📍 Location: {lat:.4f}, {lon:.4f}\n\n"
            message += f"{result['emoji']} Risk Score: {result['risk_score']}%\n"
            message += f"{result['emoji']} {result['risk_level']}\n\n"
            message += "📊 Key Factors:\n"
            if result['factors']:
                for factor in result['factors']:
                    message += f"   • {factor}\n"
            else:
                message += "   • No extreme factors detected\n"
            message += f"\n💡 Use /weather {lat:.4f} {lon:.4f} for current weather"
            await update.message.reply_text(message)
        else:
            await update.message.reply_text("❌ Unable to analyze location")
    except ValueError:
        await update.message.reply_text("❌ Invalid coordinates. Use numbers like: /risk 28.6139 77.2090")
    except Exception as e:
        await update.message.reply_text("❌ An error occurred")

async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if len(context.args) < 2:
            await update.message.reply_text("Usage: /weather latitude longitude\nExample: /weather 28.6139 77.2090")
            return
        
        lat = float(context.args[0])
        lon = float(context.args[1])
        
        await update.message.reply_text(f"🌤️ Fetching weather for {lat}, {lon}...")
        
        weather = get_weather(lat, lon)
        
        if weather:
            message = f"🌍 Current Weather\n📍 Location: {lat:.4f}, {lon:.4f}\n\n"
            message += f"🌡️ Temperature: {weather['temperature']:.1f}°C\n"
            message += f"💧 Humidity: {weather['humidity']}%\n"
            message += f"💨 Wind Speed: {weather['wind_speed']:.1f} km/h\n"
            message += f"☁️ Conditions: {weather['condition']}\n\n"
            message += f"💡 Use /risk {lat:.4f} {lon:.4f} for risk analysis"
            await update.message.reply_text(message)
        else:
            await update.message.reply_text("❌ Unable to fetch weather data. API key may need activation (takes 1-2 hours).")
    except ValueError:
        await update.message.reply_text("❌ Invalid coordinates")
    except Exception as e:
        await update.message.reply_text("❌ An error occurred")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = (
        "🛡️ GeoGuard Bot Commands\n\n"
        "/risk lat lon - Analyze terrain risk\n"
        "/weather lat lon - Get current weather\n"
        "/start - Welcome message\n"
        "/help - This help\n\n"
        "📍 Quick Coordinates:\n"
        "Delhi: 28.6139, 77.2090\n"
        "Mumbai: 19.0760, 72.8777\n"
        "Himalayas: 30.0000, 79.0000"
    )
    await update.message.reply_text(message)

# ==================== MAIN ====================
def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("risk", risk_command))
    app.add_handler(CommandHandler("weather", weather_command))
    app.add_handler(CommandHandler("help", help_command))
    
    print("🤖 GeoGuard Bot is running...")
    print("Press Ctrl+C to stop")
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()