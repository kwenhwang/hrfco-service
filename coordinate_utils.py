def dms_to_decimal(dms_str: str) -> float:
    """도-분-초를 십진도로 변환"""
    try:
        parts = dms_str.strip().split('-')
        degrees = float(parts[0])
        minutes = float(parts[1])
        seconds = float(parts[2])
        return degrees + minutes/60 + seconds/3600
    except:
        return 0.0

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """두 좌표 간 거리 계산 (km)"""
    import math
    
    R = 6371  # 지구 반지름 (km)
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c
