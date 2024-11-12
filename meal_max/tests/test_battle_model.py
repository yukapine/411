import pytest

from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meal

### Need to add tests for battle()

@pytest.fixture()
def battle_model():
    """Fixture to provide a new instance of BattleModel for each test."""
    return BattleModel()

@pytest.fixture
def mock_update_meal_stats(mocker):
    """Mock the update_meal_stats function for testing purposes."""
    return mocker.patch("meal_max.models.kitchen_model.update_meal_stats")

"""Fixtures providing sample meals for the tests."""
@pytest.fixture
def sample_meal1():
    return Meal(1, 'Meal 1', 'French', 15.0, 'LOW')

@pytest.fixture
def sample_meal2():
    return Meal(2, 'Meal 2', 'Italian', 20.0, 'HIGH')

@pytest.fixture
def sample_combatants(sample_combatant1, sample_combatant2):
    return [sample_meal1, sample_meal2]


##################################################
# Add Meal Management Test Cases
##################################################

def test_add_meal_to_combatants(kitchen_model, sample_meal1):
    ######################## CHECK ########################
    """Test adding a meal to the combatants list."""
    kitchen_model.prep_combatant(sample_meal1)
    assert len(kitchen_model.combatants) == 1
    assert kitchen_model.combatants[0].meal == 'Meal 1'

def test_add_meal_to_full_list(kitchen_model, sample_meal1):
    ######################## FIX ########################
    """Test error when adding a meal to a full combatants list."""
    kitchen_model.prep_combatant(sample_meal1)
    kitchen_model.prep_combatant(sample_meal1)
    with pytest.raises(ValueError, match="Combatant list is full, cannot add more combatants."):
        kitchen_model.prep_combatant(sample_meal1)

##################################################
# Remove Meal Management Test Cases
##################################################

def test_clear_meals(kitchen_model):
    ######################## CHECK ########################
    """Test clearing the entire combatant list."""
    kitchen_model.prep_combatant(sample_meal1)
    kitchen_model.clear_meals()
    assert len(kitchen_model.combatants) == 0, "combatant list should be empty after clearing"

##################################################
# Meal Retrieval Test Cases
##################################################

def test_get_meal_by_id(kitchen_model, sample_combatants):
    ######################## CHECK ########################
    """Test successfully retrieving a meal from the combatants list by meal number."""
    kitchen_model.combatants.extend(sample_combatants)

    retrieved_meal = kitchen_model.get_meal_by_id(1)
    assert retrieved_meal.id == 1
    assert retrieved_meal.meal == 'Meal 1'
    assert retrieved_meal.cuisine == 'French'
    assert retrieved_meal.price == 15.0
    assert retrieved_meal.difficulty == 'LOW'

def test_get_combatants(kitchen_model, sample_combatants):
    ######################## CHECK ########################
    """Test successfully retrieving all meals from the combatants list."""
    kitchen_model.combatants.extend(sample_combatants)

    all_meals = kitchen_model.get_combatants()
    assert len(all_meals) == 2
    assert all_meals[0].id == 1
    assert all_meals[1].id == 2

def test_get_battle_score(kitchen_model, sample_meal):
    ######################## CHECK ########################
    """Test getting the battle score of a combatant."""
    kitchen_model.combatants.extend(sample_meal)
    assert kitchen_model.get_battle_score() == 87, "Expected battle score"


##################################################
# Battle Test Cases
##################################################
    
def test_battle(kitchen_model, sample_combatants, mock_update_meal_stats):
    """Test running a battle between two meals."""
    kitchen_model.combatants.extend(sample_combatants)

    # Run the battle
    kitchen_model.battle()

    # Assert that the number of combatants after the battle is exactly 1 (the winner remains)
    assert len(kitchen_model.combatants) == 1, "There should be exactly 1 remaining combatant after the battle."

    # Assert that update_meal_stats was called with the correct meal IDs
    mock_update_meal_stats.assert_any_call(1)  # Meal with ID 1
    mock_update_meal_stats.assert_any_call(2)  # Meal with ID 2

    # Check that the combatants are updated correctly based on the battle
    winner = kitchen_model.combatants[0]
    loser_id = 1 if winner.id == 2 else 2  # The loser is the one whose ID doesn't match the winner

    # Ensure that the loser was properly removed
    assert all(meal.id != loser_id for meal in kitchen_model.combatants), "The losing meal should have been removed from the combatants list."

    # Optionally, verify the result of the battle (if there's a specific result to check)
    assert winner.id in [1, 2], "The remaining combatant should be one of the original combatants."
    assert winner.meal in ['Meal 1', 'Meal 2'], "The winner should be either Meal 1 or Meal 2."



