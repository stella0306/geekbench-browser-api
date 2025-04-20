from datetime import datetime, timedelta
import re
import numpy as np

def get_current_time() -> datetime:
    return datetime.now()  # 현재 시간을 반환

def format_datetime(original_datetime: str) -> str:
    # 문자열을 datetime 객체로 변환
    dt = datetime.strptime(str(original_datetime), "%Y-%m-%d %H:%M:%S.%f")
    
    # 알아보기 좋은 형식으로 변환
    formatted_datetime = dt.strftime("%Y년 %m월 %d일 %H시 %M분 %S초")
    
    return formatted_datetime

def convert_timedelta_to_dhms(total_seconds: int):
    td = timedelta(seconds=total_seconds)
    days = td.days
    seconds = td.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return days, hours, minutes, seconds

def log_progress(
    request_mode: str,
    start_time: datetime,
    query: str, 
    total_pages: int, 
    current_page: int,
    current_last_page: int,
    random_sleep: float, 
    min_delay: float, 
    max_delay: float, 
    avg_delay: float
    ) -> None:
    try:
        # 리스트 업데이트
        avg_delay.append(random_sleep)

        # 경과 시간 계산
        elapsed_time = (datetime.now() - start_time).total_seconds()
        # 남은 페이지 수
        remaining_requests = total_pages - current_page
        # 예상 남은 시간
        average_delay = np.mean(avg_delay)
        remaining_time = remaining_requests * average_delay  # 평균 대기 시간

        # 경과 시간 변환
        elapsed_days, elapsed_hours, elapsed_minutes, elapsed_seconds = convert_timedelta_to_dhms(total_seconds=elapsed_time)

        # 예상 남은 시간 변환
        remaining_days, remaining_hours, remaining_minutes, remaining_seconds = convert_timedelta_to_dhms(total_seconds=remaining_time)

        # 총 진행률 계산
        progress_percentage = (current_page / total_pages) * 100

        # 예상 완료 시간 계산
        estimated_completion_time = format_datetime(original_datetime=datetime.now() + timedelta(seconds=remaining_time))

        # 출력할 메시지를 딕셔너리에 저장
        messages = {
            "시작 시간": format_datetime(original_datetime=start_time),
            "Query": query,
            "현재 페이지": f"{current_page:,.0f} / 총 페이지: {total_pages:,.0f}, 진행률: {progress_percentage:,.2f}%",
            "현재 마지막 페이지": f"{current_last_page:,.0f}" if current_last_page != -99999 else "오류 발생",
            "병합 여부": "필요함 (긱벤치 데이터가 업데이트됨)" if total_pages != current_last_page else "필요 없음",
            "랜덤 대기(지연) 시간": f"{random_sleep:.2f}초, 평균 대기(지연) 시간: {average_delay:,.2f}초",
            "대기(지연) 시간 범위": f"{min_delay}초 to {max_delay}초",
            "경과 시간": f"{elapsed_days:,.0f}일 {elapsed_hours:,.0f}시간 {elapsed_minutes:,.0f}분 {elapsed_seconds:,.0f}초 ({elapsed_time:,.2f}초)",
            "예상 남은 시간": f"{remaining_days:,.0f}일 {remaining_hours:,.0f}시간 {remaining_minutes:,.0f}분 {remaining_seconds:,.0f}초 ({remaining_time:,.2f}초)",
            "예상 완료 시간": estimated_completion_time
        }

        # 병합 모드일때 특정 텍스트 제거
        if request_mode == "merge mode":
            messages.pop("병합 여부", None)

        # 메시지 출력
        for key, value in messages.items():
            print(f"{key}: {value}")
        print() # 줄바꿈
            
    except Exception as e:
        error = "Error occurred"
        print(f"{error}: {e}\n")

def parse_date_from_text(date_text: str) -> str:
    # 날짜 패턴을 사용하여 텍스트에서 날짜 추출
    try:
        # 정규 표현식을 사용하여 날짜 형식 매칭
        match = re.search(r'(\b\w{3} \d{1,2}, \d{4}\b)', date_text.strip())
        
        if match:  # 날짜 매칭이 성공할 경우
            extracted_date = match.group()
            # 문자열을 datetime 객체로 변환
            date_object = datetime.strptime(extracted_date, "%b %d, %Y")
            # ISO 형식으로 변환하여 반환
            return f"{date_object.year}-{date_object.month:02d}-{date_object.day:02d}"
        else:
            return None  # 매칭되지 않았을 경우 None 반환

    except ValueError:
        return None  # 날짜 구문 분석 실패 시 None 반환


def extract_date_components(date_text: str) -> dict:
    try:
        match = re.search(r'(\b\w{3} \d{1,2}, \d{4}\b)', date_text.strip())
        
        if match:
            extracted_date = match.group()
            date_object = datetime.strptime(extracted_date, "%b %d, %Y")
            return {
                "year": date_object.year,
                "month": date_object.month,
                "day": date_object.day
            }
        else:
            return None

    except ValueError:
        return None



if __name__ == "__main__":
    print(extract_date_components("Feb 17, 2025 toygoon"))