import pytest
from src.utils.journal_validator import JournalValidator
from src.models.journal import JournalCreate, JournalUpdate

def test_validator():
    # Test valid journal
    valid_journal = JournalCreate(title="Test Title", content="Test Content")
    assert JournalValidator.validate_create(valid_journal, "test_user") is None

    # Test empty journal
    empty_journal = JournalCreate(title="", content="")
    result = JournalValidator.validate_create(empty_journal, "test_user")
    assert result.success is False
    assert result.error == "EMPTY_FIELDS"

    # Test update validation
    valid_update = JournalUpdate(title="New Title", content="New Content")
    assert JournalValidator.validate_update(valid_update) is None

    # Test long content
    long_content = " ".join(["word"] * 1000)
    long_journal = JournalCreate(title="Test", content=long_content)
    result = JournalValidator.validate_create(long_journal, "test_user")
    assert result.success is False
    assert result.error == "CONTENT_TOO_LONG"