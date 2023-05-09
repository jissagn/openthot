import pytest
from fastapi import UploadFile

from stt.config import get_settings
from stt.object_storage import save_audio_file


@pytest.mark.asyncio
async def test_save_audio_file_unique_filename(mocker, upload_file_mp3):
    """Tests that the function generates a unique filename for each uploaded file."""
    # Arrange
    audio_file1 = UploadFile(filename="test_audio.mp3", file=upload_file_mp3)
    audio_file2 = UploadFile(filename="test_audio.mp3", file=upload_file_mp3)
    mocked_settings = get_settings()
    mocked_settings.object_storage_path = "/tmp"
    mocker.patch("stt.config.get_settings", return_value=mocked_settings)
    mocker.patch("aiofiles.open")
    mocker.patch("os.makedirs")

    # Act
    result1 = await save_audio_file(audio_file1)
    result2 = await save_audio_file(audio_file2)

    # Assert
    assert result1 != result2
