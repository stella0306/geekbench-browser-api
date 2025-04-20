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