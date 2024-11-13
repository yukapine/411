#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5000/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done

###############################################
#
# Health Checks
#
###############################################

# Function to check the health of the service
check_health() {
  echo "Checking health status..."
  response=$(curl -s -X GET "$BASE_URL/health")
  echo "Health Check Response: $response"  # Add this line
  if echo "$response" | grep -q '"status": "healthy"'; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}


# Function to check the database connection
check_db() {
  echo "Checking database connection..."
  response=$(curl -s -X GET "$BASE_URL/db-check")
  echo "Database Check Response: $response"  # Add this line
  if echo "$response" | grep -q '"database_status": "healthy"'; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}

##########################################################
#
# Meal Management
#
##########################################################

clear_catalog() {
  echo "Clearing the meals..."
  curl -s -X DELETE "$BASE_URL/clear-meals" | grep -q '"status": "success"'
}

create_meal() {
  name=$1
  cuisine=$2
  price=$3
  difficulty=$4

  # Debugging: Output received parameters
  echo "Received parameters: meal=$name, cuisine=$cuisine, price=$price, difficulty=$difficulty"

  # Construct the JSON payload with proper values
  json_payload="{\"meal\":\"$name\", \"cuisine\":\"$cuisine\", \"price\":$price, \"difficulty\":\"$difficulty\"}"

  # Log the payload to verify it's correct
  echo "Sending JSON payload: $json_payload"

  # Send the request
  response=$(curl -s -X POST "$BASE_URL/create-meal" -H "Content-Type: application/json" -d "$json_payload")

  # Check the response
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal created successfully: $name"
  else
    echo "Failed to create meal. Response: $response"
    exit 1
  fi
}

delete_meal_by_id() {
  meal_id=$1

  echo "Deleting meal by ID ($meal_id)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-meal/$meal_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal deleted successfully by ID ($meal_id)."
  else
    echo "Failed to delete meal by ID ($meal_id)."
    exit 1
  fi
}

get_meal_by_id() {
  meal_id=$1

  echo "Retrieving meal by ID ($meal_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-id/$meal_id")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully by ID ($meal_id)."
    if [ "$ECHO_JSON" = true ]; then
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve meal by ID."
    exit 1
  fi
}

get_meal_by_name() {
  meal_name=$1

  echo "Retrieving meal by name '$meal_name'..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-name/$meal_name")

  # Check if the response status is success
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully by name '$meal_name'."
  
    echo "$response" | jq .  

  else
    echo "Failed to retrieve meal by name '$meal_name'."
    exit 1
  fi
}

############################################################
#
# Battle Management
#
############################################################

prep_combatant () {
  meal_id=$1
  echo "Preparing combatant with Meal ID ($meal_id)..." 
  response=$(curl -s -x POST "$BASE_URL/prep-combatant/$meal_id") 
  if echo "response" | grep -q '"status": "success"'; then 
    echo "Combatant prepared successfully." 
  else
    exit 1
    echo "Failed to prepare combatant."
  fi
}

battle() {
  prep_combatant "meal1"
  prep_combatant "meal2"

  echo "Starting battle..."
  response=$(curl -s -X POST "$BASE_URL/battle") 
  if echo "response" | grep -q '"status": "success"'; then 
    echo "Battle completed successfully."
    if I "$ECHO_JSON" = true 1; then
      echo "Battle Result JSON:"
      echo "$response" | ja .
    fi 
  else
    echo "Failed to start battle."
    exit 1
  fi
}

##########################################################
#
# Leaderboard
#
##########################################################

get_leaderboard() {
  echo "Retrieving leaderboard..."
  response=$(curl -s -X GET "$BASE_URL/leaderboard")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Leaderboard retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve leaderboard."
    exit 1
  fi
}

##########################################################
#
# Smoke Test Execution
#
##########################################################

# Health and DB checks
check_health
check_db

#
clear_catalog

# Create meals
create_meal "Turkey" "Pasta" 12.99 "HIGH"
create_meal "Chicken Wings" "Appetizer" 13.48 "LOW"
create_meal "Caesar Salad" "Salad" 9.99 "HIGH"
create_meal "Tacos" "Main Course" 10.28 "MED"

# Get meals by id
get_meal_by_id 1
get_meal_by_id 2
get_meal_by_id 3
get_meal_by_id 4

# Get meals by name
get_meal_by_name "Turkey"
get_meal_by_name "Chicken%20Wings"
get_meal_by_name "Caesar%20Salad"
get_meal_by_name "Tacos"

# Run Battle

battle

# Get leaderboard
get_leaderboard

# Delete meals
delete_meal_by_id 1
delete_meal_by_id 2

echo "All smoketests completed successfully!"
