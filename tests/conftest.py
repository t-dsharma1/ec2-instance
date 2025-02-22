import pytest


@pytest.fixture(autouse=True)
def pubsub_publish(mocker):
    publish_mock = mocker.patch("genie_dao.pubsub.publish")
    return publish_mock
