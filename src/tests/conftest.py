import pytest
from prometheus_client import Gauge, CollectorRegistry, generate_latest
from app import AccessWebURL

registry =  CollectorRegistry()

#set variables
urls="https://httpstat.us/200","https://httpstat.us/503"
timeoutInSec=2
port=8080

urlStatus = Gauge('test_k8s_stats_url_up', 'Internet Urls status', ['url'])
urlResp = Gauge('test_k8s_stats_url_response_ms','Internet Urls response in milliseconds', ['url'])


@pytest.fixture
def create_processurl():
    hitUrlObj = AccessWebURL(['https://httpstat.us/503'],timeoutInSec,urlStatus,urlResp)
    hitUrlObj.send_concurrent_req()
    result = generate_latest(registry).decode('utf8').split('\n')
    return result
