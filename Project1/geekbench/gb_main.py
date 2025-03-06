import asyncio

try:
    from http_client.http_requester import AsyncGeekBenchBrowserAPI
    from http_client.http_parser import GeekBenchSearchParser
    from http_client.http_json_parser import GeekBenchJSONParser
    from http_client.utils.date_utils import get_current_time, log_progress

except ImportError:
    from .http_client.http_requester import AsyncGeekBenchBrowserAPI
    from .http_client.http_parser import GeekBenchSearchParser
    from .http_client.http_json_parser import GeekBenchJSONParser
    from .http_client.utils.date_utils import get_current_time, log_progress



async def new_geekbench_data(
    search_type:str="cpu",
    query_data:list=[],
    start_page:int=1,
    last_page:int=99999,
    default_pages:int=99999,
    min_delay:int=0,
    max_delay:int=2,
    ):

    """
    주어진 쿼리 데이터에 대해 GeekBench API를 통해 데이터를 비동기적으로 요청합니다.
    기본적으로 이 함수는 query_data를 순회하여 각 쿼리를 개별적으로 처리합니다.

    새로운 데이터는 지정된 시작 페이지부터 마지막 페이지까지 수집되며,
    페이지 수에 따라 요청에 소요되는 시간이 달라질 수 있습니다.

    :param search_type: 검색할 데이터 유형 (예: 'cpu', 'gpu' 등)
    :param query_data: 검색할 쿼리 데이터 문자열 리스트
    :param start_page: 데이터 수집 시작 페이지 번호 (기본값: 1)
    :param last_page: 데이터 수집의 마지막 페이지 번호 (기본값: 99999). 실제 요청에 사용되는 값이며, 기본값 유지가 권장됩니다.        
    :param default_pages: 기본 페이지 수 (전체 페이지 수를 요청할 때 사용)
    :param min_delay: 요청 간 최소 지연 시간 (초) (기본값: 0)
    :param max_delay: 요청 간 최대 지연 시간 (초) (기본값: 2)
    :return: 없음
    """

    avg_delay = list() # 지연 시간 저장 리스트
    request_mode = "new mode" # 요청 모드

    # 긱벤치 데이터를 수집하는 API를 생성합니다.
    api_requester = AsyncGeekBenchBrowserAPI()

    # 긱벤치 JSON 데이터를 처리하는 Parser를 생성합니다.
    json_parser = GeekBenchJSONParser()


    for query in query_data:    
        # 파일 경로
        file_path = rf"geekbench_data_json\{query}_1.json"
        
        # 수집 페이지량 참고 및 표시 전용
        total_pages = await api_requester.fetch_total_pages(
            search_type=search_type,
            query=query,
            default_pages=default_pages,
            merge_mode=False,
            add_pages=5
            )
        
        # 요청자 및 로그 출력
        await _fetch_and_log_geekbench_data(
            request_mode=request_mode,
            api_requester=api_requester,
            json_parser=json_parser,
            query=query,
            search_type=search_type, 
            start_page=start_page, 
            last_page=last_page,
            total_pages=total_pages,
            min_delay=min_delay,
            max_delay=max_delay,
            avg_delay=avg_delay
            )
        
        # 데이터 저장
        json_parser.save_data_to_json(
            file_path=file_path,
            data=json_parser.fetch_geekbench_data()
            )
        
        print(f"{request_mode}: {file_path} 생성됨.\n")
        
        # 데이터 삭제
        json_parser.remove_geekbench_data()
        avg_delay.clear()


async def new_geekbench_data_concurrently(
    search_type:str="cpu",
    query_data:list=[],
    start_page:int=1,
    last_page:int=99999,
    default_pages:int=99999,
    min_delay:int=0,
    max_delay:int=2,
    ):

    """
    주어진 쿼리 리스트에 대해 데이터를 비동기적으로 수집합니다.
    asyncio.gather를 사용하여 여러 쿼리를 동시적으로 처리합니다.
    
    최대 세션 유지는 4개까지이며, 이는 query_data (list)의 개수를 의미합니다.

    :param search_type: 검색할 데이터 유형 (예: 'cpu', 'gpu' 등)
    :param queries: 검색할 쿼리 문자열 리스트의 리스트
    :param start_page: 데이터 수집 시작 페이지 번호
    :param last_page: 데이터 수집 마지막 페이지 번호 (실제 데이터 수집 작업에 사용되는 값)
    :param default_pages: 자동으로 가져와진 페이지 수가 0또는 오류난 경우 사용할 기본 페이지 수 (총 페이지 값 표시용)
    :param min_delay: 요청 간 최소 지연 시간 (초)
    :param max_delay: 요청 간 최대 지연 시간 (초)
    """

    if len(query_data) > 5:
        raise ValueError("비동기 최대 요청은 4개까지 가능합니다.")

    # 비동기적으로 모든 쿼리에 대해 데이터 수집
    tasks = [
        new_geekbench_data(
            query_data=query,
            search_type=search_type,
            start_page=start_page,
            last_page=last_page,
            default_pages=default_pages,
            min_delay=min_delay,
            max_delay=max_delay
        ) for query in query_data
    ]

    await asyncio.gather(*tasks)


