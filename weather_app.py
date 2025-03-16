import requests
import os
import json
from datetime import datetime
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class WeatherData:
    """Class to store and represent weather data"""
    def __init__(self, city, country, temp, feels_like, description, humidity, wind_speed, timestamp):
        self.city = city
        self.country = country
        self.temperature = temp
        self.feels_like = feels_like
        self.description = description
        self.humidity = humidity
        self.wind_speed = wind_speed
        self.timestamp = timestamp
        
    def __str__(self):
        """String representation of the weather data"""
        date_time = datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S')
        
        return f"""
Weather in {self.city}, {self.country} at {date_time}:
Temperature: {self.temperature}°C (Feels like: {self.feels_like}°C)
Conditions: {self.description}
Humidity: {self.humidity}%
Wind Speed: {self.wind_speed:.1f} m/s
"""

class WeatherApp:
    def __init__(self):
        # Get API key from environment variable
        self.api_key = os.environ.get("WEATHER_API_KEY", "")
        if not self.api_key:
            raise ValueError("API key not found. Please set WEATHER_API_KEY in .env file.")
        self.base_url = "http://api.weatherapi.com/v1/current.json"
        self.recent_searches = []
    
    def display_welcome_banner(self):
        """Display welcome message on screen with formatting"""
        banner = """
╔════════════════════════════════════════════════════╗
║                                                    ║
║               WEATHER INFORMATION APP              ║
║                                                    ║
║            Get real-time weather updates           ║
║              for any city in the world             ║
║                                                    ║
╚════════════════════════════════════════════════════╝
"""
        print(banner)
    
    def display_loading_message(self, city):
        """Display a loading message animation"""
        print(f"\nFetching weather data for {city}...", end="", flush=True)
        for _ in range(3):
            time.sleep(0.5)
            print(".", end="", flush=True)
        print("\n")
    
    def display_error_message(self, error_type, message):
        """Display formatted error messages"""
        error_banner = f"""
⚠️  {error_type} ERROR  ⚠️
{'-' * 40}
{message}
{'-' * 40}
"""
        print(error_banner)

    def get_weather(self, city):
        """Fetch weather data for the specified city"""
        # Display loading message
        self.display_loading_message(city)
        
        params = {
            'q': city,
            'key': self.api_key,
        }
        
        try:
            # Network request - potential connection errors
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()  # Raise an exception for HTTP errors
            
            # Parse JSON response - potential parsing errors
            weather_data = response.json()
            
            # Process data - potential key errors if API changes
            weather_obj = self._process_weather_data(weather_data)
            
            # Store in recent searches
            self.recent_searches.append(weather_obj)
            if len(self.recent_searches) > 5:
                self.recent_searches.pop(0)
                
            # Return formatted weather data
            return str(weather_obj)
            
        except requests.exceptions.ConnectionError:
            self.display_error_message("CONNECTION", "Failed to connect to the weather service. Please check your internet connection.")
            return None
        except requests.exceptions.Timeout:
            self.display_error_message("TIMEOUT", "Request timed out. The weather service may be experiencing high traffic.")
            return None
        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 400:
                self.display_error_message("SEARCH", f"City '{city}' not found. Please check the spelling and try again.")
            else:
                self.display_error_message("HTTP", f"Weather service returned an error: {http_err}")
            return None
        except json.JSONDecodeError:
            self.display_error_message("DATA", "Received invalid data from the weather service.")
            return None
        except KeyError as key_err:
            self.display_error_message("DATA", f"Weather data is missing expected information: {key_err}")
            return None
        except Exception as err:
            self.display_error_message("UNEXPECTED", f"An unexpected error occurred: {err}")
            return None
    
    def _process_weather_data(self, data):
        """Process the weather API response into a WeatherData object"""
        try:
            location = data['location']
            current = data['current']
            
            city = location['name']
            country = location['country']
            temp = current['temp_c']
            feels_like = current['feelslike_c']
            description = current['condition']['text']
            humidity = current['humidity']
            wind_speed = current['wind_kph'] / 3.6  # Convert to m/s
            timestamp = current['last_updated_epoch']
            
            return WeatherData(
                city, country, temp, feels_like, description, 
                humidity, wind_speed, timestamp
            )
        except KeyError as e:
            raise KeyError(f"Missing expected field in API response: {e}")
    
    def show_recent_searches(self):
        """Display recent searches"""
        if not self.recent_searches:
            print("\nNo recent searches.")
            return
        
        print("\n===== RECENT SEARCHES =====")
        for i, weather in enumerate(reversed(self.recent_searches), 1):
            print(f"{i}. {weather.city}, {weather.country}: {weather.temperature}°C, {weather.description}")
        print("===========================")

def main():
    app = WeatherApp()
    
    # Display welcome message on screen
    app.display_welcome_banner()
    
    print("Type 'history' to see recent searches or 'quit' to exit.")
    print("\n" + "="*50)
    print("   Press Ctrl+C or type 'quit' at any time to exit")
    print("="*50 + "\n")
    
    while True:
        try:
            user_input = input("\nEnter city name: ").strip()
            
            if not user_input:
                print("Please enter a city name.")
                continue
                
            if user_input.lower() == 'quit':
                print("\nThank you for using the Weather App. Goodbye!")
                break
                
            if user_input.lower() == 'history':
                app.show_recent_searches()
                continue
                
            # Get weather information
            weather_info = app.get_weather(user_input)
            
            # Only print if we got valid weather information
            if weather_info:
                print(weather_info)
                print("\n" + "-"*40)
                print("Type 'quit' to exit or enter another city name")
                print("-"*40)
                
        except KeyboardInterrupt:
            print("\n\nProgram interrupted. Exiting...")
            break
            
        except Exception as e:
            # Catch any unexpected exceptions we didn't handle specifically
            print(f"\nAn unexpected error occurred: {e}")
            print("Please try again.")

if __name__ == "__main__":
    main()
