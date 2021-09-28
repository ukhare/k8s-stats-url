import concurrent.futures, os, requests
from prometheus_client import Gauge, make_wsgi_app
from wsgiref.simple_server import make_server

#set variables
urls="https://httpstat.us/200","https://httpstat.us/503"
timeoutInSec=2
port=8080

urlStatus = Gauge('k8s_stats_url_up','Internet Urls status', ['url'])
urlResp = Gauge('k8s_stats_url_response_ms','Internet Urls response in milliseconds', ['url'])
class AccessWebURL:
    def __init__(self,urls,timeoutInSec,urlStatus,urlResp):
        self.urls = urls
        self.timeoutInSec = timeoutInSec
        self.urlStatus = urlStatus
        self.urlResp = urlResp

    #Ref:https://realpython.com/python-requests/#timeouts
    #function to use request module to hit the internet urls
    def __send_request(self,url):
        try:
            r = requests.get(url, timeout=self.timeoutInSec)
            respTime = round(r.elapsed.total_seconds()*1000,2)
            return [respTime, r.status_code, url]
        except Exception as err:
            raise Exception(err)

    #Ref:https://realpython.com/python-concurrency/#threading-version
    #function to use a pool of threads to execute calls asynchronously
    def send_concurrent_req(self):
        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                results = [executor.submit(self.__send_request, url) for url in self.urls]

                for f in concurrent.futures.as_completed(results):
                    self.urlResp.labels(f.result()[2]).set(f.result()[0])
                    if f.result()[1] == 200:
                        self.urlStatus.labels(f.result()[2]).set(1)
                    else:
                        self.urlStatus.labels(f.result()[2]).set(0)
        except Exception as err:
            raise Exception(err)
#Ref: https://www.programcreek.com/python/example/126996/prometheus_client.make_wsgi_app
#Generate Output in prometheus compatible format
def my_app(environ, start_fn):
    try:
        if environ['PATH_INFO'] == '/metrics':
            global hitUrlObj
            hitUrlObj.send_concurrent_req()
            metrics_app = make_wsgi_app()
            return metrics_app(environ, start_fn)

        start_fn('200 OK', [])
        return [b'Please hit http://localhost:8080/metrics to access the prometheus metrics\n']
    except Exception as err:
        raise Exception(err)

if __name__ == '__main__':
    try:
        hitUrlObj = AccessWebURL(urls,timeoutInSec,urlStatus,urlResp)

        httpd = make_server('0.0.0.0', port, my_app)
        print("Serving localhost on port {}".format(port))
        httpd.serve_forever()
    except KeyboardInterrupt as err:
        print("Shuting Down App. Good Bye!")
        exit(0)
    except Exception as err:
        print("Error ocurred: ", err)
        exit(1)
