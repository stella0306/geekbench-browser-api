from typing import Final, Optional

class HTTPUrl:
    # 검색 URL
    BASE_URL:Final[str] = "https://browser.geekbench.com/search?"

    @staticmethod
    def _get_search_url(key: str, page: int = 1, query: Optional[str] = None) -> tuple[str, dict[str, str]]:
        payload = {
            "k": key,
            "page": str(page),
            "q": str(query) if query else "",
            "utf8": "✓"
        }
        
        return HTTPUrl.BASE_URL, payload

    @staticmethod
    def get_cpu_search_url(page: int = 1, query: Optional[str] = None) -> tuple[str, dict[str, str]]:
        return HTTPUrl._get_search_url("v6_cpu", page, query)

    @staticmethod
    def get_gpu_search_url(page: int = 1, query: Optional[str] = None) -> tuple[str, dict[str, str]]:
        return HTTPUrl._get_search_url("v6_compute", page, query)

    @staticmethod
    def get_ai_search_url(page: int = 1, query: Optional[str] = None) -> tuple[str, dict[str, str]]:
        return HTTPUrl._get_search_url("ai", page, query)

if __name__ == "__main__":
    # 사용 예시
    url_manager = HTTPUrl()
    cpu_url, cpu_payload = url_manager.get_ai_search_url(page=1, query="Intel")
    print("CPU URL:", cpu_url)
    print("CPU Payload:", cpu_payload)
