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

def test_add_song_to_playlist(playlist_model, sample_song1):
    """Test adding a song to the playlist."""
    playlist_model.add_song_to_playlist(sample_song1)
    assert len(playlist_model.playlist) == 1
    assert playlist_model.playlist[0].title == 'Song 1'

def test_add_duplicate_song_to_playlist(playlist_model, sample_song1):
    """Test error when adding a duplicate song to the playlist by ID."""
    playlist_model.add_song_to_playlist(sample_song1)
    with pytest.raises(ValueError, match="Song with ID 1 already exists in the playlist"):
        playlist_model.add_song_to_playlist(sample_song1)

##################################################
# Remove Meal Management Test Cases
##################################################

def test_remove_song_from_playlist_by_song_id(playlist_model, sample_playlist):
    """Test removing a song from the playlist by song_id."""
    playlist_model.playlist.extend(sample_playlist)
    assert len(playlist_model.playlist) == 2

    playlist_model.remove_song_by_song_id(1)
    assert len(playlist_model.playlist) == 1, f"Expected 1 song, but got {len(playlist_model.playlist)}"
    assert playlist_model.playlist[0].id == 2, "Expected song with id 2 to remain"

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
    ######################## FIX ########################
    """Test clearing the entire combatant list."""
    kitchen_model.add_song_to_playlist(sample_meal1)
    kitchen_model.clear_meals()
    assert len(kitchen_model.combatants) == 0, "combatant list should be empty after clearing"

def test_clear_playlist_empty_playlist(kitchen_model, caplog):
    ######################## DONE ########################
    """Test clearing the entire combatant list when it's empty."""
    kitchen_model.clear_meals()
    assert len(kitchen_model.combatants) == 0, "Playlist should be empty after clearing"
    assert "Clearing an empty playlist" in caplog.text, "Expected warning message when clearing an empty playlist"

##################################################
# Tracklisting Management Test Cases
##################################################

def test_move_song_to_track_number(playlist_model, sample_playlist):
    """Test moving a song to a specific track number in the playlist."""
    playlist_model.playlist.extend(sample_playlist)

    playlist_model.move_song_to_track_number(2, 1)  # Move Song 2 to the first position
    assert playlist_model.playlist[0].id == 2, "Expected Song 2 to be in the first position"
    assert playlist_model.playlist[1].id == 1, "Expected Song 1 to be in the second position"

def test_swap_songs_in_playlist(playlist_model, sample_playlist):
    """Test swapping the positions of two songs in the playlist."""
    playlist_model.playlist.extend(sample_playlist)

    playlist_model.swap_songs_in_playlist(1, 2)  # Swap positions of Song 1 and Song 2
    assert playlist_model.playlist[0].id == 2, "Expected Song 2 to be in the first position"
    assert playlist_model.playlist[1].id == 1, "Expected Song 1 to be in the second position"

def test_swap_song_with_itself(playlist_model, sample_song1):
    """Test swapping the position of a song with itself raises an error."""
    playlist_model.add_song_to_playlist(sample_song1)

    with pytest.raises(ValueError, match="Cannot swap a song with itself"):
        playlist_model.swap_songs_in_playlist(1, 1)  # Swap positions of Song 1 with itself

def test_move_song_to_end(playlist_model, sample_playlist):
    """Test moving a song to the end of the playlist."""
    playlist_model.playlist.extend(sample_playlist)

    playlist_model.move_song_to_end(1)  # Move Song 1 to the end
    assert playlist_model.playlist[1].id == 1, "Expected Song 1 to be at the end"

def test_move_song_to_beginning(playlist_model, sample_playlist):
    """Test moving a song to the beginning of the playlist."""
    playlist_model.playlist.extend(sample_playlist)

    playlist_model.move_song_to_beginning(2)  # Move Song 2 to the beginning
    assert playlist_model.playlist[0].id == 2, "Expected Song 2 to be at the beginning"

##################################################
# Song Retrieval Test Cases
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

