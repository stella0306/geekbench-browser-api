import json
import os
from pprint import pprint

class GeekBenchJSONParser:
    def __init__(self):
        """초기화 메서드입니다."""
        self.geekbench_data = dict() # GeekBench 데이터를 저장할 딕셔너리

    @staticmethod
    def save_data_to_json(file_path: str, data: dict):
        """
        주어진 데이터를 JSON (dict) 파일로 저장하는 함수.

        :param file_path: 저장할 JSON 파일의 경로
        :param data: 저장할 데이터 (딕셔너리 형식)
        """
        # 디렉토리가 존재하지 않으면 생성
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)

    @staticmethod
    def load_data_to_json(file_path: str) -> dict:
        """
        지정된 파일 경로에서 JSON (dict) 데이터를 로드합니다.

        :param file_path: str - 로드할 JSON 파일의 경로
        :return: dict - 파일에서 로드한 JSON 데이터, 파일이 존재하지 않으면 빈 딕셔너리 반환
        
        이 함수는 주어진 파일 경로에서 JSON 형식의 데이터를 읽어들여
        딕셔너리로 변환하여 반환합니다. 파일이 존재하지 않을 경우,
        빈 딕셔너리를 반환합니다.
        """
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as json_file:
                return json.load(json_file)
        return dict()


    def store_geekbench_data(self, query: str, page_number: int, parsed_data: dict):
        """
        주어진 query와 페이지 번호에 대한 GeekBench 데이터를 딕셔너리에 저장합니다.

        :param query: 기기 ID (예: 'SM-S928N')
        :param page_number: 페이지 번호 (정수)
        :param parsed_data: 저장할 데이터 (딕셔너리 형식)
        """
        # query에 대한 데이터 구조 생성
        if query not in self.geekbench_data:
            self.geekbench_data[query] = dict()

        # 페이지 번호에 대한 데이터 구조 생성
        page_key = str(page_number)
        if page_key not in self.geekbench_data[query]:
            self.geekbench_data[query][page_key] = dict()

        # parsed_data의 키를 사용하여 데이터 저장
        for url, details in parsed_data.items():
            # URL이 이미 존재하는지 확인
            if url not in self.geekbench_data[query][page_key]:
                self.geekbench_data[query][page_key][url] = details
                

    def fetch_geekbench_data(self) -> dict:
        """
        저장된 딕셔너리에서 URL의 고유 번호 기준으로 내림차순 정렬한 후, 페이지네이션 처리하여 반환합니다.

        :return: dict - 정렬된 페이지네이션 처리된 GeekBench 데이터
        
        이 함수는 저장된 GeekBench 딕셔너리 데이터를 가져와,
        URL의 고유 번호 기준으로 내림차순 정렬한 후, 페이지네이션을 적용합니다.
        """
        return self._sort_and_paginate_urls_by_unique_id_descending(data=self.geekbench_data)
    
    
    def remove_geekbench_data(self) -> None:
        """저장된 GeekBench 딕셔너리 데이터를 삭제합니다."""
        self.geekbench_data.clear()


    def _sort_and_paginate_urls_by_unique_id_descending(self, data: dict = None) -> dict:
        """
        주어진 딕셔너리에서 URL의 고유 번호 기준으로 내림차순 정렬한 후, 페이지네이션 처리합니다.

        :param data: dict - URL과 관련된 데이터를 포함하는 딕셔너리
        :return: dict - 페이지네이션 처리된 정렬된 데이터
        
        이 함수는 긱벤치 데이터의 정렬 오류, 버그, 데이터 중복 등을 방지하기 위해
        URL의 고유 번호를 기준으로 내림차순으로 재정렬 및 페이지네이션 처리합니다.
        """
        
        merge_data = dict()
        self._add_source_data_to_merge(merge_data=merge_data, source_data=data)
        # 수정 후, merge_data는 이제 수정된 딕셔너리입니다.
        paginated_data = self._paginate_data(data=self._sort_urls_by_unique_id(merge_data=merge_data))

        return paginated_data


    def merge_geekbench_data(self, new_data_path: dict | str = None, old_data_path: dict | str = None):
        """
        기존 데이터와 새로운 데이터를 합쳐서 페이지 구조로 저장된 딕셔너리를 반환합니다.
        25개의 항목마다 페이지 번호를 증가시킵니다.
        딕셔너리 특성상 데이터의 중복을 제거합니다.

        :param new_data_path: 새로운 데이터 (딕셔너리 형식 또는 파일 경로)
        :param old_data_path: 기존 데이터 (딕셔너리 형식 또는 파일 경로)
        """
        # 새로운 데이터 로드
        if isinstance(new_data_path, dict):
            new_data = new_data_path
        elif isinstance(new_data_path, str):
            new_data = GeekBenchJSONParser.load_data_to_json(new_data_path)
            if new_data is None:
                raise ValueError("New data is None. Failed to load data from the provided path.")
        else:
            raise ValueError("New data must be provided as a dictionary or a valid file path.")

        # 기존 데이터 로드
        if isinstance(old_data_path, dict):
            old_data = old_data_path
        elif isinstance(old_data_path, str):
            old_data = GeekBenchJSONParser.load_data_to_json(old_data_path)
            if old_data is None:  # 수정된 부분
                raise ValueError("Old data is None. Failed to load data from the provided path.")
        else:
            raise ValueError("Old data must be provided as a dictionary or a valid file path.")

        load_merge_data = self._load_merge_data(new_data=new_data, old_data=old_data)
        paginated_data = self._paginate_data(data=self._sort_urls_by_unique_id(merge_data=load_merge_data))

        return paginated_data
    
    def _load_merge_data(self, new_data: dict, old_data: dict) -> dict:
        """
        새로운 데이터와 기존 데이터를 로드하여 합칩니다.

        :param new_data: dict - 새로운 데이터 (쿼리를 키로 하고 결과를 값으로 가지는 딕셔너리)
        :param old_data: dict - 기존 데이터 (쿼리를 키로 하고 결과를 값으로 가지는 딕셔너리)
        :return: dict - 합쳐진 데이터
        """
        
        merge_data = dict()

        # 새로운 데이터와 기존 데이터를 합치는 함수 호출
        self._add_source_data_to_merge(merge_data, new_data)
        self._add_source_data_to_merge(merge_data, old_data)

        return merge_data

    def _add_source_data_to_merge(self, merge_data: dict, source_data: dict):
        """
        주어진 소스 데이터를 합쳐진 데이터에 추가합니다.

        :param merge_data: dict - 합쳐진 데이터 (쿼리를 키로 가지는 딕셔너리)
        :param source_data: dict - 추가할 데이터 (쿼리를 키로 가지는 딕셔너리)
        """
        
        for query, query_data in source_data.items():
            if query not in merge_data:
                merge_data[query] = dict()

            for _, results in query_data.items():
                for url, result_details in results.items():
                    merge_data[query][url] = result_details


    def _sort_urls_by_unique_id(self, merge_data: dict = None) -> dict:
        """
        주어진 딕셔너리에서 URL의 고유 번호 기준으로 내림차순으로 정렬합니다.

        :param merge_data: dict - 쿼리를 키로 하고 URL과 결과를 값으로 가지는 딕셔너리
        :return: dict - URL이 고유 번호 기준으로 내림차순으로 정렬된 딕셔너리      
        """
        
        # 각 쿼리에 대해 URL의 고유 번호 기준으로 내림차순 정렬
        for query in merge_data.keys():
            merge_data[query] = dict(sorted(
                merge_data[query].items(),
                key=lambda item: int(item[0].split('/')[-1]),  # URL에서 고유 번호 추출
                reverse=True  # 내림차순으로 정렬
            ))

        return merge_data

    def _paginate_data(self, data: dict) -> dict:
        """
        데이터를 페이지 구조로 변환합니다.

        :param data: 합쳐진 데이터
        :return: 페이지 구조로 변환된 데이터
        """
        paginated_data = dict()
        page_number = 0
        item_count = 0  # 항목 카운트 초기화
            
        for query, results in data.items():
            if query not in paginated_data:
                paginated_data[query] = dict()

            for result_url, result_details in results.items():
                # 25개마다 페이지 번호 증가
                if item_count % 25 == 0:
                    page_number += 1

                # 항목 카운트 증가
                item_count += 1
                
                # 페이지 번호에 데이터 저장
                if page_number not in paginated_data[query]:
                    paginated_data[query][page_number] = dict()

                # 데이터 추가
                paginated_data[query][page_number][result_url] = result_details

        return paginated_data


    def cpu_fix(self, file_path: str, save_file_path: str, cpu_model_mapping: dict):
        """
        CPU 모델 이름을 수정하고 수정된 데이터를 새로운 JSON 파일로 저장합니다.

        Parameters:
        :file_path (str): 수정할 JSON 파일의 경로
        :save_file_path (str): 수정된 데이터를 저장할 JSON 파일의 경로
        :cpu_model_mapping (dict): 수정할 CPU 모델 이름과 수정된 모델 이름의 매핑
        """
        # 데이터 로드
        query_results = GeekBenchJSONParser.load_data_to_json(file_path)

        # CPU 데이터 수정
        for key, results in query_results.items():
            for page_number, page_data in results.items():
                for url, entry_data in page_data.items():
                    # 원래 CPU 모델 이름
                    original_model = entry_data["system"]["cpu_model"]

                    # CPU 모델 수정
                    fixed_model = original_model
                    for old_model in cpu_model_mapping.keys():
                        # get()을 사용하여 새로운 모델 이름을 가져옴
                        new_model = cpu_model_mapping.get(old_model)
                        fixed_model = fixed_model.replace(old_model, new_model)

                    # 수정된 모델을 데이터에 반영
                    entry_data["system"]["cpu_model"] = fixed_model
                    print(f"Original: {original_model} -> Fixed: {fixed_model}")

        # 수정된 데이터 저장
        GeekBenchJSONParser.save_data_to_json(file_path=save_file_path, data=query_results)
        print(f"Modified data saved to: {save_file_path}")


    def calculate_total_pages(self, file_path: str):
        """
        주어진 JSON 파일에서 페이지 수를 계산합니다.

        Parameters:
        file_path (str): JSON 파일의 경로

        Returns:
        int: 총 페이지 수
        """
        # 데이터 로드
        query_results = GeekBenchJSONParser.load_data_to_json(file_path=file_path)

        # 페이지 개수 구하기
        total_pages = sum(len(results) for results in query_results.values())

        return total_pages


if __name__ == "__main__":
    json_parser_manager = GeekBenchJSONParser()
    # json_parser_manager.merge_and_save_geekbench_data()
    data = json_parser_manager.merge_geekbench_data(new_data_path=r"geekbench_data_json\samsung s5e9945_1.json", old_data_path=r"geekbench_data_json\samsung s5e9945_1.json")
    GeekBenchJSONParser.save_data_to_json(file_path=r"geekbench_data_json\samsung s5e9945_test_1.json", data=data)
    
    # 파일 경로 설정
    # input_path = r"geekbench_data_json\samsung sun_1.json"
    # output_path = r"geekbench_data_json\samsung sun_1.json"
    
    # CPU 모델 매핑 설정
    # cpu_model_mapping = {
    #     "Qualcomm ARMv83532 MHz(8 cores)": "Qualcomm ARMv8 3532 MHz (8 cores)",
    #     "Qualcomm ARMv82899 MHz(8 cores)": "Qualcomm ARMv8 2899 MHz (8 cores)"
    # }
    
    # # CPU 수정 실행
    # json_parser_manager.cpu_fix(input_path, output_path, cpu_model_mapping)
    
    # json_parser_manager.calculate_total_pages(file_path=input_path)