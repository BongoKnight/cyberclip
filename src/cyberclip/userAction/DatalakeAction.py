try:
    from userAction.actionInterface import actionInterface
except ImportError:
    from actionInterface import actionInterface

import json
import re

import requests

DEFAULT_BASE_URL = "https://datalake.cert.orangecyberdefense.com/api"
AUTH_TOKEN_ENDPOINT = "/v3/auth/token/"
LOOKUP_ENDPOINT = "/v3/mrti/threats/lookup/"
ADVANCED_THREATS_ENDPOINT = "/v3/mrti/advanced-queries/threats/"

LOOKUP_SUPPORTED_TYPES = {
    "asnum",
    "cidr",
    "domain",
    "ip",
    "ipv6",
    "mail",
    "md5",
    "phone",
    "sha1",
    "sha256",
    "url",
}

LOOKUP_TYPE_MAP = {
    "asnum": "as",
    "cidr": "ip_range",
    "domain": "domain",
    "ip": "ip",
    "ipv6": "ip",
    "mail": "email",
    "md5": "file",
    "phone": "phone_number",
    "sha1": "file",
    "sha256": "file",
    "url": "url",
}

QUERY_MODE_CHOICES = [
    "Atom details",
    "Regexp",
    "Threat entity ID",
    "Tags",
]

ATOM_TYPE_CHOICES = [
    "as",
    "certificate",
    "domain",
    "email",
    "file",
    "ip",
    "url",
]

DEFAULT_QUERY_PARAMETERS = {
    "Query": {"type": "longtext", "value": "example.com"},
    "Query mode": {
        "type": "list",
        "choices": QUERY_MODE_CHOICES,
        "value": "Atom details",
    },
    "Output atom types": {
        "type": "fixedlist",
        "choices": ATOM_TYPE_CHOICES,
        "value": [],
    },
    "Max results": {"type": "text", "value": "20"},
}


class _DatalakeMixin:
    def _build_base_url(self):
        return str(self.conf.get("base_url") or DEFAULT_BASE_URL).rstrip("/")

    def _get_email(self):
        email = str(self.conf.get("email", "")).strip()
        if not email:
            raise RuntimeError(
                "Missing Datalake email. Configure DATALAKE_EMAIL in .env"
            )
        return email

    def _get_password(self):
        password = str(self.conf.get("password", "")).strip()
        if not password:
            raise RuntimeError(
                "Missing Datalake password. Configure DATALAKE_PASSWORD in .env"
            )
        return password

    def _normalize_int(self, value, default=20, minimum=0):
        try:
            normalized = int(str(value).strip())
            return max(minimum, normalized)
        except Exception:
            return default

    def _split_query_inputs(self, query):
        return [line.strip() for line in str(query or "").splitlines() if line.strip()]

    def _normalize_observable_text(self, value):
        return (
            str(value or "")
            .strip()
            .replace("[.]", ".")
            .replace("[://]", "://")
            .replace("hxxp://", "http://")
            .replace("hxxps://", "https://")
        )

    def _normalize_lookup_value(self, observable_type, observable):
        normalized = self._normalize_observable_text(observable)
        if observable_type == "asnum":
            match = re.fullmatch(r"(?i)as(\d+)", normalized)
            return match.group(1) if match else normalized
        return normalized

    def _normalize_query_mode(self, value):
        normalized = str(value or "").strip().lower()
        mapping = {
            "atom details": "atom_details",
            "regexp": "regexp",
            "threat entity id": "threat_entity",
            "threat entity": "threat_entity",
            "tags": "tags",
        }
        return mapping.get(normalized, "atom_details")

    def _normalize_string_values(self, value):
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str):
            return [
                item.strip()
                for item in value.replace("\r", "\n").replace(",", "\n").split("\n")
                if item.strip()
            ]
        return []

    def _normalize_int_values(self, values, label):
        normalized = []
        for value in values:
            try:
                normalized.append(int(str(value).strip()))
            except Exception as exc:
                raise RuntimeError(
                    f"{label} expects integer IDs, got: {value}"
                ) from exc
        return normalized

    def _format_http_error(self, response, exc):
        details = f"{response.status_code} {response.reason}"
        try:
            body = response.json()
        except Exception:
            body = response.text.strip()

        if body:
            if isinstance(body, (dict, list)):
                details = f"{details}: {json.dumps(body)}"
            else:
                details = f"{details}: {body}"
        return details

    def _authenticate(self):
        cached_token = getattr(self, "_access_token", "")
        if cached_token:
            return cached_token

        response = requests.post(
            f"{self._build_base_url()}{AUTH_TOKEN_ENDPOINT}",
            headers={
                "accept": "application/json",
                "content-type": "application/json",
            },
            json={
                "email": self._get_email(),
                "password": self._get_password(),
            },
            timeout=20,
        )
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise RuntimeError(self._format_http_error(response, exc)) from exc

        payload = response.json()
        access_token = (
            payload.get("access_token") or payload.get("access") or payload.get("token")
        )
        if not access_token:
            raise RuntimeError(
                "Datalake authentication succeeded but no access token was returned."
            )

        self._access_token = str(access_token)
        self._refresh_token = str(
            payload.get("refresh_token") or payload.get("refresh") or ""
        )
        return self._access_token

    def _build_headers(self):
        return {
            "accept": "application/json",
            "Authorization": f"Token {self._authenticate()}",
        }

    def _request(self, method, path, params=None, json_body=None):
        headers = self._build_headers()
        url = f"{self._build_base_url()}{path}"
        method = str(method or "").upper()
        if method == "GET":
            response = requests.get(url, headers=headers, params=params, timeout=20)
        elif method == "POST":
            response = requests.post(
                url,
                headers={**headers, "content-type": "application/json"},
                json=json_body,
                timeout=20,
            )
        else:
            raise RuntimeError(f"Unsupported Datalake request method: {method}")
        return response

    def _request_json(self, method, path, params=None, json_body=None):
        response = self._request(method, path, params=params, json_body=json_body)
        if response.status_code == 401:
            self._access_token = ""
            self._refresh_token = ""
            response = self._request(method, path, params=params, json_body=json_body)

        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise RuntimeError(self._format_http_error(response, exc)) from exc

        content_type = response.headers.get("content-type", "")
        if "json" in content_type.lower():
            return response.json()
        return {"raw": response.text}

    def _lookup_observable(self, observable_type, observable):
        atom_type = LOOKUP_TYPE_MAP[observable_type]
        atom_value = self._normalize_lookup_value(observable_type, observable)
        response = self._request_json(
            "GET",
            LOOKUP_ENDPOINT,
            params={
                "atom_type": atom_type,
                "atom_value": atom_value,
                "hashkey_only": "false",
            },
        )
        return {
            "atom_type": atom_type,
            "atom_value": atom_value,
            "response": response,
        }

    def _build_advanced_query_item(self, raw_query, query_mode):
        values = self._split_query_inputs(raw_query)
        if not values:
            raise RuntimeError("No query provided")

        item = {"field": query_mode}
        if query_mode == "threat_entity":
            item["type"] = "filter"
            item["multi_values"] = self._normalize_int_values(
                values, "Threat entity ID"
            )
        elif query_mode == "tags":
            item["type"] = "filter"
            item["multi_values"] = values
        else:
            item["type"] = "search"
            if len(values) == 1:
                item["value"] = values[0]
            else:
                item["multi_values"] = values
            if query_mode in {"atom_details", "regexp"}:
                item["atom_values_only"] = True

        return item

    def _build_advanced_query_payload(self):
        raw_query = self.get_param_value("Query")
        if not raw_query.strip():
            raise RuntimeError("No query provided")

        limit = self._normalize_int(
            self.get_param_value("Max results"),
            default=20,
            minimum=1,
        )
        query_mode = self._normalize_query_mode(self.get_param_value("Query mode"))
        atom_types = self._normalize_string_values(
            self.get_param_value("Output atom types")
        )
        items = [self._build_advanced_query_item(raw_query, query_mode)]
        if atom_types:
            items.append(
                {
                    "field": "atom_type",
                    "type": "filter",
                    "multi_values": atom_types,
                }
            )
        return query_mode, {
            "limit": limit,
            "offset": 0,
            "query_body": {
                "AND": [
                    {
                        "AND": items,
                    }
                ]
            },
        }


