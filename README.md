
# Assignment:
# #############

Design a solution in Python to run on a Kubernetes Cluster to monitor internet urls and provide Prometheus metrics,
Requirements:

·         A service written in python or golang that queries 2 urls (https://httpstat.us/503 & https://httpstat.us/200)
·         The service will check the external urls (https://httpstat.us/503 & https://httpstat.us/200 ) are up (based on http status code 200) and response time in milliseconds
·         The service will run a simple http service that produces  metrics (on /metrics) and output a prometheus format when hitting the service /metrics url
·         Expected response format:

		§  sample_external_url_up{url="https://httpstat.us/503 "}  = 0

		§  sample_external_url_response_ms{url="https://httpstat.us/503 "}  = [value]

		§  sample_external_url_up{url="https://httpstat.us/200 "}  = 1

		§  sample_external_url_response_ms{url="https://httpstat.us/200 "}  = [value]

# Solution:
# ##########

# k8s-stats-url
#
task: Monitor external internet url status code and time to response.

1. Setup prometheus-community repo. 

		§  helm repo add prometheus-community https://prometheus-community.github.io/helm-charts

2. Install kube-prometheus-stack from kubernetes community this will setup prometheus and grafana in monitoring name space and expose services as load balancer

		§  helm upgrade --namespace monitoring prom-operator --set prometheus.service.type=LoadBalancer --set grafana.service.type=LoadBalancer --set grafana.adminPassword="<AddePreferredPassword>" --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false -i prometheus-community/kube-prometheus-stack  

3. Clone repo.

		$  git clone https://github.com/ukhare/k8s-stats-url.git

4. Go to dir

		§  cd k8s-stats-url

5. Build image

		§  docker build -t k8s-stats-url .

6. Tag newly build image by adding your docker registry url in below command

		§  docker tag k8s_stats_url:latest <docker registry url>/k8s-stats-url:latest

7. push image to your docker registry by adding your docker registry url in below command

		§  docker push <docker registry url>k8s-stats-url:latest

8. create namespace

		§  kubectl create ns k8s-stats-url

9. Add docker registry in deployment

		§  cd k8s
		
   edit line 29 in file k8s-stats-url.yml and add your docker registry url
   
		§  https://github.com/ukhare/k8s-stats-url/blob/main/k8s/k8s-stats-url.yml#L29

10. Deploy the Application on K8s (We are here exposing app service as load balancer)

		§  cd ..
		§  kubectl apply -f k8s/k8s-stats-url.yml -n k8s-stats-url

#output
	
		§  kubectl get all -n k8s-stats-url
		NAME                                        READY   STATUS    RESTARTS   AGE
		pod/k8s-stats-url-deploy-69f869f4c8-c2sjd   1/1     Running   0          17h
		pod/k8s-stats-url-deploy-69f869f4c8-snf9j   1/1     Running   0          17h
		pod/k8s-stats-url-deploy-69f869f4c8-vclpw   1/1     Running   0          17h

		NAME                            TYPE           CLUSTER-IP       EXTERNAL-IP                                                              PORT(S)        AGE
		service/k8s-stats-url-service   LoadBalancer   10.100.xxx.xxx   <ip or url of load balancer of k8s-stats-url service>   80:30707/TCP   17h

		NAME                                   READY   UP-TO-DATE   AVAILABLE   AGE
		deployment.apps/k8s-stats-url-deploy   3/3     3            3           17h

		NAME                                              DESIRED   CURRENT   READY   AGE
		replicaset.apps/k8s-stats-url-deploy-69f869f4c8   3         3         3       17h

11. execute script.sh this script will get the application load balancer ip and create  service, service monitor and service endpoint under namespace monitoring which will create stats of application

	pre-execution details
	
	1). scripts/scripts.sh parses endpoint template and passes loadbalancer ip iddress, finally generates k8s/k8s-stats-url-endpoint.yml

	2). In final step script.sh applies service, endpoint and service monitor configuration on prometheus so that prometheus starts scrapping our application and generate metrics that we can see on Grafana

		$ cat templates/template-k8s-stats-url-endpoint.yml
		apiVersion: v1
		kind: Endpoints
		metadata:
  		annotations:
		     prometheus.io/scrape: "true"
		  namespace: monitoring
		  name: k8s-stats-url
 		 labels:
    		app: k8s-stats-url
		subsets:
		- addresses:
		  - ip: $ipaddr
		  ports:
		  - name: metrics
 		   port: 80
  		  protocol: TCP

#execute script.sh

		cd scripts
		./script.sh

#check if metrics are generating

		curl <ip or url of load balancer of k8s-stats-url service>/metrics 

