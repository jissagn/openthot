import pytest
import pytest_asyncio

from stt.models.interview import InterviewCreate
from tests.conftest import V1_PREFIX

INTERVIEWS_ENDPOINT = V1_PREFIX + "/interviews"


#
# API data fillings
#
@pytest_asyncio.fixture(scope="function")
async def api_interviews(mocker, client, access_token, upload_file_mp3):
    """Creates several Interviews through API"""
    mocker.patch("stt.tasks.tasks.process_audio_task.delay")
    headers = {"Authorization": f"Bearer {access_token}"}
    file = {"audio_file": upload_file_mp3}
    for i in range(3):
        itw = InterviewCreate(name=f"Test api itw #{i}")
        response = await client.post(
            INTERVIEWS_ENDPOINT,
            follow_redirects=True,
            headers=headers,
            params=dict(itw),
            files=file,
        )
        assert response.status_code == 200
    yield
    for i in range(3):
        itw = InterviewCreate(name=f"Test api itw #{i}")
        response = await client.delete(
            INTERVIEWS_ENDPOINT,
            follow_redirects=True,
            headers=headers,
        )


@pytest.mark.asyncio
async def test_list_interviews_unauthorized(client):
    response = await client.get(INTERVIEWS_ENDPOINT, follow_redirects=True)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_interviews_empty(client, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.get(
        INTERVIEWS_ENDPOINT, follow_redirects=True, headers=headers
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_list_interviews_not_empty(client, access_token, api_interviews):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.get(
        INTERVIEWS_ENDPOINT, follow_redirects=True, headers=headers
    )
    assert response.status_code == 200
