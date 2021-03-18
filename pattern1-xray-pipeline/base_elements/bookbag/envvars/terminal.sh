#!/bin/sh

# Environment variables to set for the terminal

# Set NAMESPACE if not set
if [ -z "$NAMESPACE" ]; then
    NAMESPACE=$(cat /run/secrets/kubernetes.io/serviceaccount/namespace)
fi
oc project "${NAMESPACE}" || :
