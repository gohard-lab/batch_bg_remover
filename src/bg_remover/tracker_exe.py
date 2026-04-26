import requests
import platform
import json
import uuid
import sys
import os
from supabase import create_client
from datetime import datetime, timezone
from dotenv import load_dotenv

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

load_dotenv(resource_path('.env'))

def get_real_client_ip():
    """Fetches the real public IP address of the client in a desktop (.exe) environment."""
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=3)
        return response.json().get('ip')
    except Exception:
        return None

def get_location_data():
    """Fetches location data based on the real IP."""
    real_ip = get_real_client_ip()
    
    if not real_ip:
        return {} # 💡 None 대신 빈 딕셔너리 반환으로 하단 에러 방지

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
    
    return {} # 💡 예외 발생 시에도 빈 딕셔너리 반환

def get_supabase_client():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        return None
    
    return create_client(url, key)

def get_or_create_machine_id():
    """Retrieves or generates a unique machine ID and stores it locally."""
    id_file = os.path.join(os.path.expanduser("~"), ".magic_tracker_id.json")
    
    if os.path.exists(id_file):
        try:
            with open(id_file, "r") as f:
                return json.load(f).get("machine_id")
        except:
            pass
            
    new_id = uuid.uuid4().hex
    try:
        with open(id_file, "w") as f:
            json.dump({"machine_id": new_id}, f)
    except:
        pass
    return new_id

def log_app_usage(app_name="unknown_exe_app", action="app_executed", details=None):
    """Logs app usage to Supabase."""
    try:
        os_info = f"{platform.system()} {platform.release()} ({platform.machine()})"
        user_agent = f"Desktop EXE / {os_info}"
    except Exception:
        user_agent = "Unknown Desktop"

    try:
        ip_address = requests.get('https://api.ipify.org', timeout=3).text
    except Exception:
        ip_address = "Offline or Blocked"

    loc_data = get_location_data()
    
    try:
        client = get_supabase_client()
        if not client:
            return False
            
        machine_id = get_or_create_machine_id()

        # 💡 [핵심 수정] 타임존 이중 계산 방지를 위해 명시적인 UTC 시간(ISO 포맷) 사용
        utc_time = datetime.now(timezone.utc).isoformat()
        
        log_data = {
            "session_id": machine_id, 
            "app_name": app_name,
            "action": action,
            "timestamp": utc_time, # 💡 UTC 시간 전송 (Supabase가 알아서 KST로 변환해 줌)
            "country": loc_data.get('country', "Unknown"),
            "region": loc_data.get('region', "Unknown"),
            "city": loc_data.get('city', "Unknown"),
            "lat": loc_data.get('lat', 0.0),
            "lon": loc_data.get('lon', 0.0),
            "details": details if details else {},
            "user_agent": user_agent,
            "ip_address": ip_address
        }
        
        client.table('usage_logs').insert(log_data, returning='minimal').execute()
        return True
    except Exception as e:
        print(f"Tracker Error: {e}")
        return False