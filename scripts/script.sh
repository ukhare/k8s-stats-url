export ipaddr=$(nslookup $(kubectl get services -n k8s-stats-url|awk '{print $4}'|grep -v EXTERNAL-IP)|grep Address|grep -v "#"|head -1|sed "s/Address: //g")

rm -rf final.yml temp.yml

( echo "cat <<EOF >final.yml";
  cat ../templates/template-k8s-stats-url-endpoint.yml;
  echo "EOF";
) >temp.yml
. temp.yml

cat final.yml > ../k8s/k8s-stats-url-endpoint.yml

rm -rf final.yml temp.yml

kubectl create -f ../k8s/k8s-stats-url-service.yml -f ../k8s/k8s-stats-url-endpoint.yml -f ../k8s/k8s-stats-url-servicemonitor.yml
