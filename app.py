import streamlit as st
import pymysql
import pandas as pd

# Connect to MySQL database
def get_connection():
    return pymysql.connect(host='localhost', user='root', passwd='Lokesh#7', database='redbus_travel')

# Function to fetch route names from a specific state table starting with a specific letter
def fetch_route_names(connection, starting_letter, state):
    query = f"SELECT DISTINCT Route_name FROM {state}_routes WHERE Route_name LIKE '{starting_letter}%' ORDER BY Route_name"
    route_names = pd.read_sql(query, connection)['Route_name'].tolist()
    return route_names

# Function to fetch data from the project_info table based on selected ROUTE_NAME
def fetch_data(connection, route_name):
    query = "SELECT * FROM project_info WHERE Route_name = %s"
    df = pd.read_sql(query, connection, params=(route_name,))
    return df

# Function to filter data based on RATING and BUS_TYPE
def filter_data(df, ratings, bus_types):
    filtered_df = df[df['Ratings'].isin(ratings) & df['Bus_type'].isin(bus_types)]
    return filtered_df

# Terms and Conditions Content
def terms_and_conditions():
    st.header("Terms and Conditions")
    st.write("""
    1. General Terms
    - All users must provide accurate personal information for booking.
    - Bookings are non-refundable unless otherwise specified.
    
    2. Payment Terms
    - Payment must be completed online using valid payment methods.
    - The system will display total pricing, including applicable taxes.

    3. Cancellation and Refunds
    - Cancellations are subject to the terms set by each bus operator.
    - Refunds will be processed based on the cancellation policy of the operator.

    4. User Responsibilities
    - Users are responsible for providing correct travel details and adhering to the operator's policies.
    """)

# FAQ Content
def faq_section():
    st.header("Frequently Asked Questions (FAQ)")
    st.write("""
    1. How do I book a bus ticket?
    - You can book a bus ticket by selecting your desired route and bus type, then following the booking process on the homepage.

    2. What payment methods do you accept?
    - We accept major credit cards, debit cards, and online banking.

    3. Can I cancel my booking?
    - Yes, you can cancel your booking through the "Manage Booking" section. However, cancellations are subject to the operator's policies.

    4. How will I receive my booking confirmation?
    - Once your booking is successful, you will receive a confirmation email with your ticket details.
    """)

# Main Streamlit app
def main():
    st.sidebar.title("Navigation")
    
    # Sidebar - Option to choose between Booking, Terms and Conditions, and FAQ
    page = st.sidebar.radio("Go to", ["Bus Booking", "Terms and Conditions", "FAQ"])

    if page == "Bus Booking":
        st.header('Easy and Secure Online Bus Tickets Booking')

        connection = get_connection()

        try:
            # Sidebar - Input for starting letter
            starting_letter = st.sidebar.text_input('Enter Starting Letter of Route Name', 'A')
            
            # Sidebar - Selectbox for state
            states = ['kerala', 'andhra', 'telangana', 'kadamba', 'rajasthan', 
                      'southbengal', 'haryana', 'assam', 'uttarpradesh', 'westbengal']
            selected_state = st.sidebar.selectbox('Select State', states)

            # Fetch route names starting with the specified letter
            if starting_letter and selected_state:
                route_names = fetch_route_names(connection, starting_letter.lower(), selected_state)

                if route_names:
                    # Sidebar - Selectbox for ROUTE_NAME
                    selected_route = st.sidebar.radio('Select Route Name', route_names)

                    if selected_route:
                        # Fetch data based on selected ROUTE_NAME
                        data = fetch_data(connection, selected_route)

                        if not data.empty:
                            # Display data table with a subheader
                            st.write(f"### Data for Route: {selected_route}")
                            st.write(data)

                            # Filter by RATING and BUS_TYPE
                            ratings = data['Ratings'].unique().tolist()
                            selected_ratings = st.multiselect('Filter by Rating', ratings)

                            bus_types = data['Bus_type'].unique().tolist()
                            selected_bus_types = st.multiselect('Filter by Bus Type', bus_types)

                            if selected_ratings and selected_bus_types:
                                filtered_data = filter_data(data, selected_ratings, selected_bus_types)
                                # Display filtered data table with a subheader
                                st.write(f"### Filtered Data for Rating: {selected_ratings} and Bus Type: {selected_bus_types}")
                                st.write(filtered_data)

                                # Select number of seats
                                available_seats = filtered_data['Seats_Available'].sum()
                                if available_seats > 0:
                                    num_seats = st.number_input('Select Number of Seats', min_value=1, max_value=available_seats)

                                    # Display price information
                                    price_per_seat = filtered_data['Price'].mean()  # Average price for selected buses
                                    total_price = num_seats * price_per_seat

                                    st.write(f"Price per seat: ₹{price_per_seat:.2f}")
                                    st.write(f"Total price for {num_seats} seats: ₹{total_price:.2f}")

                                    # "Book Now" button
                                    if st.button('Book Now'):
                                        # Success message for successful booking
                                        st.success(f"Successfully booked {num_seats} seats for {selected_route} at ₹{total_price:.2f}!")
                                else:
                                    st.warning("No seats available for the selected filters.")
                        else:
                            st.write(f"No data found for Route: {selected_route}.")
                else:
                    st.write("No routes found starting with the specified letter.")
        finally:
            connection.close()

    elif page == "Terms and Conditions":
        terms_and_conditions()

    elif page == "FAQ":
        faq_section()

if __name__ == "__main__":
    main()
