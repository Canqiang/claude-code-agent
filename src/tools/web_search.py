"""Web search and fetch tools."""
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List
from .base import Tool, ToolParameter


class WebSearchTool(Tool):
    """Tool for fetching and parsing web content."""

    @property
    def name(self) -> str:
        return "fetch_web_content"

    @property
    def description(self) -> str:
        return "Fetch and extract text content from a web URL"

    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="url",
                type="string",
                description="The URL to fetch content from",
                required=True
            )
        ]

    def execute(self, **kwargs) -> Dict[str, Any]:
        url = kwargs.get("url")

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Get text
            text = soup.get_text()

            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)

            return {
                "success": True,
                "result": {
                    "url": url,
                    "content": text[:5000],  # Limit to first 5000 chars
                    "title": soup.title.string if soup.title else None,
                    "status_code": response.status_code
                }
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Error fetching URL: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error parsing content: {str(e)}"
            }
