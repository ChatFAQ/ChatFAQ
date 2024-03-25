import aiohttp

class RetrieverClient:
    """Client to retrieve documents from a retriever deployment."""
    def __init__(self, deployment_url):
        self.deployment_url = deployment_url

    async def retrieve(self, query, top_k=5, threshold=0.5):
        async with aiohttp.ClientSession() as session:
            data = {"query": query, "top_k": top_k, "threshold": threshold}
            async with session.post(self.deployment_url, json=data) as response:
                result = await response.json()
                return result