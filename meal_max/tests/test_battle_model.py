import pytest

from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meal


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
    ######################## DONE ########################
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


def test_delete_meal_by_meal_number(kitchen_model, sample_combatants):
    ######################## CHECK ########################
    """Test removing a meal from the combatants list by meal number."""
    kitchen_model.combatants.extend(sample_combatants)
    assert len(kitchen_model.combatants) == 2

    # Remove meal at meal id 1 (first meal)
    kitchen_model.delete_meal(1)
    assert len(kitchen_model.combatants) == 1, f"Expected 1 meal, but got {len(kitchen_model.playlist)}"
    assert kitchen_model.combatants[0].id == 2, "Expected meal with id 2 to remain"

def test_clear_meals(kitchen_model):
    ######################## CHECK ########################
    """Test clearing the entire combatant list."""
    kitchen_model.prep_combatant(sample_meal1)
    kitchen_model.clear_meals()
    assert len(kitchen_model.combatants) == 0, "combatant list should be empty after clearing"

def test_clear_playlist_empty_playlist(kitchen_model, caplog):
    ######################## DONE ########################
    """Test clearing the entire combatant list when it's empty."""
    kitchen_model.clear_meals()
    assert len(kitchen_model.combatants) == 0, "Playlist should be empty after clearing"
    assert "Clearing an empty playlist" in caplog.text, "Expected warning message when clearing an empty playlist"


##################################################
# Meal Retrieval Test Cases
##################################################

def test_get_meal_by_id(kitchen_model, sample_combatants):
    ######################## DONE ########################
    """Test successfully retrieving a meal from the combatants list by meal number."""
    kitchen_model.combatants.extend(sample_combatants)

    retrieved_meal = kitchen_model.get_meal_by_id(1)
    assert retrieved_meal.id == 1
    assert retrieved_meal.meal == 'Meal 1'
    assert retrieved_meal.cuisine == 'French'
    assert retrieved_meal.price == 15.0
    assert retrieved_meal.difficulty == 'LOW'

def test_get_combatants(kitchen_model, sample_combatants):
    ######################## DONE ########################
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
# Playback Test Cases
##################################################
    

def test_battle(kitchen_model, sample_combatants):
    kitchen_model.combatants.extend(sample_combatants)
    kitchen_model.battle()
    

def test_play_current_song(playlist_model, sample_playlist, mock_update_play_count):
    """Test playing the current song."""
    playlist_model.playlist.extend(sample_playlist)

    playlist_model.play_current_song()

    # Assert that CURRENT_TRACK_NUMBER has been updated to 2
    assert playlist_model.current_track_number == 2, f"Expected track number to be 2, but got {playlist_model.current_track_number}"

    # Assert that update_play_count was called with the id of the first song
    mock_update_play_count.assert_called_once_with(1)

    # Get the second song from the iterator (which will increment CURRENT_TRACK_NUMBER back to 1)
    playlist_model.play_current_song()

    # Assert that CURRENT_TRACK_NUMBER has been updated back to 1
    assert playlist_model.current_track_number == 1, f"Expected track number to be 1, but got {playlist_model.current_track_number}"

    # Assert that update_play_count was called with the id of the second song
    mock_update_play_count.assert_called_with(2)

def test_rewind_playlist(playlist_model, sample_playlist):
    """Test rewinding the iterator to the beginning of the playlist."""
    playlist_model.playlist.extend(sample_playlist)
    playlist_model.current_track_number = 2

    playlist_model.rewind_playlist()
    assert playlist_model.current_track_number == 1, "Expected to rewind to the first track"

def test_go_to_track_number(playlist_model, sample_playlist):
    """Test moving the iterator to a specific track number in the playlist."""
    playlist_model.playlist.extend(sample_playlist)

    playlist_model.go_to_track_number(2)
    assert playlist_model.current_track_number == 2, "Expected to be at track 2 after moving song"

def test_play_entire_playlist(playlist_model, sample_playlist, mock_update_play_count):
    """Test playing the entire playlist."""
    playlist_model.playlist.extend(sample_playlist)

    playlist_model.play_entire_playlist()

    # Check that all play counts were updated
    mock_update_play_count.assert_any_call(1)
    mock_update_play_count.assert_any_call(2)
    assert mock_update_play_count.call_count == len(playlist_model.playlist)

    # Check that the current track number was updated back to the first song
    assert playlist_model.current_track_number == 1, "Expected to loop back to the beginning of the playlist"

def test_play_rest_of_playlist(playlist_model, sample_playlist, mock_update_play_count):
    """Test playing from the current position to the end of the playlist."""
    playlist_model.playlist.extend(sample_playlist)
    playlist_model.current_track_number = 2

    playlist_model.play_rest_of_playlist()

    # Check that play counts were updated for the remaining songs
    mock_update_play_count.assert_any_call(2)
    assert mock_update_play_count.call_count == 1

    assert playlist_model.current_track_number == 1, "Expected to loop back to the beginning of the playlist"