Output should look like:

		#####################################################################################
		# HELP python_gc_objects_collected_total Objects collected during gc
		# TYPE python_gc_objects_collected_total counter
		python_gc_objects_collected_total{generation="0"} 9982.0
		python_gc_objects_collected_total{generation="1"} 3479.0
		python_gc_objects_collected_total{generation="2"} 0.0
		# HELP python_gc_objects_uncollectable_total Uncollectable object found during GC
		# TYPE python_gc_objects_uncollectable_total counter
		python_gc_objects_uncollectable_total{generation="0"} 0.0
		python_gc_objects_uncollectable_total{generation="1"} 0.0
		python_gc_objects_uncollectable_total{generation="2"} 0.0
		# HELP python_gc_collections_total Number of times this generation was collected
		# TYPE python_gc_collections_total counter
		python_gc_collections_total{generation="0"} 78.0
		python_gc_collections_total{generation="1"} 7.0
		python_gc_collections_total{generation="2"} 0.0
		# HELP python_info Python platform information
		# TYPE python_info gauge
		python_info{implementation="CPython",major="3",minor="9",patchlevel="7",version="3.9.7"} 1.0
		# HELP process_virtual_memory_bytes Virtual memory size in bytes.
		# TYPE process_virtual_memory_bytes gauge
		process_virtual_memory_bytes 2.9601792e+07
		# HELP process_resident_memory_bytes Resident memory size in bytes.
		# TYPE process_resident_memory_bytes gauge
		process_resident_memory_bytes 2.7332608e+07
		# HELP process_start_time_seconds Start time of the process since unix epoch in seconds.
		# TYPE process_start_time_seconds gauge
		process_start_time_seconds 1.63239755738e+09
		# HELP process_cpu_seconds_total Total user and system CPU time spent in seconds.
		# TYPE process_cpu_seconds_total counter
		process_cpu_seconds_total 94.12
		# HELP process_open_fds Number of open file descriptors.
		# TYPE process_open_fds gauge
		process_open_fds 6.0
		# HELP process_max_fds Maximum number of open file descriptors.
		# TYPE process_max_fds gauge
		process_max_fds 1.048576e+06
		# HELP k8s_stats_url_up Internet Urls status
		# TYPE k8s_stats_url_up gauge
		k8s_stats_url_up{url="https://httpstat.us/200"} 1.0
		k8s_stats_url_up{url="https://httpstat.us/503"} 0.0
		# HELP k8s_stats_url_response_ms Internet Urls response in milliseconds
		# TYPE k8s_stats_url_response_ms gauge
		k8s_stats_url_response_ms{url="https://httpstat.us/200"} 148.05
		k8s_stats_url_response_ms{url="https://httpstat.us/503"} 151.49
		##############################################################################################

#If successful then we can see the target is UP in prometheus url: 

		http://<prometheus-ip or loadblancer url>:9090/targets

		Endpoint				State	Labels	Last Scrape	Scrape Duration	Error
		http://<ip or url of load balancer of k8s-stats-url service>/metrics	UP	
		endpoint="metrics"instance="<ip or url of load balancer of k8s-stats-url service>:80"job="k8s-stats-url"namespace="monitoring"service="k8s-stats-url"
		8.558s ago	163.204ms	

![image](https://user-images.githubusercontent.com/45262478/134632255-49b2a904-b67c-4050-ac65-5dccf664b3a5.png)


#created servicemonitor should be visible in below prometheus url

		http://prometheus-ip or loadblancer url:9090/config
		

-- search for "k8s-stats-url" and you should be able to see below

		- job_name: serviceMonitor/monitoring/k8s-stats-url/0
		  honor_labels: true
		  honor_timestamps: true
		  scrape_interval: 10s
 		 scrape_timeout: 10s
 		 metrics_path: /metrics
 		 scheme: http
  		follow_redirects: true
  		relabel_configs:
		  - source_labels: [job]
 		   separator: ;
 		   regex: (.*)
 		   target_label: __tmp_prometheus_job_name
 		   replacement: $1
 		   action: replace
		  - source_labels: [__meta_kubernetes_service_label_app]
 		   separator: ;
 		   regex: k8s-stats-url
 		   replacement: $1
 		   action: keep
		
<img width="705" alt="Screenshot 2021-09-24 at 12 10 54 PM" src="https://user-images.githubusercontent.com/45262478/134632351-6021a96d-ce79-485a-80ba-2ca2335aad4b.png">

-- prometheus graphs

<img width="1679" alt="Screenshot 2021-09-24 at 12 16 29 PM" src="https://user-images.githubusercontent.com/45262478/134632624-dfcb8f57-10a4-4010-aa24-939a815c038e.png">
<img width="1676" alt="Screenshot 2021-09-24 at 12 16 58 PM" src="https://user-images.githubusercontent.com/45262478/134632645-3a48b3c0-3c10-4435-b421-2b28ea938974.png">


#cat below file and paste on grafana import to see the metrics

		cat grafana/grafana-k8s-stats-url.json

-- after uploading json we can see below graphs:
<img width="1680" alt="Screenshot 2021-09-24 at 12 08 47 PM" src="https://user-images.githubusercontent.com/45262478/134632714-e6274008-3c29-48f4-a73a-3d366bae223c.png">

<img width="1679" alt="Screenshot 2021-09-24 at 12 09 17 PM" src="https://user-images.githubusercontent.com/45262478/134632734-a6d53f1a-9899-40ab-94e2-6e000e6f6187.png">

		
<img width="1672" alt="Screenshot 2021-09-24 at 12 09 34 PM" src="https://user-images.githubusercontent.com/45262478/134632750-6ae7943c-732f-4d80-a5da-aacd59530245.png">

		
