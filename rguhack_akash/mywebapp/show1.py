from flask import Flask, render_template, request
import pandas as pd
from datetime import datetime

app = Flask(__name__)

# Load the dataset
merged_df = pd.read_csv("output_dataset.csv")

def calculate_fuel_cost_per_mile(row, miles):
    petrol_price_per_litre = 1.4251  # £/litre
    diesel_price_per_litre = 1.5090  # £/litre
    gallons_to_litres_conversion_factor = 5.549  # 1 Gallons = 5.549 litres
    
    if row['fueltype'] == 'petrol':
        fuel_price_per_litre = petrol_price_per_litre
    else:
        fuel_price_per_litre = diesel_price_per_litre
    
    litres_per_mile = row['mpg'] / gallons_to_litres_conversion_factor
    fuel_cost_per_mile = litres_per_mile * fuel_price_per_litre  # £ per mile
    
    return fuel_cost_per_mile * miles

@app.route('/')
def index():
    return render_template('index1.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    make = request.form['carName'].lower()
    car_year = int(request.form['carAge'])
    miles = int(request.form['carMiles'])
    years = int(request.form['totalYears'])
    fueltype = request.form['fuelType'].lower()

    current_year = datetime.now().year
    car_age = current_year - car_year

    # Load purchase cost and maintenance cost from dataset
    car_data_user_choice_car = merged_df[(merged_df['make'] == make) & (merged_df['year'] == car_age) & (merged_df['fueltype'] == fueltype)].copy()
    car_data_given_choice_year = merged_df[(merged_df['make'] != make) & (merged_df['year'] == car_age) & (merged_df['fueltype'] == fueltype)].copy()

    if not car_data_user_choice_car.empty:
        car_data_user_choice_car['fuel_cost'] = car_data_user_choice_car.apply(calculate_fuel_cost_per_mile, miles=miles, axis=1)
        car_data_user_choice_car['maintenance_cost'] = car_data_user_choice_car['maintenancecostyearly'] * years
        car_data_user_choice_car['tax_cost'] = car_data_user_choice_car['tax'] * years
        car_data_user_choice_car['total_cost_of_ownership'] = car_data_user_choice_car['price'] + car_data_user_choice_car['fuel_cost'] + car_data_user_choice_car['maintenance_cost'] + car_data_user_choice_car['tax_cost']
        car_data_given_choice_year['fuel_cost'] = car_data_given_choice_year.apply(calculate_fuel_cost_per_mile, miles=miles, axis=1)
        car_data_given_choice_year['maintenance_cost'] = car_data_given_choice_year['maintenancecostyearly'] * years
        car_data_given_choice_year['tax_cost'] = car_data_given_choice_year['tax'] * years
        car_data_given_choice_year['total_cost_of_ownership'] = car_data_given_choice_year['price'] + car_data_given_choice_year['fuel_cost'] + car_data_given_choice_year['maintenance_cost'] + car_data_given_choice_year['tax_cost']

        total_ownership_cost_for_user_choice_car = car_data_user_choice_car['total_cost_of_ownership'].mean()
        print("\nPredicted Total Cost of Ownership for the Specified Car:")
        print(f"Make: {make}")
        print(f"Expected Annual Mileage: {miles} miles")
        print(f"Years of Ownership: {years} years")
        print(f"Total cost user will pay: £{total_ownership_cost_for_user_choice_car:.0f}")
    else:
        print(f"No matching cars found for make '{make}' and fuel type '{fueltype}'.")

    # Calculate the total ownership cost range based on the user's choice car
    close_cost_other_cars_min = total_ownership_cost_for_user_choice_car * 0.8
    close_cost_other_cars_max = total_ownership_cost_for_user_choice_car * 1  # Adjust range as needed

    # Filter the cars from the other data frame that fall within the calculated range
    close_cost_other_cars = car_data_given_choice_year[
        (car_data_given_choice_year['total_cost_of_ownership'] >= close_cost_other_cars_min) &
        (car_data_given_choice_year['total_cost_of_ownership'] <= close_cost_other_cars_max)
    ]

    # Ensure at least one car from each brand is included
    recommended_cars = pd.concat([car_data_given_choice_year, close_cost_other_cars])
    recommended_cars = recommended_cars.groupby('make').head(1)  # Get one car per brand
    print("Recommended Cost-Effective Cars within the Total Cost of Ownership Range (One Car per Brand):")
    recommended_cars['total_cost_of_ownership'] = recommended_cars['total_cost_of_ownership'].astype(int)  # Convert to integer
    print(recommended_cars[['make', 'model', 'total_cost_of_ownership']])

    # Calculate the total cost of ownership for the specified car
    specified_car_total_cost = car_data_user_choice_car['total_cost_of_ownership'].mean()

    # Find cars from the user choice dataframe that have a total ownership cost close to the specified car's total ownership cost
    close_cost_specified_car = car_data_user_choice_car[
        abs(car_data_user_choice_car['total_cost_of_ownership'] - specified_car_total_cost).lt(specified_car_total_cost * 0.1)
    ]

    # Ensure only 5 closest cars are shown
    close_cost_specified_car = close_cost_specified_car.nsmallest(5, 'total_cost_of_ownership')

    # Display the cars close to the specified car's total ownership cost
    print("Cars with Total Ownership Cost close to the Specified Car:")
    close_cost_specified_car['total_cost_of_ownership'] = close_cost_specified_car['total_cost_of_ownership'].astype(int)
    print(close_cost_specified_car[['make', 'model', 'total_cost_of_ownership']])

    # Sort the DataFrame by total cost of ownership and select the top 5 rows
    lowest_cost_cars = car_data_user_choice_car.sort_values(by='total_cost_of_ownership').head(5)

    # Print the details of the 5 cars with the lowest total cost of ownership
    print("Details of the 5 Cars with the Lowest Total Cost of Ownership:")
    lowest_cost_cars['total_cost_of_ownership'] = lowest_cost_cars['total_cost_of_ownership'].astype(int)
    print(lowest_cost_cars[['make', 'model', 'total_cost_of_ownership']])

    # Check the unique brands in the recommended cars DataFrame
    unique_brands_recommended_cars = recommended_cars['make'].unique()
    print("Unique Brands in the Recommended Cars:")
    print(unique_brands_recommended_cars)

    car_data_user_choice_car.drop(['fuel_cost'], axis=1, inplace=True)
    car_data_user_choice_car.drop(['maintenance_cost'], axis=1, inplace=True)
    car_data_user_choice_car.drop(['tax_cost'], axis=1, inplace=True) 
    car_data_user_choice_car.drop(['total_cost_of_ownership'], axis=1, inplace=True)
    car_data_given_choice_year.drop(['fuel_cost'], axis=1, inplace=True)
    car_data_given_choice_year.drop(['maintenance_cost'], axis=1, inplace=True)
    car_data_given_choice_year.drop(['tax_cost'], axis=1, inplace=True)
    car_data_given_choice_year.drop(['total_cost_of_ownership'], axis=1, inplace=True)

    return render_template('result.html', make=make, miles=miles, years=years,
                       total_cost=  total_ownership_cost_for_user_choice_car,
                       recommended_cars=recommended_cars,
                       close_cost_specified_car=close_cost_specified_car,
                       lowest_cost_cars=lowest_cost_cars)
if __name__ == '__main__':
    app.run(debug=True) 
