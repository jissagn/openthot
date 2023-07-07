import pytest
import pytest_asyncio

from openthot.models.interview import (
    APIInputInterviewCreate,
    APIInputInterviewUpdate,
    APIOutputInterview,
    InterviewStatus,
)
from tests.conftest import V1_PREFIX

INTERVIEWS_ENDPOINT = V1_PREFIX + "/interviews"


def bearer_header(token):
    return {"Authorization": f"Bearer {token}"}


#
# API data fillings fixture
#
@pytest_asyncio.fixture(scope="function")
async def api_interviews_uploaded(mocker, client, access_token, upload_file_mp3):
    """Creates several Interviews through API. Don't bother processing them."""
    mocker.patch("openthot.tasks.tasks.process_audio_task.delay")
    file = {"audio_file": upload_file_mp3}
    interviews = []
    for i in range(3):
        itw = APIInputInterviewCreate(name=f"Test api itw #{i}")
        response = await client.post(
            INTERVIEWS_ENDPOINT,
            headers=bearer_header(access_token),
            params=itw.dict(exclude_unset=True),
            files=file,
        )
        assert response.status_code == 200
        interviews.append(APIOutputInterview(**response.json()))
    return interviews


# @pytest.mark.celery(task_always_eager=True)
# @pytest_asyncio.fixture(scope="function")
# async def api_interviews_processed(
#     mocker, client, async_test_session, access_token, upload_file_mp3
# ):
#     """Creates several Interviews through API"""
#     import time
#     mocker.patch("openthot.tasks.tasks.async_session", return_value=async_test_session)

#     async def wait_for_status_transcripted(itw_id):
#         status = InterviewStatus.uploaded
#         time.sleep(2)
#         while status != InterviewStatus.transcripted:
#             response = await client.get(
#                 INTERVIEWS_ENDPOINT + f"/{itw_id}", headers=bearer_header(access_token)
#             )

#             assert response.status_code == 200
#             returned_itw = APIOutputInterview(**response.json())
#             status = returned_itw.status
#             time.sleep(0.1)

#     file = {"audio_file": upload_file_mp3}
#     interviews = []
#     for i in range(3):
#         itw = APIInputInterviewCreate(name=f"Test api itw #{i}")
#         response = await client.post(
#             INTERVIEWS_ENDPOINT,
#             headers=bearer_header(access_token),
#             params=dict(itw),
#             files=file,
#         )
#         assert response.status_code == 200
#         interviews.append(APIOutputInterview(**response.json()))
#     return interviews


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
async def test_list_interviews_not_empty(client, access_token, api_interviews_uploaded):
    response = await client.get(
        INTERVIEWS_ENDPOINT, headers=bearer_header(access_token)
    )
    assert response.status_code == 200
    assert len(response.json()) == len(api_interviews_uploaded)


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
    mocker.patch("openthot.tasks.tasks.process_audio_task.delay")

    file = {"audio_file": upload_file_mp3}
    itw = APIInputInterviewCreate(name="Test api itw")
    response = await client.post(
        INTERVIEWS_ENDPOINT,
        headers=bearer_header(access_token),
        params=itw.dict(exclude_unset=True),
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
async def test_delete_interview_valid(client, access_token, api_interviews_uploaded):
    for api_itw in api_interviews_uploaded:
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
async def test_get_interview_uploaded(client, access_token, api_interviews_uploaded):
    for itw in api_interviews_uploaded:
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
async def test_update_interview_valid(client, access_token, api_interviews_uploaded):
    for itw in api_interviews_uploaded:
        upd_itw = APIInputInterviewUpdate(name="upd_ " + itw.name)
        response = await client.patch(
            INTERVIEWS_ENDPOINT + f"/{itw.id}",
            headers=bearer_header(access_token),
            json=upd_itw.dict(exclude_unset=True),
        )
        assert response.status_code == 200
        returned_itw = APIOutputInterview(**response.json())
        assert returned_itw.name == upd_itw.name
        assert returned_itw.update_ts > itw.update_ts


@pytest.mark.asyncio
@pytest.mark.endpoint
async def test_update_interview_speakers_valid(
    client, access_token, api_interviews_uploaded
):
    itw = api_interviews_uploaded[0]

    # First init
    update_1 = {"pouetk": "pouetv"}
    upd_itw = APIInputInterviewUpdate(speakers=update_1)
    response_2 = await client.patch(
        INTERVIEWS_ENDPOINT + f"/{itw.id}",
        headers=bearer_header(access_token),
        json=upd_itw.dict(exclude_unset=True),
    )
    assert response_2.status_code == 200
    returned_itw_2 = APIOutputInterview(**response_2.json())
    assert returned_itw_2.speakers == update_1

    # Set new
    update_2 = {"another_key": "lkj"}
    upd_itw_2 = APIInputInterviewUpdate(speakers=update_2)
    response_2 = await client.patch(
        INTERVIEWS_ENDPOINT + f"/{itw.id}",
        headers=bearer_header(access_token),
        json=upd_itw_2.dict(exclude_unset=True),
    )
    assert response_2.status_code == 200
    returned_itw_2 = APIOutputInterview(**response_2.json())
    assert returned_itw_2.speakers == update_1 | update_2

    # Override
    update_3 = {k: "another_value" for k, v in update_1.items()}
    upd_itw_3 = APIInputInterviewUpdate(speakers=update_3)
    response_3 = await client.patch(
        INTERVIEWS_ENDPOINT + f"/{itw.id}",
        headers=bearer_header(access_token),
        json=upd_itw_3.dict(exclude_unset=True),
    )
    assert response_3.status_code == 200
    returned_itw_3 = APIOutputInterview(**response_3.json())
    assert returned_itw_3.speakers == update_1 | update_2 | update_3

    # Null back
    upd_itw_4 = APIInputInterviewUpdate(speakers=None)
    response_4 = await client.patch(
        INTERVIEWS_ENDPOINT + f"/{itw.id}",
        headers=bearer_header(access_token),
        json=upd_itw_4.dict(exclude_unset=True),
    )
    assert response_4.status_code == 200
    returned_itw_4 = APIOutputInterview(**response_4.json())
    assert returned_itw_4.speakers is None
