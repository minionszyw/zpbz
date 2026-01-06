import pytest
from src.engine.models import BaziRequest, Gender, CalendarType
from src.engine.config import BaziConfig
import os
import json

def test_bazi_request_validation():
    # 合法请求
    req = BaziRequest(
        name="测试",
        birth_datetime="1990-01-01 12:00:00"
    )
    assert req.gender == Gender.MALE
    
    # 非法日期格式
    with pytest.raises(ValueError):
        BaziRequest(name="错误", birth_datetime="1990/01/01")

def test_config_longitude():
    # 创建临时测试配置
    test_json = "test_latlng.json"
    with open(test_json, "w") as f:
        json.dump({"杭州": 120.15}, f)
    
    cfg = BaziConfig(test_json)
    assert cfg.get_longitude("杭州") == 120.15
    assert cfg.get_longitude("未知") == 120.0
    
    os.remove(test_json)
