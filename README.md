# Weather App

A Python application that displays current weather information for cities around the world using the WeatherAPI.com API.

## Course Outcomes Addressed

This application demonstrates:

1. **Display message on screen (a)**:
   - Formatted welcome banners
   - Status messages and loading indicators
   - Error messages with custom styling
   - Formatted weather data output

2. **Design classes for given problem (e)**:
   - `WeatherData` class to encapsulate weather information
   - `WeatherApp` class for console application functionality
   - `WeatherAppGUI` class for graphical interface functionality

3. **Handle exceptions (f)**:
   - Network connection errors
   - HTTP response errors
   - JSON parsing errors
   - Data structure errors
   - Generic exception handling

## Setup

1. Clone or download this repository
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
   
   If you encounter issues with the above command, try:
   ```
   python -m pip install -r requirements.txt
   ```
   
   Or install packages individually:
   ```
   pip install requests==2.28.1
   pip install pillow==9.2.0
   pip install python-dotenv==1.0.0
   ```
   
3. Create a `.env` file in the project root with your API key:
   ```
   WEATHER_API_KEY=your_api_key_here
   ```
4. Run the application:
   ```
   python weather_app.py
   ```

## Usage

### Command-line Version
1. Enter the name of a city when prompted
2. View the current weather information
3. Type 'history' to see recent searches
4. Enter another city or type 'quit' to exit

### GUI Version
1. Run the GUI application:
   ```
   python weather_app_gui.py
   ```
2. Enter the name of a city in the input field
3. Click the "Search" button
4. View the current weather information displayed in the GUI
5. Click the "History" button to see recent searches

### Security Note
- The `.env` file containing your API key is listed in `.gitignore` and will not be pushed to Git
- Never commit sensitive information like API keys directly in your code
- Each developer needs to create their own `.env` file locally with their API key

## Features

- Current temperature (in Celsius)
- "Feels like" temperature
- Weather conditions description
- Humidity percentage
- Wind speed
- Current date and time of the weather data
- Weather icons (GUI version)
- Recent searches history
- Secure API key management using environment variables

## Troubleshooting

### Common Errors and Solutions

1. **Package Installation Issues**
   
   If `pip install -r requirements.txt` fails, try these alternatives:
   
   - Use the full path to requirements.txt:
     ```
     pip install -r "/path/to/requirements.txt"
     ```
   
   - Check pip version:
     ```
     pip --version
     ```
     
   - Update pip:
     ```
     python -m pip install --upgrade pip
     ```
     
   - Install packages one by one:
     ```
     pip install requests
     pip install pillow
     pip install python-dotenv
     ```

2. **Missing Modules**
   
   If you see an error like `ModuleNotFoundError: No module named 'requests'` or `No module named 'dotenv'`, it means the required packages are not installed. Run:
   ```
   pip install -r requirements.txt
   ```

3. **API Key Issues**
   
   Error: `API key not found. Please set WEATHER_API_KEY in .env file.`
   
   Solution: Create or edit the `.env` file in the project root directory and add:
   ```
   WEATHER_API_KEY=your_api_key_here
   ```

4. **Connection Errors**
   
   Error: `Failed to connect to the weather service.`
   
   Solution: 
   - Check your internet connection
   - Verify that the API service is running by visiting [weatherapi.com](https://www.weatherapi.com/docs/)
   - Ensure your API key is valid and has sufficient credits

5. **City Not Found**
   
   Error: `City '{name}' not found.`
   
   Solution: 
   - Check the spelling of the city name
   - Try adding a country code (e.g., "London,UK" instead of just "London")
   - Use a more specific location name

6. **Display Issues in GUI**
   
   If elements are cut off or not visible in the GUI:
   - Resize the window to make it larger
   - Use the scrollbar to view all content
   - Try a lower screen resolution if available

7. **Python Version Compatibility**
   
   This app is tested with Python 3.7+. If you have errors related to syntax or incompatible features, check your Python version with:
   ```
   python --version
   ```

8. **Image Loading Issues**
   
   If weather icons don't appear in the GUI:
   - Check your internet connection
   - The app will continue to function without icons and will display text descriptions instead

For additional help, please submit an issue on the project's GitHub page or contact the developer.
