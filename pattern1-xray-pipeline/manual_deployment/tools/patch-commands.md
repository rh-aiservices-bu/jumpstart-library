# CLI commands used in the demo

Before running those, make sure you are connected to the right project!

```bash
oc project xraylab
```

## Patch image-generator with seconds_wait

Change "value" for the number of seconds to waitr between each image upload. It can be less than a second (e.g. "0.1"). Value "0" stops the image-generator.

```bash
oc patch dc image-generator --type=json -p '[{"op":"replace","path":"/spec/template/spec/containers/0/env/0/value","value":"1"}]'
```

## Patch risk-assessment with revision

Change "value" with the name of the model revision you wan to simulate. It only updates the service annotation, but if a new image has been previously pushed it will use this new one. So that's a way to "force-refresh" your risk-assessment service.

```bash
oc patch service.serving.knative.dev/risk-assessment --type=json -p '[{"op":"replace","path":"/spec/template/metadata/annotations/revisionTimestamp","value":"'"$(date +%F_%T)"'"},{"op":"replace","path":"/spec/template/spec/containers/0/env/0/value","value":"v1"}]'
```
