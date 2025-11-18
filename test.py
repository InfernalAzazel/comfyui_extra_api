import asyncio
import httpx


class ExtraApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(base_url=self.base_url)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self._client is not None:
            await self._client.aclose()

    async def list_output_images(self, temp: bool = False):
        params = {"temp": "true" if temp else "false"}
        r = await self._client.get("/output-images", params=params)
        r.raise_for_status()
        return r.json()

    async def delete_output_image(self, filename: str, temp: bool = False):
        params = {"temp": "true" if temp else "false"}
        r = await self._client.delete(f"/output-images/{filename}", params=params)
        r.raise_for_status()
        return r.json()

    async def delete_input_image(self, filename: str, temp: bool = False):
        params = {"temp": "true" if temp else "false"}
        r = await self._client.delete(f"/input-images/{filename}", params=params)
        r.raise_for_status()
        return r.json()


async def _example():
    async with ExtraApiClient("http://127.0.0.1:8000/extra-api/v1") as api:
        print(await api.list_output_images())
        print("_" * 50)
        # print(await api.delete_output_image("ComfyUI_00001_.png"))
        # print(await api.delete_input_image("1.png"))

if __name__ == "__main__":
    asyncio.run(_example())