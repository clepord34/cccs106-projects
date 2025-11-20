# main.py
"""Weather Application using Flet v0.28.3"""

import flet as ft
import json
import asyncio
from weather_service import WeatherService
from config import Config
from pathlib import Path

class WeatherApp:
    """Main Weather Application class."""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.weather_service = WeatherService()
        self.history_file = Path("search_history.json")
        self.watchlist_file = Path("watchlist.json")
        self.search_history = self._load_json_file(self.history_file, [])
        self.watchlist = self._load_json_file(self.watchlist_file, [])
        self.current_unit = self._load_json_file(Path("unit_preference.json"), {"unit": "metric"}).get("unit", "metric")
        self.current_weather_data = None
        self.current_forecast_data = None
        self.watchlist_weather_data = {}
        self.setup_page()
        self.build_ui()
    
    def _load_json_file(self, file_path: Path, default):
        """Load JSON file or return default value."""
        if file_path.exists():
            with open(file_path, 'r') as f:
                return json.load(f)
        return default
    
    def _save_json_file(self, file_path: Path, data):
        """Save data to JSON file."""
        with open(file_path, 'w') as f:
            json.dump(data, f)
    
    def load_history(self):
        """Load search history from file."""
        return self._load_json_file(self.history_file, [])
    
    def save_history(self):
        """Save search history to file."""
        self._save_json_file(self.history_file, self.search_history)
    
    def add_to_history(self, city: str):
        """Add city to history, moving it to top if already exists."""
        # Remove city if it already exists to avoid duplicates
        if city in self.search_history:
            self.search_history.remove(city)
        
        # Add to the beginning (most recent)
        self.search_history.insert(0, city)
        
        # Keep only last 10 searches
        self.search_history = self.search_history[:10]
        self.save_history()
    
    def load_unit_preference(self):
        """Load temperature unit preference from file."""
        return self._load_json_file(Path("unit_preference.json"), {"unit": "metric"}).get("unit", "metric")
    
    def save_unit_preference(self):
        """Save temperature unit preference to file."""
        self._save_json_file(Path("unit_preference.json"), {"unit": self.current_unit})
    
    def load_watchlist(self):
        """Load city watchlist from file."""
        return self._load_json_file(self.watchlist_file, [])
    
    def save_watchlist(self):
        """Save city watchlist to file."""
        self._save_json_file(self.watchlist_file, self.watchlist)
    
    def setup_page(self):
        """Configure page settings."""
        self.page.title = Config.APP_TITLE
        
        # Add theme switcher
        self.page.theme_mode = ft.ThemeMode.SYSTEM  # Use system theme
        
        # Custom theme Colors
        self.page.theme = ft.Theme(
            color_scheme_seed=ft.Colors.BLUE,
        )
        
        self.page.padding = ft.padding.only(left=20, right=20)
        
        # Window properties are accessed via page.window object in Flet 0.28.3
        self.page.window.width = Config.APP_WIDTH
        self.page.window.height = Config.APP_HEIGHT
        self.page.window.resizable = False
        self.page.window.center()
    
    def build_ui(self):
        """Build the user interface."""

        # Theme toggle button
        self.theme_button = ft.IconButton(
            icon=ft.Icons.DARK_MODE,
            tooltip="Toggle theme",
            on_click=self.toggle_theme,
        )
        
        # Unit toggle button
        self.unit_button = ft.IconButton(
            icon=ft.Icons.THERMOSTAT,
            tooltip=f"Switch to {'°F' if self.current_unit == 'metric' else '°C'}",
            on_click=self.toggle_units,
        )

        # Title
        self.title = ft.Text(
            "Weather App",
            size=32,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLUE_700,
        )
        
        # Suggestions list container
        self.suggestions_column = ft.Column(
            spacing=0,
            tight=True,
        )
        
        self.suggestions_container = ft.Container(
            content=self.suggestions_column,
            bgcolor=ft.Colors.ON_INVERSE_SURFACE,
            border=ft.border.all(1, ft.Colors.BLUE_200),
            border_radius=5,
            visible=False,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
            padding=5,
        ) 
        
        # City input field
        self.city_input = ft.TextField(
            label="Enter city name",
            hint_text="e.g., London, Tokyo, New York",
            border_color=ft.Colors.BLUE_400,
            prefix_icon=ft.Icons.LOCATION_CITY,
            on_submit=self.on_search,
            on_change=self.on_input_change,
            on_focus=self.on_input_focus,
            on_blur=self.on_input_blur,
            expand=True,
        )
        
        # Search button
        self.search_button = ft.IconButton(
            icon=ft.Icons.SEARCH,
            on_click=self.on_search,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE_700,
            ),
        )
        
        # Tabs for current weather and forecast
        self.weather_tab = ft.Tab(
            text="Current",
            icon=ft.Icons.WB_SUNNY,
        )
        
        self.forecast_tab = ft.Tab(
            text="5-Day Forecast",
            icon=ft.Icons.CALENDAR_TODAY,
        )
        
        self.comparison_tab = ft.Tab(
            text="Compare Cities",
            icon=ft.Icons.COMPARE,
        )
        
        self.tabs = ft.Tabs(
            selected_index=0,
            tabs=[self.weather_tab, self.forecast_tab, self.comparison_tab],
            visible=False,
            on_change=self.on_tab_change,
            tab_alignment=ft.TabAlignment.CENTER
        )
        
        # Weather display container (initially hidden)
        self.weather_container = ft.Container(
            visible=False,
            border=ft.border.all(1, ft.Colors.BLUE_200),
            border_radius=10,
            padding=20,
        )
        
        # Forecast display container
        self.forecast_container = ft.Container(
            visible=False,
            border=ft.border.all(1, ft.Colors.BLUE_200),
            border_radius=10,
            padding=20,
        )
        
        # Comparison container
        self.comparison_container = ft.Container(
            visible=False,
            border=ft.border.all(1, ft.Colors.BLUE_200),
            border_radius=10,
            padding=20,
        )
        
        # Error message
        self.error_message = ft.Text(
            "",
            color=ft.Colors.RED_700,
            visible=False,
        )
        
        # Loading indicator
        self.loading = ft.ProgressRing(visible=False)
        
        # Add all components to page
        title_row = ft.Row(
            [
                self.title,
                ft.Row(
                    [
                        self.unit_button,
                        self.theme_button,
                    ],
                    spacing=5,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        # Add all components to page
        
        self.page.overlay.append(self.suggestions_container)
        
        self.page.add(
            ft.Column(
                [
                    title_row,
                    ft.Divider(height=5, color=ft.Colors.TRANSPARENT),
                    ft.Row(
                        [
                            self.city_input,
                            self.search_button,
                        ],
                        spacing=5,
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.START,
                    ),
                    self.loading,
                    self.error_message,
                    self.tabs,
                    self.weather_container,
                    self.forecast_container,
                    self.comparison_container,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            )
        )
        
        # Build comparison UI
        self.build_comparison_ui()
    
    def on_input_focus(self, e):
        """Show suggestions when input is focused."""
        if self.search_history:
            self.update_suggestions(self.city_input.value or "")
    
    def on_input_blur(self, e):
        """Hide suggestions when input loses focus (with delay)."""
        # Delay to allow click on suggestion
        async def hide_delayed():
            await asyncio.sleep(0.2)
            self.suggestions_container.visible = False
            self.page.update()
        
        self.page.run_task(hide_delayed)
    
    def on_input_change(self, e):
        """Filter suggestions as user types."""
        self.update_suggestions(e.control.value)
    
    def update_suggestions(self, query: str):
        """Update suggestion list based on query."""
        query_lower = query.lower().strip()
        
        # Filter history based on query
        if query_lower:
            filtered = [city for city in self.search_history if query_lower in city.lower()]
        else:
            filtered = self.search_history[:5]  # Show top 5 when no query
        
        # Clear current suggestions
        self.suggestions_column.controls.clear()
        
        if filtered:
            for city in filtered:
                suggestion_button = ft.Container(
                    content=ft.Row(
                        [
                            ft.Text(
                                city,
                                size=13,
                                color=ft.Colors.ON_SURFACE,
                                expand=True,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.CLOSE,
                                icon_size=14,
                                icon_color=ft.Colors.GREY_600,
                                tooltip="Remove from history",
                                on_click=lambda e, c=city: self.remove_from_history(c),
                                style=ft.ButtonStyle(
                                    padding=ft.padding.all(4),
                                ),
                            ),
                        ],
                        spacing=0,
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=ft.padding.only(left=8, top=4, bottom=4, right=0),
                    bgcolor=ft.Colors.TRANSPARENT,
                    ink=True,
                    on_click=lambda e, c=city: self.on_suggestion_click(c),
                    border_radius=3,
                    on_hover=lambda e: self.on_suggestion_hover(e),
                )
                self.suggestions_column.controls.append(suggestion_button)
            
            # Position the suggestions container below the input field
            # Calculate position based on input field
            self.suggestions_container.top = 118  # Approximate position below search field
            self.suggestions_container.left = 20
            self.suggestions_container.right = 65
            self.suggestions_container.visible = True
        else:
            self.suggestions_container.visible = False
        
        self.page.update()
    
    def on_suggestion_hover(self, e):
        """Handle hover effect on suggestions."""
        if e.data == "true":
            e.control.bgcolor = ft.Colors.with_opacity(0.05, ft.Colors.ON_SURFACE)
        else:
            e.control.bgcolor = ft.Colors.TRANSPARENT
        e.control.update()
    
    def on_suggestion_click(self, city: str):
        """Handle suggestion click."""
        self.city_input.value = city
        self.suggestions_container.visible = False
        self.page.update()
        self.page.run_task(self.get_weather)
    
    def remove_from_history(self, city: str):
        """Remove a city from search history."""
        if city in self.search_history:
            self.search_history.remove(city)
            self.save_history()
            # Refresh suggestions to reflect the change
            self.update_suggestions(self.city_input.value or "")
    
    def on_tab_change(self, e):
        """Handle tab switching between current weather, forecast, and comparison."""
        tab_index = e.control.selected_index
        
        # Set visibility for all containers
        self.weather_container.visible = (tab_index == 0)
        self.forecast_container.visible = (tab_index == 1)
        self.comparison_container.visible = (tab_index == 2)
        
        # Refresh comparison data when tab is opened
        if tab_index == 2:
            self.page.run_task(self.refresh_comparison)
        
        self.page.update()
    
    def toggle_theme(self, e):
        """Toggle between light and dark theme."""
        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.theme_button.icon = ft.Icons.LIGHT_MODE
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.theme_button.icon = ft.Icons.DARK_MODE
        self.page.update()
    
    def toggle_units(self, e):
        """Toggle between Celsius and Fahrenheit."""
        if self.current_unit == "metric":
            self.current_unit = "imperial"
        else:
            self.current_unit = "metric"
        
        # Update button tooltip
        self.unit_button.tooltip = f"Switch to {'°F' if self.current_unit == 'metric' else '°C'}"
        
        # Save preference
        self.save_unit_preference()
        
        # Store current tab state
        current_tab = self.tabs.selected_index if self.tabs.visible else 0
        
        # Redisplay if weather data exists
        if self.current_weather_data:
            self.display_weather(self.current_weather_data)
        
        # Redisplay if forecast data exists
        if self.current_forecast_data:
            self.display_forecast(self.current_forecast_data)
        
        # Redisplay comparison data
        if self.watchlist_weather_data:
            self.update_comparison_display()
        
        # Restore tab visibility state
        if self.tabs.visible:
            if current_tab == 0:
                self.weather_container.visible = True
                self.forecast_container.visible = False
                self.comparison_container.visible = False
            elif current_tab == 1:
                self.weather_container.visible = False
                self.forecast_container.visible = True
                self.comparison_container.visible = False
            else:
                self.weather_container.visible = False
                self.forecast_container.visible = False
                self.comparison_container.visible = True
        
        self.page.update()
    
    def convert_temp(self, temp_celsius):
        """Convert temperature based on current unit."""
        return (temp_celsius * 9/5) + 32 if self.current_unit == "imperial" else temp_celsius
    
    def get_unit_symbol(self):
        """Get temperature unit symbol."""
        return "°F" if self.current_unit == "imperial" else "°C"
    
    def _extract_weather_data(self, data: dict):
        """Extract common weather data fields."""
        return {
            "city_name": data.get("name", "Unknown"),
            "country": data.get("sys", {}).get("country", ""),
            "temp_celsius": data.get("main", {}).get("temp", 0),
            "feels_like_celsius": data.get("main", {}).get("feels_like", 0),
            "humidity": data.get("main", {}).get("humidity", 0),
            "pressure": data.get("main", {}).get("pressure", 0),
            "cloudiness": data.get("clouds", {}).get("all", 0),
            "description": data.get("weather", [{}])[0].get("description", "").title(),
            "icon_code": data.get("weather", [{}])[0].get("icon", "01d"),
            "wind_speed": data.get("wind", {}).get("speed", 0),
        }
        
    def on_search(self, e):
        """Handle search button click or enter key press."""
        self.page.run_task(self.get_weather)
    
    async def get_weather(self):
        """Fetch and display weather data."""
        city = self.city_input.value.strip()
        
        # Validate input
        if not city:
            self.show_error("Please enter a city name")
            return
        
        # Show loading, hide previous results
        self.loading.visible = True
        self.error_message.visible = False
        self.weather_container.visible = False
        self.forecast_container.visible = False
        self.tabs.visible = False
        self.page.update()
        
        try:
            # Fetch both current weather and forecast data
            weather_data, forecast_data = await asyncio.gather(
                self.weather_service.get_weather(city),
                self.weather_service.get_forecast(city, self.current_unit),
            )
            
            # Display weather and forecast
            self.display_weather(weather_data)
            self.display_forecast(forecast_data)
            
            # Show tabs
            self.tabs.visible = True
            self.tabs.selected_index = 0  # Start with current weather
            self.weather_container.visible = True
            self.forecast_container.visible = False
            
        except Exception as e:
            self.show_error(str(e))
        
        finally:
            self.loading.visible = False
            self.page.update()
    
    def display_forecast(self, data: dict):
        """Display 5-day weather forecast."""
        # Store forecast data
        self.current_forecast_data = data
        
        # Parse forecast data - API returns 3-hour intervals
        forecast_list = data.get("list", [])
        
        # Group forecasts by day
        from datetime import datetime
        daily_forecasts = {}
        
        for item in forecast_list:
            # Get date from timestamp
            dt = datetime.fromtimestamp(item["dt"])
            date_key = dt.strftime("%Y-%m-%d")
            
            if date_key not in daily_forecasts:
                daily_forecasts[date_key] = {
                    "temps": [],
                    "conditions": [],
                    "icons": [],
                    "date": dt,
                }
            
            temp = item["main"]["temp"]
            daily_forecasts[date_key]["temps"].append(temp)
            daily_forecasts[date_key]["conditions"].append(
                item["weather"][0]["description"]
            )
            daily_forecasts[date_key]["icons"].append(
                item["weather"][0]["icon"]
            )
        
        # Create forecast cards for next 5 days
        forecast_cards = []
        sorted_dates = sorted(daily_forecasts.keys())[:5]
        
        for date_key in sorted_dates:
            day_data = daily_forecasts[date_key]
            temps = day_data["temps"]
            high_temp = self.convert_temp(max(temps))
            low_temp = self.convert_temp(min(temps))
            
            # Get most common weather condition and icon
            most_common_condition = max(set(day_data["conditions"]), 
                                       key=day_data["conditions"].count)
            most_common_icon = max(set(day_data["icons"]), 
                                  key=day_data["icons"].count)
            
            # Format date
            day_name = day_data["date"].strftime("%A")
            date_str = day_data["date"].strftime("%b %d")
            
            unit_symbol = self.get_unit_symbol()
            
            # Create forecast card
            card = ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            day_name,
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLUE_900,
                        ),
                        ft.Text(
                            date_str,
                            size=14,
                            color=ft.Colors.GREY_600,
                        ),
                        ft.Container(
                            ft.Image(
                                src=f"https://openweathermap.org/img/wn/{most_common_icon}@2x.png",
                                width=80,
                                height=80,
                            ),
                            bgcolor=ft.Colors.GREY_400,
                            border_radius=5,
                        ),
                        ft.Text(
                            most_common_condition.title(),
                            size=14,
                            text_align=ft.TextAlign.CENTER,
                            color=ft.Colors.GREY_800,
                        ),
                        ft.Row(
                            [
                                ft.Column(
                                    [
                                        ft.Text("High", size=12, color=ft.Colors.GREY_600),
                                        ft.Text(
                                            f"{high_temp:.0f}{unit_symbol}",
                                            size=20,
                                            weight=ft.FontWeight.BOLD,
                                            color=ft.Colors.RED_700,
                                        ),
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                ),
                                ft.VerticalDivider(width=20),
                                ft.Column(
                                    [
                                        ft.Text("Low", size=12, color=ft.Colors.GREY_600),
                                        ft.Text(
                                            f"{low_temp:.0f}{unit_symbol}",
                                            size=20,
                                            weight=ft.FontWeight.BOLD,
                                            color=ft.Colors.BLUE_700,
                                        ),
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=5,
                ),
                bgcolor=ft.Colors.WHITE,
                border=ft.border.all(1, ft.Colors.BLUE_200),
                border_radius=10,
                padding=15,
                width=180,
            )
            forecast_cards.append(card)
        
        # Display forecast cards
        self.forecast_container.content = ft.Column(
            [
                ft.Text(
                    "5-Day Weather Forecast",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_700,
                ),
                ft.Row(
                    forecast_cards,
                    alignment=ft.MainAxisAlignment.CENTER,
                    wrap=True,
                    spacing=10,
                    run_spacing=10,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
        )
        
        self.page.update()
    
    def display_weather(self, data: dict):
        """Display weather information."""
        # Store current weather data
        self.current_weather_data = data
        
        # Extract data using helper
        weather = self._extract_weather_data(data)
        
        # Convert temperatures
        temp = self.convert_temp(weather["temp_celsius"])
        feels_like = self.convert_temp(weather["feels_like_celsius"])
        unit_symbol = self.get_unit_symbol()
        
        # Add to search history
        self.add_to_history(weather["city_name"])
        
        # Build weather display
        self.weather_container.content = ft.Column(
            [
                # Location
                ft.Text(
                    f"{weather['city_name']}, {weather['country']}",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Container(
                    # Weather icon and description
                    ft.Row(
                        [
                            ft.Image(
                                src=f"https://openweathermap.org/img/wn/{weather['icon_code']}@2x.png",
                                width=100,
                                height=100,
                            ),
                            ft.Text(
                                weather['description'],
                                size=20,
                                italic=True,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.ON_SURFACE_VARIANT),
                    border_radius=10,
                ),
                
                # Temperature
                ft.Text(
                    f"{temp:.1f}{unit_symbol}",
                    size=48,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_900,
                ),
                
                ft.Text(
                    f"Feels like {feels_like:.1f}{unit_symbol}",
                    size=16,
                    color=ft.Colors.with_opacity(0.9, ft.Colors.ON_SURFACE_VARIANT)
                ),
                
                ft.Divider(),
                
                # Additional info
                ft.Row(
                    [
                        self.create_info_card(ft.Icons.WATER_DROP, "Humidity", f"{weather['humidity']}%"),
                        self.create_info_card(ft.Icons.AIR, "Wind Speed", f"{weather['wind_speed']} m/s"),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Row(
                    [
                        self.create_info_card(ft.Icons.COMPRESS, "Pressure", f"{weather['pressure']} hPa"),
                        self.create_info_card(ft.Icons.CLOUD, "Cloudiness", f"{weather['cloudiness']} %"),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )

        # Show weather container with fade animation
        self.weather_container.animate_opacity = 300
        self.weather_container.opacity = 0
        self.weather_container.visible = True
        self.error_message.visible = False
        self.page.update()

        # Fade in animation
        async def fade_in():
            await asyncio.sleep(0.1)
            self.weather_container.opacity = 1
            self.page.update()

        # Check for high temperature alert
        if temp > 35:
            alert = ft.Banner(
                bgcolor=ft.Colors.AMBER_100,
                leading=ft.Icon(ft.Icons.WARNING, color=ft.Colors.AMBER, size=40),
                content=ft.Text("⚠️ High temperature alert!"),
                actions=[
                    ft.TextButton("OK", on_click=lambda e: setattr(self.page.banner, 'open', False) or self.page.update()),
                ],
            )
            self.page.banner = alert
            self.page.banner.open = True
            self.page.update()
        
        self.page.run_task(fade_in)



    def create_info_card(self, icon, label, value):
        """Create an info card for weather details."""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(icon, size=30, color=ft.Colors.BLUE_700),
                    ft.Text(label, size=12, color=ft.Colors.GREY_600),
                    ft.Text(
                        value,
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_900,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            ),
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            padding=15,
            width=150,
            border=ft.border.all(1, ft.Colors.BLUE_200)
        )
    
    def show_error(self, message: str):
        """Display error message."""
        self.error_message.value = f"❌ {message}"
        self.error_message.visible = True
        self.weather_container.visible = False
        self.page.update()
    
    def build_comparison_ui(self):
        """Build the comparison tab UI."""
        # Input for adding cities to watchlist
        self.watchlist_input = ft.TextField(
            label="Add city to watchlist",
            hint_text="Enter city name",
            border_color=ft.Colors.BLUE_400,
            prefix_icon=ft.Icons.ADD_LOCATION,
            on_submit=lambda e: self.page.run_task(self.add_to_watchlist),
            expand=True,
        )
        
        self.add_watchlist_button = ft.IconButton(
            icon=ft.Icons.ADD,
            tooltip="Add city",
            on_click=lambda e: self.page.run_task(self.add_to_watchlist),
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.GREEN_700,
            ),
        )
        
        # Container for comparison cards
        self.comparison_cards_container = ft.Column(
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
        )
        
        # Build initial comparison view
        self.update_comparison_display()
    
    async def add_to_watchlist(self):
        """Add a city to the watchlist."""
        city = self.watchlist_input.value.strip()
        
        if not city:
            self.show_error("Please enter a city name")
            return
        
        if city in self.watchlist:
            self.show_error(f"{city} is already in your watchlist")
            return
        
        # Show loading
        self.loading.visible = True
        self.error_message.visible = False
        self.page.update()
        
        try:
            # Verify city exists by fetching weather
            weather_data = await self.weather_service.get_weather(city)
            city_name = weather_data.get("name", city)
            
            # Add to watchlist
            self.watchlist.append(city_name)
            self.save_watchlist()
            
            # Clear input
            self.watchlist_input.value = ""
            
            # Refresh comparison display
            await self.refresh_comparison()
            
        except Exception as e:
            self.show_error(str(e))
        finally:
            self.loading.visible = False
            self.page.update()
    
    def remove_from_watchlist(self, city: str):
        """Remove a city from the watchlist."""
        if city in self.watchlist:
            self.watchlist.remove(city)
            self.save_watchlist()
            if city in self.watchlist_weather_data:
                del self.watchlist_weather_data[city]
            self.update_comparison_display()
    
    async def refresh_comparison(self):
        """Refresh weather data for all cities in watchlist."""
        if not self.watchlist:
            self.update_comparison_display()
            return
        
        # Show loading
        self.loading.visible = True
        self.error_message.visible = False
        self.page.update()
        
        try:
            # Fetch weather for all cities
            tasks = [self.weather_service.get_weather(city) for city in self.watchlist]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Store results
            self.watchlist_weather_data = {}
            for city, result in zip(self.watchlist, results):
                if isinstance(result, Exception):
                    print(f"Error fetching weather for {city}: {result}")
                else:
                    self.watchlist_weather_data[city] = result
            
            # Update display
            self.update_comparison_display()
            
        except Exception as e:
            self.show_error(str(e))
        finally:
            self.loading.visible = False
            self.page.update()
    
    def update_comparison_display(self):
        """Update the comparison display with current watchlist."""
        # Clear current cards
        self.comparison_cards_container.controls.clear()
        
        if not self.watchlist:
            # Show empty state
            self.comparison_cards_container.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(ft.Icons.ADD_LOCATION_ALT, size=80, color=ft.Colors.GREY_400),
                            ft.Text(
                                "No cities in watchlist",
                                size=20,
                                color=ft.Colors.GREY_600,
                            ),
                            ft.Text(
                                "Add cities to compare their weather",
                                size=14,
                                color=ft.Colors.GREY_500,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    padding=40,
                    alignment=ft.alignment.center,
                )
            )
        else:
            # Create comparison cards
            for city in self.watchlist:
                weather_data = self.watchlist_weather_data.get(city)
                card = self.create_comparison_card(city, weather_data)
                self.comparison_cards_container.controls.append(card)
        
        # Update comparison container
        self.comparison_container.content = ft.Column(
            [
                ft.Text(
                    "Compare Cities",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_700,
                ),
                ft.Row(
                    [
                        self.watchlist_input,
                        self.add_watchlist_button,
                    ],
                    spacing=10,
                ),
                ft.Divider(height=20),
                self.comparison_cards_container,
            ],
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
        )
        
        self.page.update()
    
    def create_comparison_card(self, city: str, weather_data: dict = None):
        """Create a comparison card for a city."""
        if weather_data is None:
            # Loading or error state
            return ft.Container(
                content=ft.Row(
                    [
                        ft.Text(city, size=18, weight=ft.FontWeight.BOLD),
                        ft.ProgressRing(width=20, height=20),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                bgcolor=ft.Colors.WHITE,
                border=ft.border.all(1, ft.Colors.BLUE_200),
                border_radius=10,
                padding=20,
            )
        
        # Extract weather data using helper
        weather = self._extract_weather_data(weather_data)
        temp = self.convert_temp(weather["temp_celsius"])
        feels_like = self.convert_temp(weather["feels_like_celsius"])
        unit_symbol = self.get_unit_symbol()
        
        # Create card with better layout
        return ft.Container(
            content=ft.Column(
                [
                    # Top row - City name and delete button
                    ft.Row(
                        [
                            ft.Text(
                                f"{weather['city_name']}, {weather['country']}",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.BLUE_900,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                icon_color=ft.Colors.RED_700,
                                tooltip="Remove from watchlist",
                                on_click=lambda e, c=city: self.remove_from_watchlist(c),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    # Main content row
                    ft.Row(
                        [
                            # Left - Weather icon and description
                            ft.Column(
                                [
                                    ft.Container(
                                        ft.Image(
                                            src=f"https://openweathermap.org/img/wn/{weather['icon_code']}@2x.png",
                                            width=60,
                                            height=60,
                                        ),
                                        bgcolor=ft.Colors.GREY_400,
                                        border_radius=5,
                                    ),
                                    ft.Text(
                                        weather['description'],
                                        size=12,
                                        italic=True,
                                        color=ft.Colors.GREY_700,
                                        text_align=ft.TextAlign.CENTER,
                                    ),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=5,
                            ),
                            # Middle - Temperature
                            ft.Column(
                                [
                                    ft.Text(
                                        f"{temp:.1f}{unit_symbol}",
                                        size=32,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.BLUE_900,
                                    ),
                                    ft.Text(
                                        f"Feels like {feels_like:.1f}{unit_symbol}",
                                        size=11,
                                        color=ft.Colors.GREY_600,
                                    ),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=5,
                            ),
                            # Right - Additional info
                            ft.Column(
                                [
                                    ft.Row(
                                        [
                                            ft.Icon(ft.Icons.WATER_DROP, size=16, color=ft.Colors.BLUE_700),
                                            ft.Text(f"{weather['humidity']}%", size=13, color=ft.Colors.GREY_700),
                                        ],
                                        spacing=5,
                                    ),
                                    ft.Row(
                                        [
                                            ft.Icon(ft.Icons.AIR, size=16, color=ft.Colors.BLUE_700),
                                            ft.Text(f"{weather['wind_speed']} m/s", size=13, color=ft.Colors.GREY_700),
                                        ],
                                        spacing=5,
                                    ),
                                ],
                                spacing=8,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                        spacing=10,
                    ),
                ],
                spacing=5,
            ),
            bgcolor=ft.Colors.WHITE,
            border=ft.border.all(1, ft.Colors.BLUE_200),
            border_radius=10,
            padding=15,
        )


def main(page: ft.Page):
    """Main entry point."""
    WeatherApp(page)


if __name__ == "__main__":
    ft.app(target=main)