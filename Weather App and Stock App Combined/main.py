#Creating ONE GUI that hosts two apps (called Weather app and Stock app).
#this app will have 3 GUIs in total. One will be the main GUI and within that we will host two other GUIs.


# Creating ONE main window (GUI) that lets us open two apps:
# 1. A weather app to check the weather of a city
# 2. A stock app to check stock prices

import tkinter as tk  # This is a toolbox that helps us make buttons and windows.
from tkinter import messagebox  # This helps us show pop-up messages if something goes wrong.
import requests  # This helps us talk to the internet to get weather and stock data.
import time  # This helps us work with time, like showing sunrise and sunset times.

# 🌎 API keys (These are like special passwords that allow us to get weather and stock data)
WEATHER_API_KEY = "472ad775865e82e6b711fca01ae4a756"
STOCK_API_KEY = "0SU00ZDM262X3RQ8"

# 🟢 Function to open the Weather App Window
def open_weather_app():
    # 🌤️ Function to get the weather for a city
    def get_weather():
        city = city_entry.get()  # Get the city name from the input box.
        if not city:
            messagebox.showerror("Error", "Please enter a city name!")  # Show an error if no city is entered.
            return  # Stop the function if there is no city name.

        # 🔗 Create the magic internet link (API call) to get the weather data.
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url)  # Ask the internet for the weather data.
        data = response.json()  # Convert the internet response to a format our program understands.

        if data.get("cod") != 200:  # If the city name is wrong or not found
            messagebox.showerror("Error", "No such city exists!")  # Show an error.
            return  # Stop the function.

        # 📊 Extract weather details
        description = data['weather'][0]['description'].title()  # Get the weather condition (e.g., Clear, Rainy).
        temp = data['main']['temp']  # Get the temperature in Celsius.
        min_temp = int((data['main']['temp_min'] * 1.8) + 32)  # Convert the minimum temp from Celsius to Fahrenheit.
        max_temp = int((data['main']['temp_max'] * 1.8) + 32)  # Convert the maximum temp from Celsius to Fahrenheit.
        pressure = data['main']['pressure']  # Get the air pressure.
        humidity = data['main']['humidity']  # Get the humidity level.
        wind = data['wind']['speed']  # Get the wind speed.

        # Convert sunrise and sunset time from UTC to human-readable format
        sunrise = time.strftime('%I:%M:%S %p', time.gmtime(data['sys']['sunrise']))
        sunset = time.strftime('%I:%M:%S %p', time.gmtime(data['sys']['sunset']))

        # 📌 Show all the weather details in the window
        weather_label.config(text=f"🌤️ {description}\n"
                                  f"🌡️ Temp: {temp}°C\n"
                                  f"🔻 Min Temp: {min_temp}°F\n"
                                  f"🔺 Max Temp: {max_temp}°F\n"
                                  f"🌬️ Wind Speed: {wind} m/s\n"
                                  f"💧 Humidity: {humidity}%\n"
                                  f"⚖️ Pressure: {pressure} hPa\n"
                                  f"🌅 Sunrise: {sunrise}\n"
                                  f"🌇 Sunset: {sunset}")

    # 🏡 Create the Weather App window
    weather_window = tk.Toplevel(root)
    weather_window.title("Weather App")
    weather_window.geometry("350x350")

    tk.Label(weather_window, text="Enter City Name:").pack(pady=5)  # A label for city input
    city_entry = tk.Entry(weather_window, width=25)  # Input box for city name
    city_entry.pack(pady=5)

    tk.Button(weather_window, text="Get Weather", command=get_weather).pack(pady=10)  # Button to get weather
    weather_label = tk.Label(weather_window, text="", font=("Arial", 12), justify="left")  # Empty label to display weather details
    weather_label.pack(pady=10)

# 🟢 Function to open the Stock App Window
def open_stock_app():
    # 📈 Function to get the stock price of a company
    def get_stock_price():
        symbol = stock_entry.get().upper()  # Get the stock symbol and convert it to uppercase
        if not symbol:
            messagebox.showerror("Error", "Please enter a stock symbol!")  # Show an error if no stock symbol is entered.
            return  # Stop the function.

        # 🔗 Create the magic internet link (API call) to get stock data.
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={STOCK_API_KEY}"
        response = requests.get(url)  # Ask the internet for stock data.
        data = response.json()  # Convert the response to JSON format.

        # 🚨 Error Handling for Invalid Stock Symbol
        if "Global Quote" not in data or "05. price" not in data["Global Quote"]:
            messagebox.showerror("Error", "No such stock ticker exists!")  # Show an error if the stock symbol is incorrect.
            return  # Stop the function.

        # 📊 Extract stock details
        stock_name = symbol  # Get the stock name
        current_price = data["Global Quote"]["05. price"]  # Get the current stock price
        high_price = data["Global Quote"]["03. high"]  # Get the highest stock price today
        low_price = data["Global Quote"]["04. low"]  # Get the lowest stock price today
        close_price = data["Global Quote"]["08. previous close"]  # Get the closing stock price

        # 📌 Show stock details in the window
        stock_label.config(text=f"📈 Stock: {stock_name}\n"
                                f"💲 Current Price: ${current_price}\n"
                                f"📉 Lowest Price: ${low_price}\n"
                                f"📈 Highest Price: ${high_price}\n"
                                f"🔚 Closing Price: ${close_price}")

    # 🏡 Create the Stock App window
    stock_window = tk.Toplevel(root)
    stock_window.title("Stock Price Checker")
    stock_window.geometry("350x250")

    tk.Label(stock_window, text="Enter Stock Symbol:").pack(pady=5)  # A label for stock symbol input
    stock_entry = tk.Entry(stock_window, width=25)  # Input box for stock symbol
    stock_entry.pack(pady=5)

    tk.Button(stock_window, text="Get Stock Price", command=get_stock_price).pack(pady=10)  # Button to get stock price
    stock_label = tk.Label(stock_window, text="", font=("Arial", 12))  # Empty label to display stock details
    stock_label.pack(pady=10)

# 🔵 Main Window (GUI) that holds both apps
root = tk.Tk()
root.title("Multi-App Launcher")  # Title of the main window
root.geometry("300x200")  # Size of the main window

tk.Label(root, text="Choose an App", font=("Arial", 14)).pack(pady=10)  # Label for the main window

# 🟠 Buttons to open the two apps
weather_button = tk.Button(root, text="Weather", width=15, command=open_weather_app)
weather_button.pack(pady=5)

stock_button = tk.Button(root, text="Stock", width=15, command=open_stock_app)
stock_button.pack(pady=5)

# 🏁 Start the main window and keep it running
root.mainloop()