def test_get_song_by_song_id(playlist_model, sample_song1):
    """Test successfully retrieving a song from the playlist by song ID."""
    playlist_model.add_song_to_playlist(sample_song1)

    retrieved_song = playlist_model.get_song_by_song_id(1)

    assert retrieved_song.id == 1
    assert retrieved_song.title == 'Song 1'
    assert retrieved_song.artist == 'Artist 1'
    assert retrieved_song.year == 2022
    assert retrieved_song.duration == 180
    assert retrieved_song.genre == 'Pop'

def test_get_current_song(playlist_model, sample_playlist):
    """Test successfully retrieving the current song from the playlist."""
    playlist_model.playlist.extend(sample_playlist)

    current_song = playlist_model.get_current_song()
    assert current_song.id == 1
    assert current_song.title == 'Song 1'
    assert current_song.artist == 'Artist 1'
    assert current_song.year == 2022
    assert current_song.duration == 180
    assert current_song.genre == 'Pop'

def test_get_playlist_length(playlist_model, sample_playlist):
    """Test getting the length of the playlist."""
    playlist_model.playlist.extend(sample_playlist)
    assert playlist_model.get_playlist_length() == 2, "Expected playlist length to be 2"

def test_get_playlist_duration(playlist_model, sample_playlist):
    """Test getting the total duration of the playlist."""
    playlist_model.playlist.extend(sample_playlist)
    assert playlist_model.get_playlist_duration() == 335, "Expected playlist duration to be 360 seconds"

##################################################
# Utility Function Test Cases
##################################################

def test_check_if_empty_non_empty_playlist(playlist_model, sample_song1):
    """Test check_if_empty does not raise error if playlist is not empty."""
    playlist_model.add_song_to_playlist(sample_song1)
    try:
        playlist_model.check_if_empty()
    except ValueError:
        pytest.fail("check_if_empty raised ValueError unexpectedly on non-empty playlist")

def test_check_if_empty_empty_playlist(playlist_model):
    """Test check_if_empty raises error when playlist is empty."""
    playlist_model.clear_playlist()
    with pytest.raises(ValueError, match="Playlist is empty"):
        playlist_model.check_if_empty()

def test_validate_song_id(playlist_model, sample_song1):
    """Test validate_song_id does not raise error for valid song ID."""
    playlist_model.add_song_to_playlist(sample_song1)
    try:
        playlist_model.validate_song_id(1)
    except ValueError:
        pytest.fail("validate_song_id raised ValueError unexpectedly for valid song ID")

def test_validate_song_id_no_check_in_playlist(playlist_model):
    """Test validate_song_id does not raise error for valid song ID when the id isn't in the playlist."""
    try:
        playlist_model.validate_song_id(1, check_in_playlist=False)
    except ValueError:
        pytest.fail("validate_song_id raised ValueError unexpectedly for valid song ID")

def test_validate_song_id_invalid_id(playlist_model):
    """Test validate_song_id raises error for invalid song ID."""
    with pytest.raises(ValueError, match="Invalid song id: -1"):
        playlist_model.validate_song_id(-1)

    with pytest.raises(ValueError, match="Invalid song id: invalid"):
        playlist_model.validate_song_id("invalid")

def test_validate_track_number(playlist_model, sample_song1):
    """Test validate_track_number does not raise error for valid track number."""
    playlist_model.add_song_to_playlist(sample_song1)
    try:
        playlist_model.validate_track_number(1)
    except ValueError:
        pytest.fail("validate_track_number raised ValueError unexpectedly for valid track number")

def test_validate_track_number_invalid(playlist_model, sample_song1):
    """Test validate_track_number raises error for invalid track number."""
    playlist_model.add_song_to_playlist(sample_song1)

    with pytest.raises(ValueError, match="Invalid track number: 0"):
        playlist_model.validate_track_number(0)

    with pytest.raises(ValueError, match="Invalid track number: 2"):
        playlist_model.validate_track_number(2)

    with pytest.raises(ValueError, match="Invalid track number: invalid"):
        playlist_model.validate_track_number("invalid")

##################################################
# Playback Test Cases
##################################################

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