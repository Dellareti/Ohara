import tempfile
from pathlib import Path

import pytest

from app.core.library_state import LibraryState

@pytest.fixture
def temp_directory():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def library_state(temp_directory):
    state = LibraryState()
    state._library_path_file = str(temp_directory / "test_library_path.txt")
    yield state
    state.clear()


@pytest.fixture
def configured_library_state(library_state, temp_directory):
    library_state.current_path = str(temp_directory)
    return library_state


@pytest.fixture
def library_state_with_saved_path(library_state, temp_directory):
    library_state.current_path = str(temp_directory)

    new_state = LibraryState()
    new_state._library_path_file = library_state._library_path_file
    return new_state, str(temp_directory)


class TestLibraryStatePublicMethods:
    def test_initial_state(self):
        library_state = LibraryState()
        assert library_state.current_path is None
        assert not library_state.is_configured()
        assert not library_state.validate_current_path()

    def test_set_current_path__valid(self, library_state, temp_directory):
        test_path = str(temp_directory)
        library_state.current_path = test_path

        assert library_state.current_path == test_path
        assert library_state.is_configured()
        assert library_state.validate_current_path()

    def test_set_current_path__none(self, configured_library_state):
        assert configured_library_state.is_configured()

        configured_library_state.current_path = None

        assert configured_library_state.current_path is None
        assert not configured_library_state.is_configured()
        assert not configured_library_state.validate_current_path()

    def test_load_from_file__existing_valid_path(self, library_state_with_saved_path):
        new_state, expected_path = library_state_with_saved_path
        loaded_path = new_state.load_from_file()

        assert loaded_path == expected_path
        assert new_state.current_path == expected_path
        assert new_state.is_configured()

    def test_load_from_file__nonexistent_path(self, library_state, temp_directory):
        invalid_path = "/path/that/does/not/exist/anywhere"
        path_file = Path(library_state._library_path_file)
        path_file.write_text(invalid_path, encoding='utf-8')

        loaded_path = library_state.load_from_file()

        assert loaded_path is None
        assert library_state.current_path is None
        assert not library_state.is_configured()

    def test_load_from_file__no_file(self, library_state):
        loaded_path = library_state.load_from_file()

        assert loaded_path is None
        assert library_state.current_path is None
        assert not library_state.is_configured()

    def test_clear(self, configured_library_state):
        assert configured_library_state.is_configured()

        configured_library_state.clear()

        assert configured_library_state.current_path is None
        assert not configured_library_state.is_configured()
        assert not configured_library_state.validate_current_path()


class TestLibraryStateValidation:
    def test_validate_current_path__valid(self, configured_library_state):
        assert configured_library_state.validate_current_path()

    def test_validate_current_path__invalid(self, library_state):
        library_state.current_path = "/path/that/does/not/exist"
        assert not library_state.validate_current_path()

    def test_validate_current_path__none(self, library_state):
        assert library_state.current_path is None
        assert not library_state.validate_current_path()

    def test_validate_current_path__empty_string(self, library_state):
        library_state.current_path = ""
        assert not library_state.validate_current_path()

    def test_validate_current_path__whitespace_only(self, library_state):
        library_state.current_path = "   \t\n   "
        assert not library_state.validate_current_path()


class TestLibraryStateEdgeCases:
    def test_multiple_clear_calls(self, configured_library_state):
        assert configured_library_state.is_configured()

        configured_library_state.clear()
        configured_library_state.clear()
        configured_library_state.clear()

        assert not configured_library_state.is_configured()
        assert configured_library_state.current_path is None
        assert not configured_library_state.validate_current_path()

    def test_property_getter_setter_consistency(self, library_state):
        test_values = ["/valid/path", "/another/path", None, "/yet/another"]

        for value in test_values:
            library_state.current_path = value
            assert library_state.current_path == value

    def test_is_configured_state_consistency(self, library_state, temp_directory):
        assert not library_state.is_configured()

        library_state.current_path = str(temp_directory)
        assert library_state.is_configured()

        library_state.current_path = None
        assert not library_state.is_configured()
