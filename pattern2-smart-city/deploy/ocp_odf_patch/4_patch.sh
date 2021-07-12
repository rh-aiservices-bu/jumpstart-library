#!/bin/bash
oc patch dns.operator/default --type=merge --patch '{"spec":{"servers":[{"forwardPlugin":{"upstreams":["'$(oc get -n openshift-storage svc | grep dns | awk '{print $3}')':5353"]},"name":"rook-dns","zones":["data.local"]}]}}'

oc patch OCSInitialization ocsinit -n openshift-storage --type json --patch  '[{ "op": "replace", "path": "/spec/enableCephTools", "value": true }]'

sleep 60

oc exec -n openshift-storage deploy/rook-ceph-tools -- bash -c "radosgw-admin zonegroup get --rgw-zonegroup=ocs-storagecluster-cephobjectstore > /tmp/config.json && sed -i 's/\"hostnames\": \[],/\"hostnames\": \[\"s3\.data\.local\"],/' /tmp/config.json && radosgw-admin zonegroup set --rgw-zonegroup=ocs-storagecluster-cephobjectstore --infile=/tmp/config.json"
