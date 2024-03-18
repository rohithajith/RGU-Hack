#lock&load
library(dplyr)
library(tidyr)
library(randomForest)

cleandataset_mfd = read.csv('/Users/rohith/Downloads/used-car-dataset-challenge/myfuckinglastdata.csv', header = T, stringsAsFactors = T)
cleandataset = read.csv('/Users/rohith/Downloads/used-car-dataset-challenge/cleaned_dataset.csv', header = T, stringsAsFactors = T)
maintainance_cost = read.csv('/Users/rohith/Downloads/used-car-dataset-challenge/maintain_cost.csv', header = T, stringsAsFactors = T)
summary(maintainance_cost)
maintainance_cost_duplicate = maintainance_cost
maintainance_cost_super = maintainance_cost
cleandataset_duplicate= cleandataset_mfd


# Assuming the column with years is named 'Year' in your data frame df
View(cleandataset_mfd)

# Constants
num_years = 5
annual_mileage = 8000
fuel_cost_petrol = 1.4251 #per mile 
fuel_cost_diesel = 1.5090 #per mile

# Feature engineering
# Constants
num_years <- 5
annual_mileage <- 8000
fuel_cost_petrol <- 1.4251 # per mile
fuel_cost_diesel <- 1.5090 # per mile


# Feature engineering
# Create Fuel_Cost_5_years column
cleandataset$Fuel_Cost_5_years <- ifelse(cleandataset$fuelType == "petrol", 
                                         fuel_cost_petrol * cleandataset$mpg * annual_mileage * 5,
                                          fuel_cost_diesel * cleandataset$mpg * annual_mileage * 5)

# Create Taxes_Cost_5_years column  
cleandataset$Taxes_Cost_5_years <- cleandataset$tax * 5
# Create Total_Cost_5_years column
cleandataset$Total_Cost_5_years <- cleandataset$price + cleandataset$Fuel_Cost_5_years + cleandataset$Taxes_Cost_5_years
# Calculate five year fuel cost
cleandataset$five_year_fuel_cost = cleandataset$annual_fuel_cost * 5


# Example: Select features and convert "model" to factor
features <- c("mileage", "mpg", "tax", "Taxes_Cost_5_years", "Fuel_Cost_5_years")
car_data <- cleandataset_mfd[, features]
car_data$model <- factor(car_data$model)
# Define target variable (e.g., total cost)
target <- "price"

# Split data into training and testing sets (optional)
set.seed(123)  # For reproducibility
train_index <- sample(1:nrow(data), size = 0.8 * nrow(data))
training_data <- data[train_index, ]
testing_data <- data[-train_index, ]
print(names(training_data))
features <- intersect(features, names(training_data)) 
# Train the Random Forest model
memory.limit(size = 4096)  # Set limit to 4 GB
# Train the Random Forest model
model <- randomForest(formula = paste(target, "~.", paste(features, collapse = "+")), data = training_data, x = training_data[, features])
 # Get feature importance scores (optional)
importance <- importance(model)
print(importance)  # Visualize feature importance

# Make predictions on new data (e.g., testing set)
predictions <- predict(model, newdata = testing_data)


