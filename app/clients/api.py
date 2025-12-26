import asyncio
import httpx
import logging
from json import JSONDecodeError
from typing import Any, Dict, Optional
from logger.logger import logger
from exception import NotFoundException, APIClientException



class APIClient:

    _instance:Optional["APIClient"] = None 

    def __new__(cls, *args, **kwargs):
        
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance


    def __init__(
        self,
        timeout: Optional[int] = 10,
        max_connections:Optional[int] = 20,
        max_keepalive_connections:Optional[int] = 40,
        keepalive_expiry:Optional[float] = 30.0
    ):
        # self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_connections = max_connections
        self.max_keepalive_connections = max_keepalive_connections
        self.keepalive_expiry = keepalive_expiry

        # Create an HTTP client with connection pooling
        self.client = httpx.AsyncClient(
            timeout=self.timeout,
            limits=httpx.Limits(
                max_connections=self.max_connections,
                max_keepalive_connections=self.max_keepalive_connections,
                keepalive_expiry=self.keepalive_expiry
            )
        )

    def _get_headers(self, headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        default_headers = {
            "Content-Type": "application/json",
        }

        if headers:
            default_headers.update(headers)

        return default_headers

    async def _make_request(
        self,
        method: str,
        url: str,
        auth_token:Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        retries:Optional[int] = 3
    ) -> Any:
        
        headers = self._get_headers(headers)
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"

        for attempt in range(1, retries + 1):
            try:
                logger.info(
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

                logger.info(f"Response received: {response.status_code}")
                logger.info(f"Respnose dir: {response.__dict__}")
                return response.raise_for_status().json()
            except httpx.ConnectError as e:
                logger.error(f"Connection error on attempt {attempt}: {e}")
            except httpx.ReadTimeout as e:
                logger.error(f"Timeout on attempt {attempt}: {e}")
            except httpx.RequestError as e:
                logger.error(f"Request error on attempt {attempt}: {e}")
            except JSONDecodeError as e:
                raise APIClientException("Error while decoding response as JSON") from e
            except httpx.HTTPStatusError as e:
                logger.error(
                    f"HTTP error on attempt {attempt}: {e.response.status_code} {e.response.text}"
                )
                raise APIClientException(str(e), e.request, e.response) from e

            backoff_time = 2 ** (attempt - 1)
            logger.info(f"Retrying in {backoff_time} seconds...")
            await asyncio.sleep(backoff_time)

        raise APIClientException(
            f"Failed to complete {method} request to {url} after {self.retries} attempts."
        )

    async def get(
        self,
        url: str,
        auth_token:Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        retries:Optional[int] = 3
    ) -> Any:
        return await self._make_request("GET", url, params=params, auth_token=auth_token,retries=retries, headers=headers)

    async def put(
        self,
        url: str,
        data: Dict[str, Any],
        auth_token:Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        retries:Optional[int] = 3
    ) -> Any:
        return await self._make_request("PUT", url, data=data,auth_token=auth_token,retries=retries, headers=headers)

    async def post(
        self,
        url: str,
        data: Dict[str, Any],
        auth_token:Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        retries:Optional[int] = 3
    ) -> Any:
        return await self._make_request("POST", url, data=data, headers=headers, auth_token=auth_token,retries=retries)

    async def delete(
        self, 
        url: str,
        auth_token:Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        retries:Optional[int] = 3

    ) -> Any:
        return await self._make_request("DELETE", url, headers=headers, auth_token=auth_token,retries=retries)

    async def patch(
        self,
        url: str,
        data: Dict[str, Any],
        auth_token:Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        retries:Optional[int] = 3
    ) -> Any:
        return await self._make_request("PATCH", url,auth_token=auth_token,retries=retries, data=data, headers=headers)

    async def close(self):
        """Close the HTTP client."""
        logger.info(f"Closing {self.client._limits.max_connections} connections...")
        if self.client:
            await self.client.aclose()
            self.client = None
            logger.info("Successfully closed api client connection.")

api_client:Optional[APIClient] = None

def create_api_client() -> APIClient :
    global api_client
    if api_client is None:
        api_client = APIClient(
            timeout=15,
            max_connections=20,
            max_keepalive_connections=40,
            keepalive_expiry=30.0
        )
    logger.info(f"Successfully created api client: {api_client}")
    return api_client


async def close_api_client() -> None:
    global api_client
    if api_client:
        await api_client.close()
        api_client = None
        logger.info("Successfully closed api client connection.")

