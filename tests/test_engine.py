import json
from src.engine.core import BaziEngine
from src.engine.models import BaziRequest, CalendarType

def test_engine_smoke():
    engine = BaziEngine()
    req = BaziRequest(
        name="张三",
        birth_datetime="1990-01-01 12:00:00",
        calendar_type=CalendarType.SOLAR,
        birth_location="北京"
    )
    
    result = engine.arrange(req)
    
    # 验证数据结构完整性
    assert result.request.name == "张三"
    assert result.core.year.gan == "己"
    assert len(result.fortune.da_yun) > 0
    assert result.auxiliary.tai_yuan != ""
    
    # 验证序列化
    json_str = result.model_dump_json()
    data = json.loads(json_str)
    assert data["request"]["name"] == "张三"
    assert "core" in data
    assert "fortune" in data
    assert "auxiliary" in data
