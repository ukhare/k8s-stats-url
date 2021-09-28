#set variables
urls="https://httpstat.us/200","https://httpstat.us/503"
timeoutInSec=2
port=8080

class TestApp:
  def test_ProcessURL_request_loop(self, create_processurl):
      urlStatus = float(create_processurl[2].split(' ')[1])
      urlResp = float(create_processurl[5].split(' ')[1])

      assert create_processurl[2].split(' ')[0] == \
            'test_k8s_stats_url_up{url="https://httpstat.us/503"}'
      assert urlStatus == 0.0

      assert create_processurl[5].split(' ')[0] == \
            'test_k8s_stats_url_response_ms{url="https://httpstat.us/503"}'
      assert type(urlResp) is float
      assert urlResp > 0.0
