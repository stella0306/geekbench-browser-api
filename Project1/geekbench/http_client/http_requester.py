import aiohttp
from aiohttp import ClientSession
import asyncio
import time
import random
from urllib.parse import urlencode, urljoin
from functools import wraps

try:
    from http_url import HTTPUrl
    from http_headers import HTTPHeaders
    from utils.http_utils import is_last_page, fetch_total_pages_parser
    
except ImportError:
    from .http_url import HTTPUrl
    from .http_headers import HTTPHeaders
    from .utils.http_utils import is_last_page, fetch_total_pages_parser



class AsyncGeekBenchBrowserAPI:
    def __init__(self):
        """긱벤치 브라우저 API 초기화."""
        
        # 긱벤치 브라우저 URL 관리
        self.url_manager = HTTPUrl()
        
        # 긱벤치 브라우저 요청 headers 관리
        self.headers_manager = HTTPHeaders()

    @staticmethod
    async def _fetch(
        session: ClientSession,
        url: str, 
        payload:dict, 
        headers:dict
        ) -> str:
        
        async with session.get(url, params=payload, headers=headers) as response:
            # 응답 상태 코드 처리
            if response.status == 200:
                return await response.text(encoding="utf-8")  # 성공적으로 응답을 받은 경우
            
            # 재시도할 상태 코드 리스트
            retry_statuses = {429, 500, 503}
            
            if response.status in retry_statuses:
                print(f"Received {response.status} error, waiting for 5 seconds before retrying...")
                await asyncio.sleep(5)  # 재시도 전에 5초 대기
                return await AsyncGeekBenchBrowserAPI._fetch(session=session, url=url, payload=payload, headers=headers)  # 재귀적으로 요청 재시도
            
            # 기타 오류 상태에 대한 처리
            print(f"Error: Received status code {response.status} for URL: {url}")
            print(f"Error: Received status code {response.status} for PAYLOAD: {payload}")
            return None  # 오류 상태일 경우 None 반환



    def _get_search_url_and_payload(self, search_type: str, query: str, start_page: int):
        if search_type == "cpu":
            return self.url_manager.get_cpu_search_url(page=start_page, query=query)
        elif search_type == "gpu":
            return self.url_manager.get_gpu_search_url(page=start_page, query=query)
        elif search_type == "ai":
            return self.url_manager.get_ai_search_url(page=start_page, query=query)
        else:
            raise ValueError("Invalid search type. Use 'cpu', 'gpu', or 'ai'.")


    async def fetch_total_pages(self, search_type: str = None, query: str = None, default_pages: int = 0, merge_mode: bool = False, add_pages: int = 5) -> int:
        # URL 및 요청 payload 생성
        url, payload = self._get_search_url_and_payload(search_type=search_type, query=query, start_page=1)

        # Referer 헤더 업데이트
        self.headers_manager.update_referer(self.url_manager.BASE_URL)

        async with aiohttp.ClientSession() as session:
            # 현재 요청의 Referer 헤더 업데이트
            self.headers_manager.update_referer(url + "?" + urlencode(payload))

            # 비동기 요청 결과를 가져오기
            result = await AsyncGeekBenchBrowserAPI._fetch(
                session=session,
                url=url,
                payload=payload,
                headers=self.headers_manager.get_search_headers(search_type=search_type)
            )

            # 페이지 수를 파싱하고 보정하여 반환
            total_pages = fetch_total_pages_parser(content=result, default_pages=default_pages)
            
            # 병합 모드일 때만 보정
            if merge_mode:
                return total_pages + add_pages  # 보정을 위해 페이지 추가
            else:
                return total_pages  # 보정하지 않고 반환


    async def search_client(self, search_type:str, query: str, start_page: int = 1, last_page: int = 1, min_delay: int = 1, max_delay: int = 1):
        # URL 및 요청 payload 생성
        url, payload = self._get_search_url_and_payload(search_type=search_type, query=query, start_page=start_page)

        # Referer 헤더 업데이트
        self.headers_manager.update_referer(self.url_manager.BASE_URL)

        async with aiohttp.ClientSession() as session:
            for current_page in range(start_page, last_page + 1):
                # 현재 페이지에 대한 payload 및 headers 업데이트
                payload["page"] = current_page
                self.headers_manager.update_referer(url + "?" + urlencode(payload))

                # 비동기 요청 결과를 가져오기
                result = await AsyncGeekBenchBrowserAPI._fetch(
                    session=session,
                    url=url,
                    payload=payload,
                    headers=self.headers_manager.get_search_headers(search_type=search_type)
                )
                
                # 마지막 페이지 확인
                if is_last_page(content=result):
                    break
                
                # 랜덤 대기 시간 계산
                random_sleep = random.uniform(min_delay, max_delay)
                current_last_page = fetch_total_pages_parser(content=result, default_pages=-99999)

                yield result, current_page, current_last_page, random_sleep  # 결과 반환: 검색 결과, 현재 페이지, 현재 마지막 페이지 번호, 랜덤 대기 시간
                await asyncio.sleep(random_sleep)  # 랜덤 대기    