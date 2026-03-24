import requests
import platform
import json
import uuid
import os
from supabase import create_client
from datetime import datetime, timezone, timedelta

def get_real_client_ip():
    """데스크톱(.exe) 환경에서는 파이썬이 직접 공인 IP를 조회합니다."""
    try:
        # 프록시 서버가 없으므로 가장 단순하고 확실한 방법으로 내 공인 IP를 가져옵니다.
        response = requests.get('https://api.ipify.org?format=json', timeout=3)
        return response.json().get('ip')
    except Exception:
        return None

def get_location_data():
    """실제 IP를 기반으로 위치 정보를 가져옵니다."""
    real_ip = get_real_client_ip()
    
    if not real_ip:
        return None 

    url = f"http://ip-api.com/json/{real_ip}?fields=status,country,regionName,city,lat,lon"
    try:
        response = requests.get(url, timeout=3)
        data = response.json()
        if data.get('status') == 'success':
            return {
                'country': data.get('country'),
                'region': data.get('regionName'),
                'city': data.get('city'),
                'lat': data.get('lat'),
                'lon': data.get('lon')
            }
    except Exception:
        pass
    return None

def get_supabase_client():
    # 사용하시는 Supabase URL과 Key를 그대로 넣으시면 됩니다.
    url = "https://gkzbiacodysnrzbpvavm.supabase.co"
    key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdremJpYWNvZHlzbnJ6YnB2YXZtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM1NzE2MTgsImV4cCI6MjA4OTE0NzYxOH0.Lv5uVeNZOyo21tgyl2jjGcESoLl_iQTJYp4jdCwuYDU"

    return create_client(url, key)

# 1. 💡 PC 고유 ID를 발급/저장/조회하는 함수 추가
def get_or_create_machine_id():
    # 내문서/홈 폴더에 숨김 파일로 저장할 경로 지정
    id_file = os.path.join(os.path.expanduser("~"), ".magic_tracker_id.json")
    
    # 이미 쪽지가 있으면 읽어서 반환
    if os.path.exists(id_file):
        try:
            with open(id_file, "r") as f:
                return json.load(f).get("machine_id")
        except:
            pass
            
    # 쪽지가 없으면 새로 만들어서 저장
    new_id = uuid.uuid4().hex
    try:
        with open(id_file, "w") as f:
            json.dump({"machine_id": new_id}, f)
    except:
        pass
    return new_id

def log_app_usage(app_name="unknown_exe_app", action="app_executed", details=None):
    
    # --- [EXE 전용] PC 정보와 진짜 공인 IP 추출 ---
    try:
        # 1. 기기 정보 (예: Windows 10 (AMD64))
        # 브라우저 대신, 이 프로그램을 실행한 진짜 PC의 윈도우 OS 정보를 캐냅니다.
        os_info = f"{platform.system()} {platform.release()} ({platform.machine()})"
        user_agent = f"Desktop EXE / {os_info}"
    except Exception as e:
        user_agent = "Unknown Desktop"

    try:
        # 2. 공인 IP 추출 (외부 무료 API 활용)
        # EXE는 로컬에서 돌기 때문에, 인터넷 우체국에 "내 진짜 겉면 주소가 뭐야?"라고 물어봐야 합니다.
        # api.ipify.org는 전 세계 개발자들이 가장 많이 쓰는 빠르고 안전한 IP 확인소입니다.
        ip_address = requests.get('https://api.ipify.org', timeout=3).text
    except Exception as e:
        # 오프라인이거나 방화벽에 막혔을 경우
        ip_address = "Offline or Blocked"
    # -------------------------------------------------------------

    """Supabase에 .exe 프로그램 실행 기록을 남깁니다."""
    loc_data = get_location_data()
    
    try:
        client = get_supabase_client()
        if not client:
            return False
            
        # PC 고유 ID 가져오기
        machine_id = get_or_create_machine_id()

        kst = timezone(timedelta(hours=9))
        korea_time = datetime.now(kst).strftime("%Y-%m-%d %H:%M:%S")
        
        log_data = {
            "session_id": machine_id, # EXE 사용자들도 평생 고유 ID가 생김!
            "app_name": app_name,
            "action": action,
            "timestamp": korea_time, 
            "country": loc_data['country'] if loc_data else "Unknown",
            "region": loc_data['region'] if loc_data else "Unknown",
            "city": loc_data['city'] if loc_data else "Unknown",
            "lat": loc_data['lat'] if loc_data else 0.0,
            "lon": loc_data['lon'] if loc_data else 0.0,
            "details" : details,
            "user_agent": user_agent,  # EXE용 PC 정보가 들어갑니다
            "ip_address": ip_address   # EXE가 실행된 진짜 공인 IP가 들어갑니다
        }
        
        client.table('usage_logs').insert(log_data, returning='minimal').execute()
        return True
    except Exception:
        return False