from typing import Final, Optional

class HTTPUrl:
    # 검색 URL
    BASE_URL:Final[str] = "https://browser.geekbench.com/search?"

    @staticmethod
    def _get_search_url(key: str, page: int = 1, query: Optional[str] = None) -> tuple[str, dict[str, str]]:
        """
        검색 URL과 페이로드를 반환하는 내부 메서드입니다.

        :param key: 검색 키 (예: 'v6_cpu', 'v6_compute', 'ai')
        :param page: 페이지 번호
        :param query: 검색 쿼리
        :return: 검색 URL과 페이로드
        """
        payload = {
            "k": key,
            "page": str(page),
            "q": str(query) if query else "",
            "utf8": "✓"
        }
        
        return HTTPUrl.BASE_URL, payload

    @staticmethod
    def get_cpu_search_url(page: int = 1, query: Optional[str] = None) -> tuple[str, dict[str, str]]:
        """CPU 검색 URL과 페이로드를 반환합니다."""
        return HTTPUrl._get_search_url("v6_cpu", page, query)

    @staticmethod
    def get_gpu_search_url(page: int = 1, query: Optional[str] = None) -> tuple[str, dict[str, str]]:
        """GPU 검색 URL과 페이로드를 반환합니다."""
        return HTTPUrl._get_search_url("v6_compute", page, query)

    @staticmethod
    def get_ai_search_url(page: int = 1, query: Optional[str] = None) -> tuple[str, dict[str, str]]:
        """AI 검색 URL과 페이로드를 반환합니다."""
        return HTTPUrl._get_search_url("ai", page, query)

if __name__ == "__main__":
    # 사용 예시
    url_manager = HTTPUrl()
    cpu_url, cpu_payload = url_manager.get_ai_search_url(page=1, query="Intel")
    print("CPU URL:", cpu_url)
    print("CPU Payload:", cpu_payload)
