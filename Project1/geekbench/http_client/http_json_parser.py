import json
import os
from pprint import pprint

class GeekBenchJSONParser:
    def __init__(self):
        self.geekbench_data = dict() # GeekBench 데이터를 저장할 딕셔너리

    @staticmethod
    def save_data_to_json(file_path: str, data: dict):
        # 디렉토리가 존재하지 않으면 생성
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)

    @staticmethod
    def load_data_to_json(file_path: str) -> dict:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as json_file:
                return json.load(json_file)
        return dict()


    def store_geekbench_data(self, query: str, page_number: int, parsed_data: dict):
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
        return self._sort_and_paginate_urls_by_unique_id_descending(data=self.geekbench_data)
    
    
    def remove_geekbench_data(self) -> None:
        """저장된 GeekBench 딕셔너리 데이터를 삭제합니다."""
        self.geekbench_data.clear()


    def _sort_and_paginate_urls_by_unique_id_descending(self, data: dict = None) -> dict:
        merge_data = dict()
        self._add_source_data_to_merge(merge_data=merge_data, source_data=data)
        # 수정 후, merge_data는 이제 수정된 딕셔너리입니다.
        paginated_data = self._paginate_data(data=self._sort_urls_by_unique_id(merge_data=merge_data))

        return paginated_data


    def merge_geekbench_data(self, new_data_path: dict | str = None, old_data_path: dict | str = None):
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
        merge_data = dict()

        # 새로운 데이터와 기존 데이터를 합치는 함수 호출
        self._add_source_data_to_merge(merge_data, new_data)
        self._add_source_data_to_merge(merge_data, old_data)

        return merge_data

    def _add_source_data_to_merge(self, merge_data: dict, source_data: dict):
        for query, query_data in source_data.items():
            if query not in merge_data:
                merge_data[query] = dict()

            for _, results in query_data.items():
                for url, result_details in results.items():
                    merge_data[query][url] = result_details


    def _sort_urls_by_unique_id(self, merge_data: dict = None) -> dict:
        # 각 쿼리에 대해 URL의 고유 번호 기준으로 내림차순 정렬
        for query in merge_data.keys():
            merge_data[query] = dict(sorted(
                merge_data[query].items(),
                key=lambda item: int(item[0].split('/')[-1]),  # URL에서 고유 번호 추출
                reverse=True  # 내림차순으로 정렬
            ))

        return merge_data

    def _paginate_data(self, data: dict) -> dict:
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