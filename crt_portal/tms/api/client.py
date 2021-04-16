from django.conf import settings
import requests


class TMSClient(object):
    """
    TMS API Client
    """

    def __init__(self, api_root=None, api_auth_token=None):
        self.api_root = api_root or settings.TMS_TARGET_ENDPOINT
        self.api_auth_token = api_auth_token or settings.TMS_AUTH_TOKEN
        self.headers = {'X-AUTH-TOKEN': self.api_auth_token}

    def _get_endpoint(self, target=''):
        """
        Return full uri for target resource
        """
        return self.api_root + target

    def get(self, target='', query_parameters='', payload=None):
        """
        GET w/ parameters to target
        """
        endpoint = self._get_endpoint(target)
        return requests.get(endpoint + query_parameters, headers=self.headers)

    def post(self, target='', query_parameters='', payload=None):
        """
        POST payload as json and parameters to target
        """
        endpoint = self._get_endpoint(target)
        return requests.post(endpoint + query_parameters, json=payload, headers=self.headers)
