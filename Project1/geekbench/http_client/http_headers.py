from typing import Final

class HTTPHeaders:
    # 공통 HTTP 헤더 상수
    ACCEPT: Final[str] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
    ACCEPT_ENCODING: Final[str] = "gzip, deflate, br, zstd"
    ACCEPT_LANGUAGE: Final[str] = "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"
    CACHE_CONTROL: Final[str] = "max-age=0"
    CONNECTION: Final[str] = "keep-alive"
    COOKIE: Final[str] = ""  # 초기값은 빈 문자열
    DNT: Final[str] = "1"
    HOST: Final[str] = "browser.geekbench.com"
    IF_NONE_MATCH: Final[str] = ""
    REFERER: Final[str] = ""
    SEC_FETCH_DEST: Final[str] = "document"
    SEC_FETCH_MODE: Final[str] = "navigate"
    SEC_FETCH_SITE: Final[str] = "same-origin"
    SEC_FETCH_USER: Final[str] = "?1"
    UPGRADE_INSECURE_REQUESTS: Final[str] = "1"
    USER_AGENT: Final[str] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
    SEC_CH_UA: Final[str] = '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"'
    SEC_CH_UA_MOBILE: Final[str] = "?0"
    SEC_CH_UA_PLATFORM: Final[str] = '"Windows"'

    @staticmethod
    def get_search_headers(search_type:str) -> dict[str, str]:
        
        # 공통 헤더 생성
        common_headers = {
                "Accept": HTTPHeaders.ACCEPT,
                "Accept-Encoding": HTTPHeaders.ACCEPT_ENCODING,
                "Accept-Language": HTTPHeaders.ACCEPT_LANGUAGE,
                "Cache-Control": HTTPHeaders.CACHE_CONTROL,
                "Connection": HTTPHeaders.CONNECTION,
                # "Cookie": HTTPHeaders.COOKIE,
                "DNT": HTTPHeaders.DNT,
                "Host": HTTPHeaders.HOST,
                # "If-None-Match": HTTPHeaders.IF_NONE_MATCH,
                "Referer": HTTPHeaders.REFERER,
                "Sec-Fetch-Dest": HTTPHeaders.SEC_FETCH_DEST,
                "Sec-Fetch-Mode": HTTPHeaders.SEC_FETCH_MODE,
                "Sec-Fetch-Site": HTTPHeaders.SEC_FETCH_SITE,
                "Sec-Fetch-User": HTTPHeaders.SEC_FETCH_USER,
                "Upgrade-Insecure-Requests": HTTPHeaders.UPGRADE_INSECURE_REQUESTS,
                "User-Agent": HTTPHeaders.USER_AGENT,
                "sec-ch-ua": HTTPHeaders.SEC_CH_UA,
                "sec-ch-ua-mobile": HTTPHeaders.SEC_CH_UA_MOBILE,
                "sec-ch-ua-platform": HTTPHeaders.SEC_CH_UA_PLATFORM,
            }

        # 검색 유형에 따라 헤더 반환
        if search_type in ["cpu", "gpu", "ai"]:
            return common_headers
        else:
            raise ValueError("Invalid search type. Use 'cpu', 'gpu', or 'ai'.")

    @staticmethod
    def update_referer(new_referer: str) -> None:
        HTTPHeaders.REFERER = new_referer

    @staticmethod
    def update_cookie(new_cookie: str) -> None:
        HTTPHeaders.COOKIE = new_cookie

    @staticmethod
    def update_if_none_match(new_if_none_match: str) -> None:
        HTTPHeaders.IF_NONE_MATCH = new_if_none_match

if __name__ == "__main__":
    # 사용 예시
    headers_manager = HTTPHeaders()
    print("기본 Referer:", headers_manager.get_search_headers("cpu")["Referer"])  # 출력: ""

    # Referer 업데이트
    headers_manager.update_referer("https://example.com")
    print("업데이트된 Referer:", headers_manager.get_search_headers("cpu")["Referer"])  # 출력: https://example.com

