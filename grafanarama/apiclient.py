import json
import requests

from pydantic import BaseModel


class Gr2JSON(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, BaseModel):
            return o.model_dump(mode='json')
        return super().default(o)


class GrafanaClient(object):
    def __init__(
        self, host="localhost", port=3000, apiKey=None, auth_user=None, auth_pass=None, use_https=False
    ):
        self._host = host
        self._port = port
        self._apiKey = apiKey
        self._auth_user = auth_user
        self._auth_pass = auth_pass
        self._use_https = use_https
        self._results = None
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self._apiKey:
            # Strip any whitespace that might have been accidentally included
            self._apiKey = self._apiKey.strip()
            
            # Grafana API keys can use different formats depending on version:
            # 1. X-Grafana-API-Key: <key> (traditional format, most common)
            # 2. Authorization: Bearer <key> (newer format for service account tokens)
            # Use X-Grafana-API-Key as it's the most widely supported format
            self.headers["X-Grafana-API-Key"] = self._apiKey
            
            # Don't use basic auth if API key is provided
            if auth_user or auth_pass:
                import warnings
                warnings.warn("Both API key and basic auth provided. API key will be used, basic auth ignored.")

    @property
    def apiKey(self):
        return self._apiKey

    @property
    def auth(self):
        if self._auth_user and self._auth_pass:
            return (self._auth_user, self._auth_pass)
        else:
            return None

    @property
    def results(self):
        return self._results

    @property
    def server(self):
        return f"{self._host}:{self._port}"
    
    @property
    def base_url(self):
        protocol = "https" if self._use_https else "http"
        return f"{protocol}://{self.server}"

    def send_dashboard(self, dashboard, overwrite=False, message=""):
        dest = "/api/dashboards/db"
        url = f"{self.base_url}{dest}"
        data = dict(dashboard=dashboard, overwrite=overwrite, message=message)
        return self.post(url, data)

    def send_datasource(self, datasource):
        # Handle both Pydantic models and dicts
        if isinstance(datasource, BaseModel):
            name = datasource.name if hasattr(datasource, 'name') else None
        elif isinstance(datasource, dict):
            name = datasource.get('name')
        else:
            raise ValueError("datasource must be a Pydantic model or dict with a 'name' field")
        
        if not name:
            raise ValueError("datasource must have a 'name' field")
        
        id = self.get_datasource_id_byname(name=name)
        if id:
            print(f"found id {id} for {name}...updating")
            dest = f"/api/datasources/{id}"
            url = f"{self.base_url}{dest}"
            return self.put(url, datasource)
        else:
            print(f"not found {name}...adding")
            dest = "/api/datasources"
            url = f"{self.base_url}{dest}"
            return self.post(url, datasource)

    def get_datasource_id_byname(self, name):
        dest = f"/api/datasources/name/{name}"
        url = f"{self.base_url}{dest}"
        result = self.get(url)
        if result:
            return result.get("id", None)

    def get_dashboard(self, slug):
        dest = f"/api/dashboards/db/{slug}"
        url = f"{self.base_url}{dest}"
        result = self.get(url)
        if result:
            return result.get("dashboard", None)

    def delete(self, url):
        self._results = requests.delete(url, headers=self.headers, auth=self.auth)
        if self.results.status_code == requests.codes.ok:
            return True
        return False

    def get(self, url):
        self._results = requests.get(url, headers=self.headers, auth=self.auth)
        if self.results.status_code == requests.codes.ok:
            return self.results.json()
        elif self.results.status_code == 401:
            self._print_error()
        return None

    def post(self, url, data):
        self._results = requests.post(
            url, data=self._encode_data(data), headers=self.headers, auth=self.auth
        )
        if self.results.status_code == requests.codes.ok:
            return True
        else:
            self._print_error()
            return False
    
    def _print_error(self):
        """Print detailed error information for debugging"""
        status_code = self.results.status_code
        print(f"Error: HTTP {status_code}")
        try:
            error_data = self.results.json()
            if isinstance(error_data, dict):
                if "message" in error_data:
                    print(f"Message: {error_data['message']}")
                print(f"Response: {json.dumps(error_data, indent=2)}")
            else:
                print(f"Response: {error_data}")
        except Exception:
            print(f"Response text: {self.results.text}")
        
        if status_code == 401:
            print("\nAuthentication failed. Check:")
            print("  - API key is correct and has Admin role")
            print("  - API key format: Should be 'glsa_...' for service accounts")
            print("  - API key hasn't expired")
            print("  - If using basic auth, check username/password")
            print(f"\nDebug info:")
            print(f"  - Using API key: {'Yes' if self._apiKey else 'No'}")
            if self._apiKey:
                # Show first/last few chars for debugging without exposing full key
                key_preview = f"{self._apiKey[:8]}...{self._apiKey[-4:]}" if len(self._apiKey) > 12 else "***"
                print(f"  - API key preview: {key_preview}")
                print(f"  - API key length: {len(self._apiKey)}")
                print(f"  - Auth header: X-Grafana-API-Key")
            print(f"  - Using basic auth: {'Yes' if (self._auth_user and self._auth_pass) else 'No'}")

    def put(self, url, data):
        self._results = requests.put(
            url, data=self._encode_data(data), headers=self.headers, auth=self.auth
        )
        if self.results.status_code == requests.codes.ok:
            return True
        return False

    def _encode_data(self, data):
        return json.dumps(data, cls=Gr2JSON)


def print_grafana(object):
    print(json.dumps(obj=object, cls=Gr2JSON, indent=4))
