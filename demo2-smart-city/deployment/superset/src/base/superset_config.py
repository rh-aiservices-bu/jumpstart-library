import os
import requests

from flask_appbuilder.security.manager import AUTH_OAUTH
from superset.security import SupersetSecurityManager

MAPBOX_API_KEY = os.getenv('MAPBOX_API_KEY', '')

db_username = os.environ['POSTGRESQL_USERNAME']
db_password = os.environ['POSTGRESQL_PASSWORD']
db_name = os.environ['POSTGRESQL_DATABASE']
SQLALCHEMY_DATABASE_URI = (f'postgresql://{db_username}:'
                           f'{db_password}@supersetdb:5432/{db_name}')

SQLALCHEMY_TRACK_MODIFICATIONS = True
SECRET_KEY = os.getenv('SUPERSET_SECRET_KEY', '')
DATA_DIR = '/var/lib/superset'
LOG_LEVEL = 'INFO'
FEATURE_FLAGS = {
    'ENABLE_TEMPLATE_PROCESSING': True,
}

SUPERSET_WEBSERVER_PROTOCOL = 'https'
ENABLE_PROXY_FIX = True

AUTH_USER_REGISTRATION = True
AUTH_USER_REGISTRATION_ROLE = 'Public'
AUTH_ROLE_ADMIN = 'Admin'
PUBLIC_ROLE_LIKE = 'Gamma'

# if we should replace ALL the user's roles each login
AUTH_ROLES_SYNC_AT_LOGIN = True

# force users to re-auth after 6 hours of inactivity (to keep roles in sync)
PERMANENT_SESSION_LIFETIME = 21600

SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 15,
    'pool_timeout': 60,
    'pool_recycle': 3600
}

# Set Webserver timeout to 30 minutes to wait for the queries to be executed
SUPERSET_WEBSERVER_TIMEOUT = 1800

SYSTEM_CERT_BUNDLE = '/etc/ssl/certs/ca-bundle.crt'
CLUSTER_CERT_BUNDLE = '/run/secrets/kubernetes.io/serviceaccount/ca.crt'
COMBINED_CERT_BUNDLE = '/tmp/superset-combined-cert-bundle.crt'

with open(COMBINED_CERT_BUNDLE, 'a+') as combined:
    with open(SYSTEM_CERT_BUNDLE) as sys_bundle:
        combined.write(sys_bundle.read())

    with open(CLUSTER_CERT_BUNDLE) as clus_bundle:
        combined.write(clus_bundle.read())

os.environ['CURL_CA_BUNDLE'] = COMBINED_CERT_BUNDLE

AUTH_TYPE = AUTH_OAUTH

service_account_path = '/var/run/secrets/kubernetes.io/serviceaccount'
with open(os.path.join(service_account_path, 'token')) as f:
    client_secret = f.read().strip()

with open(os.path.join(service_account_path, 'namespace')) as f:
    namespace = f.read().strip()

openshift_url = 'https://openshift.default.svc.cluster.local'
auth_info_url = f'{openshift_url}/.well-known/oauth-authorization-server'
auth_api_url = requests.get(auth_info_url, verify=False).json().get('issuer')

OAUTH_PROVIDERS = [
    {
        'name': 'openshift',
        'icon': 'fa-circle-o',
        'token_key': 'access_token',
        'remote_app': {
            'client_id': f'system:serviceaccount:{namespace}:superset',
            'client_secret': client_secret,
            'api_base_url': 'https://openshift.default.svc.cluster.local:443',
            'client_kwargs': {
                'scope': 'user:info',
            },
            'access_token_url': f'{auth_api_url}/oauth/token',
            'authorize_url': f'{auth_api_url}/oauth/authorize',
            'token_endpoint_auth_method': 'client_secret_post'
        }
    }
]


class CustomSecurityManager(SupersetSecurityManager):

    def user_is_namespace_admin(self, provider, username):
        rolebindings_endpoint = ('apis/rbac.authorization.k8s.io/v1/'
                                 f'namespaces/{namespace}/'
                                 'rolebindings/admin')

        headers = {}
        headers["Accept"] = "application/json"
        headers["Authorization"] = f"Bearer {client_secret}"

        rb_url = f'{openshift_url}/{rolebindings_endpoint}'
        data = requests.get(rb_url, verify=False, headers=headers).json()

        subjects = data.get('subjects', [])
        for subject in subjects:
            if subject.get('name', '') == username:
                return True

        return False

    def oauth_user_info(self, provider, response=None):
        me = self.appbuilder.sm.oauth_remotes[provider].get(
            "apis/user.openshift.io/v1/users/~"
        )
        data = me.json()
        username = data.get('metadata').get('name')
        full_name = data.get('fullName', '')
        first_name = ''
        last_name = ''
        if ' ' in full_name:
            first_name = full_name.split(' ')[0]
            last_name = full_name.split(' ')[1]
        if self.user_is_namespace_admin(provider, username):
            roles = ['Admin']
        else:
            roles = []

        return {
            "username": username,
            'name': full_name,
            'first_name': first_name,
            'last_name': last_name,
            'email': username,
            "role_keys": roles
        }

    def auth_user_oauth(self, userinfo):
        user = super(CustomSecurityManager, self).auth_user_oauth(userinfo)
        for rk in userinfo['role_keys']:
              role = self.find_role(rk)
              if role is not None and role not in user.roles:
                user.roles.append(role)
        self.update_user(user)  # update user roles

        return user


CUSTOM_SECURITY_MANAGER = CustomSecurityManager

additional_config_path = os.getenv('SUPERSET_ADDITIONAL_CONFIG')
if additional_config_path:
    with open(additional_config_path) as f:
        additional_config = f.read()
        exec(additional_config)