async def merge_geekbench_data(
    search_type:str="cpu",
    query_data:list=[],
    start_page:int=1,
    default_pages:int=99999,
    min_delay:int=0.5,
    max_delay:int=3,
    add_pages:int=5
    ):

    """
    주어진 쿼리 데이터에 대해 GeekBench API를 통해 데이터를 비동기적으로 요청하고,
    기존 데이터에 새로운 데이터를 병합합니다.

    이 함수는 query_data를 순회하여 각 쿼리를 개별적으로 처리합니다.
    새로운 데이터가 업로드되면 기존 데이터를 재활용하여 수집 시간을 단축합니다.
    이를 통해 HTTP 요청을 최소화하고, 수집 시간 및 비용을 절감할 수 있습니다.

    새로운 데이터는 지정된 시작 페이지부터 마지막 페이지까지 수집되며,
    페이지 수에 따라 소요되는 시간이 달라질 수 있습니다.

    :param search_type: 검색할 데이터 유형 (예: 'cpu', 'gpu' 등)
    :param query_data: 검색할 쿼리 데이터 문자열 리스트 (기본값: None)
    :param start_page: 데이터 수집 시작 페이지 번호 (기본값: 1)
    :param default_pages: 자동으로 가져와진 페이지 수가 0또는 오류난 경우 사용할 기본 페이지 수
    :param min_delay: 요청 간 최소 지연 시간 (초) (기본값: 0.5)
    :param max_delay: 요청 간 최대 지연 시간 (초) (기본값: 3)
    :param add_pages: 추가 페이지 (페이지 값 보정에 사용되는 매개변수) (기본값: 5, 최소 기본값 또는 이상 값으로 권장)
    :return: 없음
    """

    avg_delay = list() # 지연 시간 저장 리스트
    request_mode = "merge mode" # 요청 모드

    # 긱벤치 데이터를 수집하는 API를 생성합니다.
    api_requester = AsyncGeekBenchBrowserAPI()

    # 긱벤치 JSON 데이터를 처리하는 Parser를 생성합니다.
    json_parser = GeekBenchJSONParser()

    for query in query_data:
        # 파일 경로
        file_path = rf"geekbench_data_json\{query}_1.json"

        # 합병 전용 ((전체 페이지 수 - 수집된 페이지 수) = 최적의 수집 페이지 수 계산
        total_pages = \
        await api_requester.fetch_total_pages(
            search_type=search_type,
            query=query,
            default_pages=default_pages,
            merge_mode=True,
            add_pages=add_pages

            ) - \
        json_parser.calculate_total_pages(
            file_path=file_path
            )
        
        # 요청자 및 로그 출력
        await _fetch_and_log_geekbench_data(
            request_mode=request_mode,
            api_requester=api_requester,
            json_parser=json_parser,
            query=query,
            search_type=search_type, 
            start_page=start_page, 
            last_page=None,
            total_pages=total_pages,
            min_delay=min_delay,
            max_delay=max_delay,
            avg_delay=avg_delay
            )

        # 수집된 데이터 및 기존 데이터 합병 및 추가 처리
        paginated_data = json_parser.merge_geekbench_data(
            new_data_path=json_parser.fetch_geekbench_data(),
            old_data_path=file_path, 
            )
        
        # 데이터 저장
        GeekBenchJSONParser.save_data_to_json(
            file_path=file_path,
            data=paginated_data
            )

        print(f"{request_mode}: {file_path} 병합됨.\n")
        
        # 데이터 삭제
        json_parser.remove_geekbench_data()
        avg_delay.clear()


