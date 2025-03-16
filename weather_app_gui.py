import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import json
from datetime import datetime
from PIL import Image, ImageTk
import io
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class WeatherData:
    """Class to store and represent weather data"""
    def __init__(self, city, country, temp, feels_like, description, humidity, wind_speed, timestamp, icon_url=None):
        self.city = city
        self.country = country
        self.temperature = temp
        self.feels_like = feels_like
        self.description = description
        self.humidity = humidity
        self.wind_speed = wind_speed
        self.timestamp = timestamp
        self.icon_url = icon_url
        
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

class WeatherAppGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather App")
        # Further increase window size to ensure all information is visible
        self.root.geometry("700x650")
        self.root.resizable(True, True)
        self.root.configure(bg="#f0f0f0")
        
        # Get API key from environment variable
        self.api_key = os.environ.get("WEATHER_API_KEY", "")
        if not self.api_key:
            messagebox.showerror("Configuration Error", 
                               "API key not found. Please set WEATHER_API_KEY in .env file.")
            self.root.quit()
            return
            
        self.base_url = "http://api.weatherapi.com/v1/current.json"
        
        # Store recent searches
        self.recent_searches = []
        
        self.setup_ui()
    
    def setup_ui(self):
        # Create a frame for the search section
        search_frame = tk.Frame(self.root, bg="#f0f0f0")
        search_frame.pack(pady=20)
        
        # Create and place search components
        tk.Label(search_frame, text="Enter City:", font=("Arial", 14), bg="#f0f0f0").grid(row=0, column=0, padx=10)
        self.city_entry = tk.Entry(search_frame, font=("Arial", 14), width=20)
        self.city_entry.grid(row=0, column=1, padx=10)
        
        search_button = tk.Button(search_frame, text="Search", font=("Arial", 12), 
                                 command=self.get_weather, bg="#4CAF50", fg="white", padx=10)
        search_button.grid(row=0, column=2, padx=10)
        
        history_button = tk.Button(search_frame, text="History", font=("Arial", 12), 
                                  command=self.show_history, bg="#2196F3", fg="white", padx=10)
        history_button.grid(row=0, column=3, padx=10)
        
        # Bind Enter key to search function
        self.city_entry.bind("<Return>", lambda event: self.get_weather())
        
        # Create frame for weather display
        self.weather_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.weather_frame.pack(pady=10, fill="both", expand=True)
        
        # Status bar for messages
        self.status_bar = tk.Label(self.root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Initially display a welcome message
        self.display_welcome_message()
    
    def display_welcome_message(self):
        """Display welcome message on the GUI"""
        welcome_frame = tk.Frame(self.weather_frame, bg="#e6f7ff", padx=20, pady=20)
        welcome_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.8)
        
        # Welcome title
        tk.Label(welcome_frame, text="Welcome to Weather App", font=("Arial", 18, "bold"), 
                bg="#e6f7ff").pack(pady=(10, 20))
        
        # App description
        description = """
This application provides real-time weather information 
for cities around the world.

Enter a city name in the search box and click 'Search' 
or press Enter to get weather information.

Click 'History' to view your recent searches.
"""
        tk.Label(welcome_frame, text=description, font=("Arial", 12), 
                bg="#e6f7ff", justify="left").pack(pady=10)
    
    def display_status_message(self, message):
        """Display a message in the status bar"""
        self.status_bar.config(text=message)
        self.root.update()
    
    def get_weather(self):
        city = self.city_entry.get().strip()
        if not city:
            messagebox.showwarning("Input Error", "Please enter a city name!")
            return
        
        # Clear previous weather display
        for widget in self.weather_frame.winfo_children():
            widget.destroy()
        
        # Show loading message
        self.display_status_message(f"Fetching weather data for {city}...")
        loading_label = tk.Label(self.weather_frame, text="Loading...", font=("Arial", 14), bg="#f0f0f0")
        loading_label.pack(pady=100)
        self.root.update()
        
        params = {
            'q': city,
            'key': self.api_key,
        }
        
        try:
            # Network request - potential connection errors
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            # Parse JSON response - potential parsing errors
            data = response.json()
            
            # Process data - potential key errors
            weather_obj = self._process_weather_data(data)
            
            # Add to recent searches
            self.recent_searches.append(weather_obj)
            if len(self.recent_searches) > 5:
                self.recent_searches.pop(0)
            
            # Clear loading message
            loading_label.destroy()
            
            # Display weather data
            self.display_weather_data(weather_obj)
            self.display_status_message(f"Displaying weather for {city}")
            
        except requests.exceptions.ConnectionError:
            loading_label.destroy()
            self.display_error("CONNECTION ERROR", "Failed to connect to the weather service.\nPlease check your internet connection.")
        except requests.exceptions.Timeout:
            loading_label.destroy()
            self.display_error("TIMEOUT ERROR", "Request timed out.\nThe weather service may be experiencing high traffic.")
        except requests.exceptions.HTTPError as http_err:
            loading_label.destroy()
            if response.status_code == 400:
                error_msg = f"City '{city}' not found.\nPlease check the spelling and try again."
            else:
                error_msg = f"Weather service returned an error:\n{http_err}"
            self.display_error("SEARCH ERROR", error_msg)
        except json.JSONDecodeError:
            loading_label.destroy()
            self.display_error("DATA ERROR", "Received invalid data from the weather service.")
        except KeyError as key_err:
            loading_label.destroy()
            self.display_error("DATA ERROR", f"Weather data is missing expected information:\n{key_err}")
        except Exception as err:
            loading_label.destroy()
            self.display_error("UNEXPECTED ERROR", f"An unexpected error occurred:\n{err}")
    
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
            icon_url = "https:" + current['condition']['icon']
            
            return WeatherData(
                city, country, temp, feels_like, description, 
                humidity, wind_speed, timestamp, icon_url
            )
        except KeyError as e:
            raise KeyError(f"Missing field in API response: {e}")
    
    def display_weather_data(self, weather_data):
        # Clear any existing frames in the weather frame
        for widget in self.weather_frame.winfo_children():
            widget.destroy()
            
        # Create a frame that will contain all weather information
        main_info_frame = tk.Frame(self.weather_frame, bg="white", padx=25, pady=25)
        main_info_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create a canvas with scrollbar for the content
        canvas = tk.Canvas(main_info_frame, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_info_frame, orient="vertical", command=canvas.yview)
        
        # Connect scrollbar to canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Place canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create frame inside canvas to hold weather information
        info_frame = tk.Frame(canvas, bg="white", padx=15, pady=15)
        
        # Add info_frame to a window in the canvas
        canvas_window = canvas.create_window((0, 0), window=info_frame, anchor="nw")
        
        # Configure canvas to resize with window
        def configure_canvas(event):
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind('<Configure>', configure_canvas)
        
        # City and country title
        tk.Label(info_frame, text=f"{weather_data.city}, {weather_data.country}", 
                font=("Arial", 24, "bold"), bg="white").pack(pady=(0, 10))
        
        # Date and time
        date_time = datetime.fromtimestamp(weather_data.timestamp).strftime('%Y-%m-%d %H:%M:%S')
        tk.Label(info_frame, text=f"As of {date_time}", font=("Arial", 12), 
                bg="white", fg="gray").pack(pady=(0, 20))
        
        # Try to get weather icon
        if weather_data.icon_url:
            try:
                icon_response = requests.get(weather_data.icon_url)
                icon_image = Image.open(io.BytesIO(icon_response.content))
                # Make icon larger
                icon_image = icon_image.resize((100, 100), Image.LANCZOS)
                icon_photo = ImageTk.PhotoImage(icon_image)
                icon_label = tk.Label(info_frame, image=icon_photo, bg="white")
                icon_label.image = icon_photo  # Keep a reference
                icon_label.pack(pady=(0, 10))
            except Exception:
                # If icon loading fails, just show description text
                pass
        
        # Weather description
        tk.Label(info_frame, text=weather_data.description, font=("Arial", 16), 
                bg="white").pack(pady=(5, 20))
        
        # Temperature information in a frame
        temp_frame = tk.Frame(info_frame, bg="white")
        temp_frame.pack(pady=15, fill="x")
        
        tk.Label(temp_frame, text=f"{weather_data.temperature}°C", font=("Arial", 36, "bold"), 
                bg="white").pack(side="left", padx=20)
        
        feels_frame = tk.Frame(temp_frame, bg="white")
        feels_frame.pack(side="left", pady=10)
        
        tk.Label(feels_frame, text="Feels Like:", font=("Arial", 14), 
                bg="white").pack(anchor="w")
        tk.Label(feels_frame, text=f"{weather_data.feels_like}°C", font=("Arial", 14, "bold"), 
                bg="white").pack(anchor="w")
        
        # Add a separator for better visual organization
        separator = ttk.Separator(info_frame, orient='horizontal')
        separator.pack(fill='x', pady=20)
        
        # Details section with more spacing
        details_frame = tk.Frame(info_frame, bg="white")
        details_frame.pack(pady=10, fill="x")
        
        # Headers
        tk.Label(details_frame, text="Details", font=("Arial", 16, "bold"),
                bg="white").grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(0, 15))
        
        # Humidity with larger font and more spacing
        tk.Label(details_frame, text="Humidity:", font=("Arial", 14), 
                bg="white").grid(row=1, column=0, sticky="w", padx=10, pady=8)
        tk.Label(details_frame, text=f"{weather_data.humidity}%", font=("Arial", 14, "bold"), 
                bg="white").grid(row=1, column=1, sticky="w", pady=8)
        
        # Wind with larger font and more spacing
        tk.Label(details_frame, text="Wind Speed:", font=("Arial", 14), 
                bg="white").grid(row=2, column=0, sticky="w", padx=10, pady=8)
        tk.Label(details_frame, text=f"{weather_data.wind_speed:.1f} m/s", font=("Arial", 14, "bold"), 
                bg="white").grid(row=2, column=1, sticky="w", pady=8)
        
        # Add extra padding at the bottom
        tk.Label(info_frame, text="", bg="white").pack(pady=20)
        
        # Update the scroll region after the widgets are placed
        info_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))
    
    def display_error(self, error_type, message):
        """Display error information in the GUI"""
        error_frame = tk.Frame(self.weather_frame, bg="#ffcccc", padx=20, pady=20)
        error_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.4)
        
        tk.Label(error_frame, text=error_type, font=("Arial", 16, "bold"), 
                bg="#ffcccc", fg="#cc0000").pack(pady=(0, 10))
        
        tk.Label(error_frame, text=message, font=("Arial", 12), 
                bg="#ffcccc", wraplength=400).pack(pady=5)
        
        self.display_status_message(f"Error: {error_type}")
    
    def show_history(self):
        """Show recent search history"""
        if not self.recent_searches:
            messagebox.showinfo("History", "No recent searches.")
            return
        
        # Create a new top-level window for history
        history_window = tk.Toplevel(self.root)
        history_window.title("Recent Searches")
        history_window.geometry("500x350")  # Increase history window size
        history_window.resizable(True, True)
        
        # Create a frame for the history display
        history_frame = tk.Frame(history_window)
        history_frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Title label
        tk.Label(history_frame, text="Recent Weather Searches", 
                font=("Arial", 16, "bold")).pack(pady=(0, 15))
        
        # Create a list of recent searches
        list_frame = tk.Frame(history_frame)
        list_frame.pack(fill="both", expand=True)
        
        # Create a scrollable text area
        history_text = scrolledtext.ScrolledText(list_frame, width=40, height=10, wrap=tk.WORD)
        history_text.pack(fill="both", expand=True)
        
        # Insert history items
        for i, weather in enumerate(reversed(self.recent_searches), 1):
            date_time = datetime.fromtimestamp(weather.timestamp).strftime('%Y-%m-%d %H:%M')
            history_text.insert(tk.END, f"{i}. {date_time} - {weather.city}, {weather.country}: {weather.temperature}°C, {weather.description}\n\n")
        
        history_text.config(state="disabled")  # Make read-only
        
        # Add close button
        tk.Button(history_frame, text="Close", 
                 command=history_window.destroy, 
                 font=("Arial", 12),
                 bg="#4CAF50", fg="white", padx=10).pack(pady=10)

def main():
    try:
        root = tk.Tk()
        app = WeatherAppGUI(root)
        
        # Set minimum size to prevent window from being too small
        root.minsize(650, 600)
        
        # Center window on screen
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - 700) // 2
        y = (screen_height - 650) // 2
        root.geometry(f"+{x}+{y}")
        
        # Set app icon if available
        try:
            root.iconbitmap("weather_icon.ico")
        except:
            pass
            
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Application Error", f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
