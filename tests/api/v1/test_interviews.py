import pytest
import pytest_asyncio

from stt.models.interview import (
    APIInputInterviewCreate,
    APIOutputInterview,
    InterviewStatus,
    APIInputInterviewUpdate,
)
from tests.conftest import V1_PREFIX

INTERVIEWS_ENDPOINT = V1_PREFIX + "/interviews"


def bearer_header(token):
    return {"Authorization": f"Bearer {token}"}


#
# API data fillings fixture
#
@pytest_asyncio.fixture(scope="function")
async def api_interviews(mocker, client, access_token, upload_file_mp3):
    """Creates several Interviews through API"""
    mocker.patch("stt.tasks.tasks.process_audio_task.delay")
    file = {"audio_file": upload_file_mp3}
    interviews = []
    for i in range(3):
        itw = APIInputInterviewCreate(name=f"Test api itw #{i}")
        response = await client.post(
            INTERVIEWS_ENDPOINT,
            headers=bearer_header(access_token),
            params=dict(itw),
            files=file,
        )
        assert response.status_code == 200
        interviews.append(APIOutputInterview(**response.json()))
    return interviews


#
# List
#
@pytest.mark.asyncio
@pytest.mark.endpoint
async def test_list_interviews_unauthorized(client):
    response = await client.get(INTERVIEWS_ENDPOINT)
    assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.endpoint
async def test_list_interviews_empty(client, access_token):
    response = await client.get(
        INTERVIEWS_ENDPOINT, headers=bearer_header(access_token)
    )
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
@pytest.mark.endpoint
async def test_list_interviews_not_empty(client, access_token, api_interviews):
    response = await client.get(
        INTERVIEWS_ENDPOINT, headers=bearer_header(access_token)
    )
    assert response.status_code == 200
    assert len(response.json()) == len(api_interviews)


#
# Create
#
@pytest.mark.asyncio
@pytest.mark.endpoint
async def test_create_interview_unauthorized(client):
    response = await client.post(
        INTERVIEWS_ENDPOINT,
    )
    assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.endpoint
async def test_create_interview_valid(
    mocker, client, access_token, logged_user, upload_file_mp3
):
    mocker.patch("stt.tasks.tasks.process_audio_task.delay")

    file = {"audio_file": upload_file_mp3}
    itw = APIInputInterviewCreate(name="Test api itw")
    response = await client.post(
        INTERVIEWS_ENDPOINT,
        headers=bearer_header(access_token),
        params=dict(itw),
        files=file,
    )
    assert response.status_code == 200
    returned_itw = APIOutputInterview(**response.json())
    assert returned_itw.id is not None
    assert returned_itw.name == itw.name
    assert returned_itw.status == InterviewStatus.uploaded
    assert str(returned_itw.creator_id) == str(logged_user.id)


#
# Delete
#
@pytest.mark.asyncio
@pytest.mark.endpoint
async def test_delete_interview_unauthorized(client):
    response = await client.delete(
        INTERVIEWS_ENDPOINT + "/99999",
    )
    assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.endpoint
async def test_delete_interview_valid(client, access_token, api_interviews):
    for api_itw in api_interviews:
        response = await client.delete(
            INTERVIEWS_ENDPOINT + f"/{api_itw.id}",
            headers=bearer_header(access_token),
        )
        assert response.status_code == 200


@pytest.mark.asyncio
@pytest.mark.endpoint
async def test_delete_interview_inexistent(client, access_token):
    response = await client.delete(
        INTERVIEWS_ENDPOINT + "/99999",
        headers=bearer_header(access_token),
    )
    assert response.status_code == 404


#
# Get
#
@pytest.mark.asyncio
@pytest.mark.endpoint
async def test_get_interview_unauthorized(client):
    response = await client.get(
        INTERVIEWS_ENDPOINT + "/99999",
    )
    assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.endpoint
async def test_get_interview_valid(client, access_token, api_interviews):
    for itw in api_interviews:
        response = await client.get(
            INTERVIEWS_ENDPOINT + f"/{itw.id}", headers=bearer_header(access_token)
        )
        assert response.status_code == 200
        returned_itw = APIOutputInterview(**response.json())
        assert returned_itw.id == itw.id
        assert returned_itw.name == itw.name
        assert returned_itw.status in InterviewStatus._value2member_map_.keys()


@pytest.mark.asyncio
@pytest.mark.endpoint
async def test_get_interview_inexistent(client, access_token):
    response = await client.get(
        INTERVIEWS_ENDPOINT + "/99999",
        headers=bearer_header(access_token),
    )
    assert response.status_code == 404


#
# Update
#
@pytest.mark.asyncio
@pytest.mark.endpoint
async def test_update_interview_unauthorized(client):
    response = await client.patch(
        INTERVIEWS_ENDPOINT + "/99999",
    )
    assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.endpoint
async def test_update_interview_valid(client, access_token, api_interviews):
    for itw in api_interviews:
        upd_itw = APIInputInterviewUpdate(name="upd_ " + itw.name)
        response = await client.patch(
            INTERVIEWS_ENDPOINT + f"/{itw.id}",
            headers=bearer_header(access_token),
            json=dict(upd_itw),
        )
        assert response.status_code == 200
        returned_itw = APIOutputInterview(**response.json())
        assert returned_itw.name == upd_itw.name
        assert returned_itw.update_ts > itw.update_ts
