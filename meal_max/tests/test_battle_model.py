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
    ######################## CHECK ########################
    """Test running a battle."""
    kitchen_model.combatants.extend(sample_combatants)

    kitchen_model.battle()

    # Assert that 2 combatants are prepped for a battle.
    assert len(kitchen_model.combatants) >= 2, f"Not enough combatants to start a battle."

    # Assert that update_meal_stats was called with the id of both meals, and their result
    mock_update_meal_stats.assert_called_once_with(1)
    mock_update_meal_stats.assert_called_once_with(2)

    # Assert that the losing combatant was removed from the list.
    assert len(kitchen_model.combatants) == 1


