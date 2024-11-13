from contextlib import contextmanager
import re
import sqlite3

import pytest

from meal_max.models.kitchen_model import (
    Meal,
    create_meal,
    clear_meals,
    delete_meal,
    get_meal_by_name,
    get_meal_by_id,
    get_leaderboard,
    update_meal_stats,
)

######################################################
#
#    Fixtures
#
######################################################

### Still need to test update_meal_stats, get_leaderboard, get_meal_by_name

@pytest.fixture
def kitchen_model():
    # Setup for kitchen_model (e.g., create an instance of the model)
    model = kitchen_model()
    yield model
    # Teardown if needed (e.g., closing database connections or cleanup)
    model.cleanup()

def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()

# Mocking the database connection for tests
@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Mock the connection's cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Default return for queries
    mock_cursor.fetchall.return_value = []
    mock_conn.commit.return_value = None

    # Mock the get_db_connection context manager from sql_utils 
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn  # Yield the mocked connection object

    mocker.patch("meal_max.models.kitchen_model.get_db_connection", mock_get_db_connection)

    return mock_cursor  # Return the mock cursor so we can set expectations per test

######################################################
#
#    Add and delete
#
######################################################

def test_create_meal(mock_cursor):
    """Test creating a new meal in the database."""

    # Call the function to add a new meal
    create_meal(meal="eggs", cuisine='diner', price=10.0, difficulty='HIGH')

    expected_query = normalize_whitespace("""
        INSERT INTO meals (meal, cuisine, price, difficulty)
        VALUES (?, ?, ?, ?)
    """)

    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = ("eggs", 'diner', 10.0, 'HIGH')
    assert actual_arguments == expected_arguments, f"Expected {expected_arguments}, got {actual_arguments}."

def test_create_meal_duplicate(mock_cursor):
    """Test creating a meal with a duplicate name (should raise an error)."""

     # Simulate that the database will raise an IntegrityError due to a duplicate entry
    mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: meals.meal, meals.cuisine, meals.price, meals.difficulty")

    # Expect the function to raise a ValueError with a specific message when handling the IntegrityError
    with pytest.raises(ValueError, match="Meal with name 'eggs' already exists"):
        create_meal(meal="eggs", cuisine='diner', price=10.0, difficulty='HIGH')

def test_create_meal_negative_price():
    """Test error when trying to create a meal with an invalid price."""

    # Attempt to add a meal with a negative price
    with pytest.raises(ValueError, match="Invalid price: -10.0. Price must be a positive number."):
        create_meal(meal="Pasta", cuisine="Italian", price=-10.0, difficulty="LOW")


def test_create_meal_invalid_difficulty():
    """Test error when trying to create a meal with an invalid difficulty."""

    # Attempt to add a meal with a invalid difficulty
    with pytest.raises(ValueError, match="Invalid difficulty level: invalid. Must be 'LOW', 'MED', or 'HIGH'."):
        create_meal(meal="Pasta", cuisine="Italian", price=10.0, difficulty="invalid")

def test_delete_meal(mock_cursor):
    """Test soft deleting a meal from the database by meal ID."""

    # Simulate that the meal exists (id = 1)
    mock_cursor.fetchone.return_value = ([False])

    # Call the delete_meal function
    delete_meal(1)

    expected_select_sql = normalize_whitespace("SELECT deleted FROM meals WHERE id = ?")
    expected_update_sql = normalize_whitespace("UPDATE meals SET deleted = TRUE WHERE id = ?")

    actual_select_sql = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    actual_update_sql = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    assert actual_select_sql == expected_select_sql, "The SELECT query did not match the expected structure."
    assert actual_update_sql == expected_update_sql, "The UPDATE query did not match the expected structure."

    # Ensure the correct arguments were used in both SQL queries
    expected_args = (1,)
    actual_select_args = mock_cursor.execute.call_args_list[0][0][1]
    actual_update_args = mock_cursor.execute.call_args_list[1][0][1]

    assert actual_select_args == expected_args
    assert actual_update_args == expected_args

def test_delete_meal_bad_id(mock_cursor):
    """Test error when trying to delete a non-existent meal."""

    # Simulate that no meal exists with the given ID
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when attempting to delete a non-existent meal
    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        delete_meal(999)

