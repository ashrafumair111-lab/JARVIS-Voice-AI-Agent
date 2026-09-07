"""Web tools: Tavily search + full webpage extraction."""

import requests

import config


class WebTools:
    # ------------------------------------------------------------- search
    def search(self, query, max_results=5):
        if not config.TAVILY_API_KEY:
            return {"error": "Tavily API key is missing."}
        query = (query or "").strip()
        if not query:
            return {"error": "Empty search query."}
        try:
            resp = requests.post(
                config.TAVILY_URL,
                json={
                    "api_key": config.TAVILY_API_KEY,
                    "query": query,
                    "search_depth": "advanced",
                    "max_results": min(int(max_results), 8),
                    "include_answer": True,
                    "include_raw_content": False,
                },
                timeout=25,
            )
            resp.raise_for_status()
            data = resp.json()
            results = [
                {
                    "title": r.get("title"),
                    "url": r.get("url"),
                    "content": (r.get("content") or "")[:800],
                }
                for r in data.get("results", [])
            ]
            return {"answer": data.get("answer", ""), "results": results}
        except Exception as exc:
            return {"error": f"Tavily search failed: {exc}"}

    # ------------------------------------------------------------- fetch
    def fetch(self, url):
        url = (url or "").strip()
        if not url:
            return {"error": "No URL given."}
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
            )
        }
        try:
            resp = requests.get(url, headers=headers, timeout=25)
            resp.raise_for_status()
            html = resp.text

            text = ""
            try:
                import trafilatura

                text = trafilatura.extract(html) or ""
            except Exception:
                pass

            if not text.strip():
                try:
                    from bs4 import BeautifulSoup

                    soup = BeautifulSoup(html, "html.parser")
                    for tag in soup(["script", "style", "nav", "footer", "header"]):
                        tag.decompose()
                    text = soup.get_text("\n", strip=True)
                except Exception:
                    text = ""

            text = " ".join(text.split())[:6000]
            if not text.strip():
                return {"url": url, "content": "(no extractable text)"}
            return {"url": url, "content": text}
        except Exception as exc:
            return {"error": f"Fetch failed for {url}: {exc}"}