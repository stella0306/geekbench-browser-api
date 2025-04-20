from bs4 import BeautifulSoup

try:
    from utils.date_utils import parse_date_from_text, extract_date_components
    from utils.http_utils import separate_device_and_cpu
except ImportError:
    from .utils.date_utils import parse_date_from_text, extract_date_components
    from .utils.http_utils import separate_device_and_cpu


class GeekBenchSearchParser:
    @staticmethod
    def parse_search_benchmark(benchmark_type: str, content: str):
        # BeautifulSoup을 사용하여 HTML 파싱
        soup = BeautifulSoup(markup=content, features="lxml")

        # 벤치마크 결과 선택
        benchmark_results = GeekBenchSearchParser._get_benchmark_results(soup, benchmark_type)        

        for result in benchmark_results:
            yield GeekBenchSearchParser._extract_benchmark_data(result, benchmark_type)


    @staticmethod
    def _get_benchmark_results(soup, benchmark_type: str):
        # 벤치마크 결과 선택
        if benchmark_type in ["cpu", "gpu"]:
            return soup.select(selector="#wrap > div > div > div > div:nth-child(3) > div.col-12.col-lg-9 > div:nth-child(2) > div")
            
        elif benchmark_type == "ai":
            return soup.select(selector="#wrap > div > div > div > div:nth-child(3) > div.col-12.col-lg-9 > div.banff > div > div > table > tbody > tr")
            
        else:
            raise ValueError(f"Invalid benchmark_type: {benchmark_type}")  # 잘못된 benchmark_type에 대해 ValueError 발생



    @staticmethod
    def _extract_benchmark_data(result, benchmark_type: str):
        if benchmark_type in ["cpu", "gpu"]:
            return GeekBenchSearchParser._extract_cpu_gpu_data(result, benchmark_type)
        elif benchmark_type == "ai":
            return GeekBenchSearchParser._extract_ai_data(result)



    @staticmethod
    def _extract_cpu_gpu_data(result, benchmark_type: str):
        """CPU 및 GPU 데이터를 추출하는 헬퍼 함수"""
        device_name = result.select_one(selector="#wrap > div > div > div > div:nth-child(3) > div.col-12.col-lg-9 > div:nth-child(2) > div > div > div > div.col-12.col-lg-4 > a").get_text(strip=True)
        cpu_model = result.select_one(selector="#wrap > div > div > div > div:nth-child(3) > div.col-12.col-lg-9 > div:nth-child(2) > div > div > div > div.col-12.col-lg-4 > span.list-col-model").get_text(strip=False).replace("\n", " ").strip()
        upload_date = result.select_one(selector="#wrap > div > div > div > div:nth-child(3) > div.col-12.col-lg-9 > div:nth-child(2) > div > div > div > div:nth-child(2) > span.list-col-text").get_text(strip=False)
        platform_name = result.select_one(selector="#wrap > div > div > div > div:nth-child(3) > div.col-12.col-lg-9 > div:nth-child(2) > div > div > div > div:nth-child(3) > span.list-col-text").get_text(strip=True)
        result_url = "https://browser.geekbench.com" + result.select_one(selector="#wrap > div > div > div > div:nth-child(3) > div.col-12.col-lg-9 > div:nth-child(2) > div > div > div > div.col-12.col-lg-4 > a")["href"]
        
        # 벤치마크 유형에 따라 추가 데이터 추출
        core_scores = {}
        if benchmark_type == "cpu":           
            core_scores["single"] = int(result.select_one(selector="#wrap > div > div > div > div:nth-child(3) > div.col-12.col-lg-9 > div:nth-child(2) > div > div > div > div:nth-child(4) > span.list-col-text-score").get_text(strip=True))
            core_scores["multi"] = int(result.select_one(selector="#wrap > div > div > div > div:nth-child(3) > div.col-12.col-lg-9 > div:nth-child(2) > div > div > div > div:nth-child(5) > span.list-col-text-score").get_text(strip=True))

        elif benchmark_type == "gpu":
            core_scores["api_name"] = result.select_one(selector="#wrap > div > div > div > div:nth-child(3) > div.col-12.col-lg-9 > div:nth-child(2) > div > div > div > div:nth-child(4) > span.list-col-text").get_text(strip=True)
            core_scores["api_score"] = int(result.select_one(selector="#wrap > div > div > div > div:nth-child(3) > div.col-12.col-lg-9 > div:nth-child(2) > div > div > div > div:nth-child(5) > span.list-col-text-score").get_text(strip=True))

        # 날짜 정보를 추출
        upload_date_components = extract_date_components(upload_date)

        # 결과를 딕셔너리로 반환
        return {
            result_url: {  # URL을 키로 사용하여 결과를 저장
                "system": {
                    "device_name": device_name,
                    "cpu_model": cpu_model,
                },
                "upload_date": {
                    "default": str(upload_date).strip(),  # 원본 날짜 문자열
                    "parsed": parse_date_from_text(upload_date),  # ISO 형식으로 변환된 날짜
                    "year": upload_date_components.get("year"),  # 추출된 년도
                    "month": upload_date_components.get("month"),  # 추출된 월
                    "day": upload_date_components.get("day")  # 추출된 일
                },
                "platform": platform_name,  # 플랫폼 이름
                "core_scores": core_scores
            }
        }


    @staticmethod
    def _extract_ai_data(result):
        device_name_and_cpu_model = result.select_one(selector="#wrap > div > div > div > div:nth-child(3) > div.col-12.col-lg-9 > div.banff > div > div > table > tbody > tr > td.device > a").get_text(strip=False)
        device_name, cpu_model = separate_device_and_cpu(device_name_and_cpu_model)
        framework_name = result.select_one(selector="#wrap > div > div > div > div:nth-child(3) > div.col-12.col-lg-9 > div.banff > div > div > table > tbody > tr > td.framework").get_text(strip=True)
        single_precision = result.select_one(selector="#wrap > div > div > div > div:nth-child(3) > div.col-12.col-lg-9 > div.banff > div > div > table > tbody > tr > td:nth-child(3)").get_text(strip=True)
        half_precision = result.select_one(selector="#wrap > div > div > div > div:nth-child(3) > div.col-12.col-lg-9 > div.banff > div > div > table > tbody > tr > td:nth-child(4)").get_text(strip=True)
        quantized = result.select_one(selector="#wrap > div > div > div > div:nth-child(3) > div.col-12.col-lg-9 > div.banff > div > div > table > tbody > tr > td:nth-child(5)").get_text(strip=True)
        result_url = "https://browser.geekbench.com" + result.select_one(selector="#wrap > div > div > div > div:nth-child(3) > div.col-12.col-lg-9 > div.banff > div > div > table > tbody > tr > td.device > a")["href"]
        
        core_scores = {
            "single_precision": int(single_precision),
            "half_precision": int(half_precision),  
            "quantized": int(quantized)
        }

        # 결과를 딕셔너리로 반환
        return {
            result_url: {  # URL을 키로 사용하여 결과를 저장
                "system": {
                    "device_name": device_name,
                    "cpu_model": cpu_model,
                },
                "framework_name": framework_name,
                "core_scores": core_scores
            }
        }