def test_delete_meal_already_deleted(mock_cursor):
    """Test error when trying to delete a meal that's already marked as deleted."""

    # Simulate that the meal exists but is already marked as deleted
    mock_cursor.fetchone.return_value = ([True])

    # Expect a ValueError when attempting to delete a meal that's already been deleted
    with pytest.raises(ValueError, match="Meal with ID 999 has been deleted"):
        delete_meal(999)

######################################################
#
#    Get Meal
#
######################################################

def test_get_meal_by_id(mock_cursor):
    """Test retrieving a meal by ID."""

    # Simulate that the meal exists (id = 1)
    mock_cursor.fetchone.return_value = (1, "Pasta", "Italian", 10.0, 'LOW', False)

    # Call the function and check the result
    result = get_meal_by_id(1)

    # Expected result based on the simulated fetchone return value
    expected_result = Meal(1, "Pasta", "Italian", 10.0, 'LOW')

    assert result == expected_result

    expected_query = normalize_whitespace("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."
    assert mock_cursor.execute.call_args[0][1] == (1,)

def test_get_meal_by_id_bad_id(mock_cursor):
    """Test error when trying to delete a non-existent song."""
    # Simulate that no meal exists for the given ID
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when the meal is not found
    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        get_meal_by_id(999)

def test_get_meal_by_name(mock_cursor):
    """Test getting a meal by its name."""
    # Simulate that the song exists (meal = "Pasta", cuisine = "Italian", price = 15.0, difficulty = "HIGH")
    mock_cursor.fetchone.return_value = (1, "Pasta", "Italian", 15.0, "HIGH", False)

    # Call the function and check the result
    result = get_meal_by_name("Pasta")

    # Expected result based on the simulated fetchone return value
    expected_result = Meal(1, "Pasta", "Italian", 15.0, "HIGH")

    # Ensure the result matches the expected output
    assert result == expected_result, f"Expected {expected_result}, got {result}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE meal = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = ('Pasta',)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_get_leaderboard(mock_cursor):
    """Test that the leaderboard correctly sorts meals by battle score."""
    #kitchen_model.combatants.extend(sample_combatants)

    mock_cursor.fetchall.return_value = [
        (1, "Pasta", "Italian", 12.5, "LOW", 10, 8, 0.8),  
        (2, "Sushi", "Japanese", 15.0, "HIGH", 20, 15, 0.75),
    ]
    # Call function
    result = get_leaderboard(sort_by="wins")

    # Expected output
    expected = [
        {
            'id': 1,
            'meal': "Pasta",
            'cuisine': "Italian",
            'price': 12.5,
            'difficulty': "LOW",
            'battles': 10,
            'wins': 8,
            'win_pct': 80.0
        },
        {
            'id': 2,
            'meal': "Sushi",
            'cuisine': "Japanese",
            'price': 15.0,
            'difficulty': "HIGH",
            'battles': 20,
            'wins': 15,
            'win_pct': 75.0
        }
    ]
    print("Expected:", expected)
    print("Actual:", result)
    assert result == expected


######################################################
#
#    Clear Database
#
######################################################

def test_clear_meals(mock_cursor, mocker):
    """Test clearing the entire meal database."""

    # Mock the SQL file reading
    mocker.patch.dict('os.environ', {'SQL_CREATE_TABLE_PATH': 'sql/create_meal_table.sql'})
    mock_open = mocker.patch('builtins.open', mocker.mock_open(read_data="CREATE TABLE meals..."))

    # Call the clear_meals function
    clear_meals()

    # Ensure the file was opened using the environment variable's path
    mock_open.assert_called_once_with('sql/create_meal_table.sql', 'r')

    # Verify that the correct SQL script was executed
    mock_cursor.executescript.assert_called_once()

def test_update_meal_stats(mock_cursor):
    """Test updating the meal stats of a meal."""
     # Simulate that the song exists and is not deleted (id = 1)
    mock_cursor.fetchone.return_value = [False]

    # Call the update_play_count function with a sample song ID
    meal_id = 1
    result = 'win'
    update_meal_stats(meal_id, result)

    # Normalize the expected SQL query
    expected_query = normalize_whitespace("""
        UPDATE meals SET battles = battles + 1, wins = wins + 1 WHERE id = ?
    """)

    # Ensure the SQL query was executed correctly
    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args_list[1][0][1]

    # Assert that the SQL query was executed with the correct arguments (meal ID)
    expected_arguments = (meal_id,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."