async def _fetch_and_log_geekbench_data(
    request_mode: str,
    api_requester: object,
    json_parser: object,
    query: str,
    search_type: str,
    start_page: int,
    last_page: int,
    total_pages: int,
    min_delay: float,
    max_delay: float,
    avg_delay: float
    ) -> None:

    """
    주어진 쿼리와 검색 유형에 따라 GeekBench API에서 데이터를 비동기적으로 요청하고,
    수집된 데이터를 파싱하여 저장한 후, 검색 로그를 출력합니다.

    이 함수는 다음과 같은 정보를 로그로 기록합니다:
    - 시작 시간
    - query
    - 페이지
    - 랜덤 대기 시간
    - 경과 시간
    - 예상 남은 시간
    - 예상 완료 시간
    - ...
    - ...

    :param request_mode: 요청 모드
    :param api_requester: 비동기 HTTP 통신을 해서 웹-데이터를 가져옵니다.
    :param json_parser: json 포맷으로 수집한 데이터 정렬, 저장, 병합을 처리합니다.
    :param query: 검색할 쿼리 문자열
    :param search_type: 검색할 데이터 유형 (예: 'cpu', 'gpu' 등)
    :param start_page: 데이터 수집 시작 페이지 번호
    :param last_page: 데이터 수집 마지막 페이지 번호
    :param total_pages: 총 페이지 수
    :param min_delay: 요청 간 최소 지연 시간 (초)
    :param max_delay: 요청 간 최대 지연 시간 (초)
    :param avg_delay: 요청 간 지연 시간 저장 리스트 (초)
    """

    start_time = get_current_time()  # 시작 시간 기록
            
    print(query, ":", total_pages)

    async for result, current_page, current_last_page, random_sleep, in api_requester.search_client(
        search_type=search_type,
        query=query,
        start_page=start_page,
        last_page=total_pages if last_page is None else last_page,
        min_delay=min_delay,
        max_delay=max_delay
        ):

        for parsed_result in GeekBenchSearchParser.parse_search_benchmark(benchmark_type=search_type, content=result):
            json_parser.store_geekbench_data(query=query, page_number=current_page, parsed_data=parsed_result)

        # 진행 상황 로그
        log_progress(
            request_mode=request_mode,
            start_time=start_time,
            query=query,
            total_pages=total_pages,
            current_page=current_page,
            current_last_page=current_last_page,
            random_sleep=random_sleep,
            min_delay=min_delay,
            max_delay=max_delay,
            avg_delay=avg_delay
        )


# 사용 예시
if __name__ == "__main__":
    # 새로운 데이터 수집 (동시적 처리)
    concurrently_new_query_data = \
        [
            ["samsung exynos990"],
            ["samsung kona"],
        ]

    # asyncio.run(
    #     new_geekbench_data_concurrently(
    #         search_type="cpu",
    #         query_data=concurrently_new_query_data,
    #         start_page=1,
    #         last_page=99999,
    #         default_pages=99999,
    #         min_delay=1,
    #         max_delay=3
    #     )
    # )


    # 새로운 데이터 수집 (순차 처리)
    new_query_data = \
        [
            "samsung exynos990",
            "samsung kona"
        ]

    # asyncio.run(
    #     new_geekbench_data(
    #         search_type="cpu",
    #         query_data=new_query_data,
    #         start_page=1,
    #         last_page=99999,
    #         default_pages=99999,
    #         min_delay=0.5,
    #         max_delay=3
    #     )
    # )


    # 새로운 데이터 및 기존 데이터 병합 (순차 처리)
    merge_query_data = \
        [
            # 삼성 스냅드래곤 모델
            [
                "samsung sun",
                "samsung pineapple",
                "samsung kalama",
                "samsung taro",
                "samsung lahaina",
                "samsung kona",
                "samsung parrot",
            ],
            
            # 삼성 엑시노스 모델
            [
                "samsung s5e9945",
                "samsung s5e9925",
                "samsung exynos2100",
                "samsung s5e8855",
                "samsung s5e8835",
                "samsung exynos990",
                "samsung exynos980",

            ],

            # 아이폰 모델
            [
                "IPhone17",
                "IPhone16",
                "IPhone15",
                "IPhone14",
                "IPhone13",
                "IPhone12",
            ]
        ]

    for query_data in merge_query_data:
        asyncio.run(
            merge_geekbench_data(
                search_type="cpu",
                query_data=query_data,
                start_page=1,
                default_pages=99999,
                min_delay=0.5,
                max_delay=2,
                add_pages=5
            )
        )