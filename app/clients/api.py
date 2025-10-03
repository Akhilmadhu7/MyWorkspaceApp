import asyncio
import httpx
import logging
from json import JSONDecodeError
from typing import Any, Dict, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class APIClientError(Exception):
    """Custom exception for APIClient errors."""

    def __init__(self, message, request=None, response=None):
        super().__init__(message)
        self.request = request
        self.response = response


class APIClient:
    def __init__(
        self,
        base_url: str,
        timeout: int = 10,
        retries: int = 1,
        auth_token: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retries = retries
        self.auth_token = auth_token
        self.logger = logger or logging.getLogger(__name__)
        # Create an HTTP client with connection pooling
        self.client = httpx.AsyncClient(timeout=self.timeout)

    def _get_headers(self, headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        default_headers = {
            "Content-Type": "application/json",
        }
        if self.auth_token:
            default_headers["Authorization"] = f"Bearer {self.auth_token}"

        if headers:
            default_headers.update(headers)

        return default_headers

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        url = (
            f"{self.base_url}/{endpoint.lstrip('/')}"
            if endpoint
            else f"{self.base_url}"
        )
        headers = self._get_headers(headers)

        for attempt in range(1, self.retries + 1):
            try:
                self.logger.info(
                    f"{method} {url} (attempt {attempt}) with payload: {data}"
                )
                if method == "GET":
                    response = await self.client.get(
                        url, params=params, headers=headers
                    )
                elif method == "POST":
                    response = await self.client.post(url, json=data, headers=headers)
                elif method == "PUT":
                    response = await self.client.put(url, json=data, headers=headers)
                elif method == "DELETE":
                    response = await self.client.delete(url, headers=headers)
                elif method == "PATCH":
                    response = await self.client.patch(url, json=data, headers=headers)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                self.logger.info(f"Response received: {response.status_code}")
                return response.raise_for_status().json()
            except httpx.ConnectError as e:
                self.logger.error(f"Connection error on attempt {attempt}: {e}")
            except httpx.ReadTimeout as e:
                self.logger.error(f"Timeout on attempt {attempt}: {e}")
            except httpx.RequestError as e:
                self.logger.error(f"Request error on attempt {attempt}: {e}")
            except JSONDecodeError as e:
                raise APIClientError("Error while decoding response as JSON") from e
            except httpx.HTTPStatusError as e:
                self.logger.error(
                    f"HTTP error on attempt {attempt}: {e.response.status_code} {e.response.text}"
                )
                raise APIClientError(str(e), e.request, e.response) from e

            backoff_time = 2 ** (attempt - 1)
            self.logger.info(f"Retrying in {backoff_time} seconds...")
            await asyncio.sleep(backoff_time)

        raise APIClientError(
            f"Failed to complete {method} request to {url} after {self.retries} attempts."
        )

    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        return await self._make_request("GET", endpoint, params=params, headers=headers)

    async def put(
        self,
        endpoint: str,
        data: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        return await self._make_request("PUT", endpoint, data=data, headers=headers)

    async def post(
        self,
        endpoint: str,
        data: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        return await self._make_request("POST", endpoint, data=data, headers=headers)

    async def delete(
        self, endpoint: str, headers: Optional[Dict[str, str]] = None
    ) -> Any:
        return await self._make_request("DELETE", endpoint, headers=headers)

    async def patch(
        self,
        endpoint: str,
        data: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        return await self._make_request("PATCH", endpoint, data=data, headers=headers)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def __aenter__(self):
        """Called when entering the 'async with' block."""
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        """Called when exiting the 'async with' block."""
        await self.close()
