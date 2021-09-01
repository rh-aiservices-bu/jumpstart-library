SEP Deployment

## Prerequisites

- Starburst Harbor registry credentials
- Starburst Enterprise license file
- OBC for Secor bucket created (preffered secor service deployed)

- ODF
  - RGW Service IP address

```
oc -n openshift-storage get svc rook-ceph-rgw-ocs-storagecluster-cephobjectstore -o json | jq -r  .spec.clusterIP
```

- OBC Credentials

```
oc get secret/secor-obc -o yaml | grep " AWS_ACCESS_KEY_ID" | awk '{ print $2 }' - | base64 -d
oc get secret/secor-obc -o yaml | grep " AWS_SECRET_ACCESS_KEY" | awk '{ print $2 }' - | base64 -d
```

- Set starburst registry

```
helm repo add \
  --username redhat \
  --password xxx\
  starburstdata \
  https://harbor.starburstdata.net/chartrepo/starburstdata

helm repo list
```

- Create starburst license as secret

```
oc create secret generic starburst-license --from-file=starburstdata.license
```

## Deploying Hive Meta Store

- update `hms.yaml` with ODF RGW IP , secor obc Access and secret keys before deploying

- Deploy Hive Metastore Store

```
helm upgrade sep-hive starburstdata/starburst-hive \
  --install \
  --version 356.0.0 \
  --values ./hms.yaml
```

## Deploying Starburst Enterise Presto

- update `sep.yaml` with
  - `hive.s3.endpoint` with ODF RGW IP
  - `hive.s3.aws-access-key`
  - `hive.s3.aws-access-key`

```
helm upgrade sep-cluster starburstdata/starburst-enterprise \
  --install \
  --version 356.0.0 \
  --values ./sep.yaml
```

```
oc expose svc/coordinator
```

## To connect to presto cluster from CLI (optional)

```
oc port-forward svc/coordinator 8080:8080
# Need to download trino CLI locally
 ./trino --server localhost:8080 --catalog hive --schema default
```

### TODO

- work with Starburst to include licene free version of presto in this demo
