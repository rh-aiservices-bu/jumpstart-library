# Apache Superset

Apache Superset component installs Apache Superset tool which provides a portal for business intelligence. It provides tools for exploring and visualizing datasets and creating business intelligence dashboards. Superset can also connect to SQL databases for data access. For more information please visit [Apache Superset](https://superset.apache.org/)

### Folders
There is one main folder in the Superset component
1. base: contains all the necessary yaml files to install Superset

### Installation
To install Superset add the following to the `kfctl` yaml file.

```yaml
  - kustomizeConfig:
      repoRef:
        name: manifests
        path: superset
    name: superset
```

Superset is configured by default to use OpenShift OAuth for authentication. Any user that has admin access to the
OpenShift namespace that Superset is deployed in will automatically be granted Admin to Superset.

To launch Superset, go to the routes in the namespace you installed Open Data Hub and click on the route with `superset` name.

### Parameters

There are 11 parameters exposed via KfDef.

#### storage_class

Name of the storage class to be used for PVC created by Hue's database. This requires `storage-class` **overlay** to be enabled as well to work.
#### superset_secret

The secret containing the environment variables to set the admin credentials and the Superset app secret key used to encrypt information in the database. If not specified, environment variables from [`superset`](base/secret-superset.yaml) will be used.

When creating a custom secret, the following information should be added:

* **SUPERSET_ADMIN_USER**: The username of the Superset administrator. If using the `superset` secret, `admin` will be used
* **SUPERSET_ADMIN_FNAME**: The First Name of the Superset administrator. If using the `superset` secret, `admin` will be used
* **SUPERSET_ADMIN_LNAME**: The LastName of the Superset administrator. If using the `superset` secret, `admin` will be used
* **SUPERSET_ADMIN_EMAIL**: The e-mail of the Superset administrator. If using the `superset` secret, `admin@fab.org` will be used
* **SUPERSET_ADMIN_PASSWORD**: The password of the Superset administrator. If using the `superset` secret, `admin` will be used
* **SUPERSET_SECRET_KEY**: The app secret key used by Superset to encrypt information in the database. If using the `superset` secret, `thisISaSECRET_1234` will be used

#### superset_db_secret

This parameter configures the Superset database. The secret of choice must contain `database-name`, `database-user`, and `database-password` keys. If not set, credentials from [`supersetdb-secret`](base/supersetdb-secret.yaml) will be used instead.

#### superset_memory_requests

This parameter will configure the Memory request for Superset. If not set, the default value `1Gi` will be used instead.

#### superset_memory_limits

This parameter will configure the Memory limits for Superset. If not set, the default value `2Gi` will be used instead.

#### superset_cpu_requests

This parameter will configure the CPU request for Superset. If not set, the default value `300m` will be used instead.

#### superset_cpu_limits

This parameter will configure the CPU limits for Superset. If not set, the default value `2` will be used instead.

#### superset_db_memory_requests

This parameter will configure the Memory request for Superset Database. If not set, the default value `300Mi` will be used instead.

#### superset_db_memory_limits

This parameter will configure the Memory limits for Superset Database. If not set, the default value `1Gi` will be used instead.

#### superset_db_cpu_requests

This parameter will configure the CPU request for Superset Database. If not set, the default value `300m` will be used instead.

#### superset_db_cpu_limits

This parameter will configure the CPU request for Superset Database. If not set, the default value `1` will be used instead.

### Superset config file customization

In addition to the above parameters, Superset is configured via a [`superset_config.py`](base/superset_config.py) script.
This script configures a number of important options, including:
  * The SQLAlchemy URL for Superset's Database
  * Superset session timeout settings
  * Superset role paramters
  * Superset OAuth configuration

Users may wish to extend this configuration to further customize their deployment,
for example to map specific user groups to roles in Superset via the
`AUTH_ROLES_MAPPING` variable. In order to do this, do the following:

1. Add your customization in the form of a python file and override the
   [Superset deploymment](base/deployment.yaml) so that the file is mounted
   inside the Superset container
2. Override the [Superset deployment](base/deployment.yaml) and add a
   variable to the Superset container with name `SUPERSET_ADDITIONAL_CONFIG`.
   The value of this environment variable should be the path to your script
   from step 1 above.

At runtime, the contents of your custom file will be dynamically read in
by [superset_config.py](superset_config.py) and executed via the
`exec` command in Python.

### Superset Database Initialization

Prior to running, Superset's database must be initialized. This is handled via the `superset-init` initContainer. Once this is done, the Superset pod should
start running without intervention. If the database is already initialized the initContainer just checks if everything is as expected and finishes with success.
