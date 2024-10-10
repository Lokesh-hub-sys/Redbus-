import streamlit as st
import pymysql
import pandas as pd

# Connect to MySQL database
def get_connection():
    return pymysql.connect(host='localhost', user='root', passwd='Lokesh#7', database='redbus_travel')

# Function to fetch route names from a specific state table
def fetch_route_names(connection, state):
    query = f"SELECT DISTINCT Route_name FROM {state}_routes ORDER BY Route_name"
    route_names = pd.read_sql(query, connection)['Route_name'].tolist()
    return route_names

# Function to fetch data from the project_info table based on selected ROUTE_NAME
def fetch_data(connection, route_name):
    query = "SELECT * FROM project_info WHERE Route_name = %s"
    df = pd.read_sql(query, connection, params=(route_name,))
    return df

# Function to filter data based on selected criteria
def filter_data(df, selected_filters):
    filtered_df = df[
        (df['Ratings'] >= selected_filters['Min_Rating']) &
        (df['Ratings'] <= selected_filters['Max_Rating']) &
        (df['Bus_type'].isin(selected_filters['Bus_Type']))
    ]
    return filtered_df

# Main Streamlit app
def main():
    st.title("Booking")
    st.markdown("### Online Bus Ticket Booking")

    connection = get_connection()

    try:
        # Main booking section
        st.subheader("Select Your Route")
        states = ['kerala', 'andhra', 'telangana', 'kadamba', 'rajasthan', 
                  'southbengal', 'haryana', 'assam', 'uttarpradesh', 'westbengal']
        selected_state = st.selectbox('Select State', states)

        if selected_state:
            route_names = fetch_route_names(connection, selected_state)
            selected_route = st.selectbox('Select Route Name', route_names)

            if selected_route:
                data = fetch_data(connection, selected_route)
                st.write(f"### Available Buses for {selected_route}")
                st.dataframe(data)

                # Filters
                st.subheader("Select")
                selected_filters = {'Min_Rating': 0, 'Max_Rating': 5, 'Bus_Type': []}

                # Slider for Ratings
                min_rating, max_rating = st.slider('Select Rating Range', 0, 5, (0, 5))
                selected_filters['Min_Rating'] = min_rating
                selected_filters['Max_Rating'] = max_rating

                # Filter by Bus Type
                bus_types = data['Bus_type'].unique().tolist()
                selected_filters['Bus_Type'] = st.multiselect('Select Bus Types', bus_types)

                # Apply filters
                if selected_filters['Bus_Type'] or (selected_filters['Min_Rating'] < selected_filters['Max_Rating']):
                    filtered_data = filter_data(data, selected_filters)
                    if not filtered_data.empty:
                        st.write("### Filtered Results")
                        st.dataframe(filtered_data)

                        # Seat selection
                        available_seats = filtered_data['Seats_Available'].sum()
                        if available_seats > 0:
                            num_seats = st.number_input('Select Number of Seats', min_value=1, max_value=available_seats)
                            price_per_seat = filtered_data['Price'].mean()  # Average price for selected buses
                            total_price = num_seats * price_per_seat

                            st.write(f"Price per seat: ₹{price_per_seat:.2f}")
                            st.write(f"Total price for {num_seats} seats: ₹{total_price:.2f}")

                            # "Book Now" button
                            if st.button('Book Now'):
                                st.success(f"Successfully booked {num_seats} seats for {selected_route} at ₹{total_price:.2f}!")
                        else:
                            st.warning("No seats available for the selected filters.")
                    else:
                        st.warning("No results match the selected filters.")
                else:
                    st.info("Please select bus types or adjust the rating range to see results.")

    finally:
        connection.close()

if __name__ == "__main__":
    main()
