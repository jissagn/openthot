import pytest
import schemathesis
from hypothesis import HealthCheck, settings

from openthot.api.main import app

schema = schemathesis.from_asgi("/openapi.json", app)

schemathesis.fixups.install()


@pytest.mark.asyncio
@pytest.mark.endpoint
@pytest.mark.slow
@schema.parametrize(endpoint="^/api/v1/interviews/((?!audio).)*$")
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
async def test_api(case, access_token):
    print(access_token)
    response = case.call_asgi(headers={"Authorization": f"Bearer {access_token}"})
    case.validate_response(response)
