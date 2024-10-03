from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import os
import time
# State links
state_links = [
    "https://www.redbus.in/online-booking/ksrtc-kerala/?utm_source=rtchometile",
    "https://www.redbus.in/online-booking/apsrtc/?utm_source=rtchometile",
    "https://www.redbus.in/online-booking/tsrtc/?utm_source=rtchometile",
    "https://www.redbus.in/online-booking/ktcl/?utm_source=rtchometile",
    "https://www.redbus.in/online-booking/rsrtc/?utm_source=rtchometile",
    "https://www.redbus.in/online-booking/south-bengal-state-transport-corporation-sbstc/?utm_source=rtchometile",
    "https://www.redbus.in/online-booking/hrtc/?utm_source=rtchometile",
    "https://www.redbus.in/online-booking/astc/?utm_source=rtchometile",
    "https://www.redbus.in/online-booking/uttar-pradesh-state-road-transport-corporation-upsrtc/?utm_source=rtchometile",
    "https://www.redbus.in/online-booking/wbtc-ctc/?utm_source=rtchometile"
]

# Initialize the WebDriver
driver = webdriver.Chrome()
wait = WebDriverWait(driver, 20)

# Helper function to scroll to an element and click it
def scroll_to_and_click(driver, element):
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    time.sleep(2)  # Ensure some time for scrolling
    driver.execute_script("arguments[0].click();", element)

# Function to retrieve bus routes for a state
def get_state_bus_routes(state_link, path="//a[@class='route']"):
    driver.get(state_link)
    time.sleep(3)
    driver.maximize_window()
    
    links = []
    routes = []
    
    for i in range(1, 4):  # Adjust the range based on the number of pages
        paths = driver.find_elements(By.XPATH, path)
        
        # Collect route links and names
        for link in paths:
            href = link.get_attribute("href")
            route_name = link.text.strip()  # Ensure full route name is collected
            if href and route_name:  # Ensure both name and link are not empty
                links.append(href)
                routes.append(route_name)
        
        try:
            # Check if next page exists and navigate
            pagination = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@class="DC_117_paginationTable"]')))
            next_button_xpath = f'//div[@class="DC_117_pageTabs " and text()="{i+1}"]'
            next_button = driver.find_element(By.XPATH, next_button_xpath)
            scroll_to_and_click(driver, next_button)
        
        except NoSuchElementException:
            print(f"No more pages for state: {state_link}")
            break
    
    # Return DataFrame with full route names and links
    return pd.DataFrame({"Route_name": routes, "Route_link": links})

# Initialize final DataFrame to collect all state data
all_states_data = pd.DataFrame()

# Iterate through each state and collect data
for state_link in state_links:
    df_state = get_state_bus_routes(state_link)
    all_states_data = pd.concat([all_states_data, df_state], ignore_index=True)

# Check if file path is accessible before saving
output_path_routes = r"C:\Users\lokes\OneDrive\Documents\bus_data\all_routes1.csv"  # Change path if needed
if os.path.exists(output_path_routes):
    if not os.access(output_path_routes, os.W_OK):
        print(f"File at {output_path_routes} is not writable. Please check permissions.")
else:
    print(f"Saving routes data to {output_path_routes}")
    all_states_data.to_csv(output_path_routes, index=False, encoding='utf-8-sig')

# Function to collect detailed bus information from each route link
def get_bus_details(df):
    Bus_names = []
    Bus_types = []
    Start_Time = []
    End_Time = []
    Total_Duration = []
    Prices = []
    Seats_Available = []
    Ratings = []
    Route_links = []
    Route_names = []
    
    for i, row in df.iterrows():
        link = row["Route_link"]
        route = row["Route_name"]
        
        driver.get(link)
        time.sleep(2)
        
        try:
            bus_name_elements = driver.find_elements(By.XPATH, "//div[@class='travels lh-24 f-bold d-color']")
            bus_type_elements = driver.find_elements(By.XPATH, "//div[@class='bus-type f-12 m-top-16 l-color evBus']")
            start_time_elements = driver.find_elements(By.XPATH, "//*[@class='dp-time f-19 d-color f-bold']")
            end_time_elements = driver.find_elements(By.XPATH, "//*[@class='bp-time f-19 d-color disp-Inline']")
            total_duration_elements = driver.find_elements(By.XPATH, "//*[@class='dur l-color lh-24']")
            rating_elements = driver.find_elements(By.XPATH, "//div[@class='clearfix row-one']/div[@class='column-six p-right-10 w-10 fl']")
            price_elements = driver.find_elements(By.XPATH, '//*[@class="fare d-block"]')
            seats_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'seat-left')]")
            
            for bus in bus_name_elements:
                Bus_names.append(bus.text)
                Route_links.append(link)
                Route_names.append(route)
            
            for bus_type in bus_type_elements:
                Bus_types.append(bus_type.text)
                
            for start_time in start_time_elements:
                Start_Time.append(start_time.text)
                
            for end_time in end_time_elements:
                End_Time.append(end_time.text)
                
            for duration in total_duration_elements:
                Total_Duration.append(duration.text)
                
            for rating in rating_elements:
                Ratings.append(rating.text)
                
            for price in price_elements:
                Prices.append(price.text)
                
            for seat in seats_elements:
                Seats_Available.append(seat.text)
        
        except NoSuchElementException:
            print(f"Failed to extract data for route: {route}")
            continue
    
    # Create DataFrame from collected bus details
    bus_data = pd.DataFrame({
        "Bus_name": Bus_names,
        "Bus_type": Bus_types,
        "Start_time": Start_Time,
        "End_time": End_Time,
        "Total_duration": Total_Duration,
        "Price": Prices,
        "Seats_Available": Seats_Available,
        "Ratings": Ratings,
        "Route_link": Route_links,
        "Route_name": Route_names
    })
    
    return bus_data

# Get detailed bus information from the routes
bus_details_df = get_bus_details(all_states_data)

# Check if file path is accessible before saving bus details
output_path_bus_details = r"C:\Users\lokes\OneDrive\Documents\bus_data\redbus.csv"  # Change path if needed
if os.path.exists(output_path_bus_details):
    if not os.access(output_path_bus_details, os.W_OK):
        print(f"File at {output_path_bus_details} is not writable. Please check permissions.")
else:
    print(f"Saving bus details to {output_path_bus_details}")
    bus_details_df.to_csv(output_path_bus_details, index=False, encoding='utf-8-sig')

# Close the browser
driver.quit()
print("Data collection completed and saved.")
