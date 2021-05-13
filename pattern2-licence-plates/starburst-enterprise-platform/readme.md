- Install helm 3.x client
- oc new-project presto

helm repo add \
  --username redhat \
  --password JBXjLPv6Scch5t8Dk2zLnZhgS \
  starburstdata \
  https://harbor.starburstdata.net/chartrepo/starburstdata

helm repo list

helm search repo

oc create secret generic mylicense --from-file=starburstdata.license

helm upgrade sep-hive starburstdata/starburst-hive \
  --install \
  --version 356.0.0 \
  --values ./hms-config.yaml

helm upgrade sep-cluster starburstdata/starburst-enterprise \
  --install \
  --version 356.0.0 \
  --values ./sep-config.yaml

oc expose svc/coordinator

oc port-forward svc/coordinator 8080:8080
visit http://127.0.0.1:8080