import requests
from bs4 import BeautifulSoup
import re

    
def is_last_page(content: str) -> bool:
    soup = BeautifulSoup(markup=content, features="lxml")
    
    # 마지막 페이지를 확인하기 위한 정규 표현식 패턴
    no_results_pattern = r"Your search did not match any .* results."
    
    # 텍스트에서 패턴이 발견되면 마지막 페이지로 간주
    return re.search(no_results_pattern, soup.get_text(strip=True)) is not None


def separate_device_and_cpu(text: str):
    # 정규 표현식을 사용하여 전체 문자열에서 모델 이름과 CPU 이름을 추출
    match = re.match(r"(.+?)\n\n(.+)", text.strip(), re.DOTALL)

    if match:
        device_info = match.group(1).strip()  # 모델 이름
        cpu_info = match.group(2).strip()      # CPU 이름

        return device_info, cpu_info
    else:
        raise ValueError("No match found for the given text.")


def fetch_total_pages_parser(content: str, default_pages: int) -> int:
    if content is not None:
        # BeautifulSoup 객체 생성
        soup = BeautifulSoup(markup=content, features="lxml")
        
        # 모든 페이지 항목에서 페이지 번호 추출
        page_numbers = [
            int(page.find(name="a", attrs={"class": "page-link"}).get_text(strip=True))
            for page in soup.find_all(name="li", attrs={"class": "page-item"})
            if page.find(name="a", attrs={"class": "page-link"}) and 
            page.find(name="a", attrs={"class": "page-link"}).get_text(strip=True).isdigit()
        ]
    
    else:
        page_numbers = []

    # 가장 큰 페이지 번호 반환, 페이지가 없으면 default_pages 값 반환
    return max(page_numbers, default=default_pages)