class SearchInDatalakeAction(_DatalakeMixin, actionInterface):
    """An action module to search IoCs in Datalake."""

    def __init__(self, parsers={}, supportedType=LOOKUP_SUPPORTED_TYPES):
        super().__init__(parsers=parsers, supportedType=supportedType)
        self.description = "Datalake: Search IoC"
        self.indicators = "🔑"
        self.load_conf("Datalake")

    def execute(self):
        self.results = {}
        observables = self.get_observables()
        observable_items = []
        for observable_type in self.supportedType:
            observable_items.extend(
                (observable_type, observable)
                for observable in observables.get(observable_type, [])
            )

        for observable_type, observable in sorted(set(observable_items)):
            try:
                self.results[observable] = self._lookup_observable(
                    observable_type, observable
                )
            except Exception as exc:
                self.results[observable] = {"error": str(exc)}
        return self.results

    def __str__(self):
        self.execute()
        return "\r\n".join(json.dumps(value) for value in self.results.values())


class QueryDatalakeAction(_DatalakeMixin, actionInterface):
    """An action module to run Datalake advanced queries."""

    def __init__(
        self, parsers={}, supportedType={"text"}, complex_param=DEFAULT_QUERY_PARAMETERS
    ):
        super().__init__(
            parsers=parsers, supportedType=supportedType, complex_param=complex_param
        )
        self.description = "Datalake: Query"
        self.indicators = "🔑"
        self.load_conf("Datalake")

    def execute(self):
        try:
            query_mode, payload = self._build_advanced_query_payload()
            response = self._request_json(
                "POST",
                ADVANCED_THREATS_ENDPOINT,
                json_body=payload,
            )
            self.results = {
                "query_mode": query_mode,
                "request_body": payload,
                "response": response,
            }
        except Exception as exc:
            self.results = {"error": str(exc)}
        return self.results

    def __str__(self):
        self.execute()
        return json.dumps(self.results)
