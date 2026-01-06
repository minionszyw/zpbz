import pytest
from src.engine.core import BaziEngine
from src.engine.models import BaziRequest

@pytest.fixture
def engine():
    return BaziEngine()

def test_interaction_transformation_success(engine):
    """
    验证合化成功场景: 丁壬合化木
    案例: 1987-02-15 10:00 (丁卯年 壬寅月 乙亥日 辛巳时)
    """
    req = BaziRequest(
        name="合化成功测试",
        birth_datetime="1987-02-15 10:00:00"
    )
    res = engine.arrange(req)
    
    # 丁(年) 壬(月) 合
    combos = [i for i in res.interactions if i.type == "合"]
    assert len(combos) > 0
    
    target = next((c for c in combos if "丁壬" in c.desc or "壬丁" in c.desc), None)
    assert target is not None
    # 验证是否化木成功 (月令寅木支持)
    assert target.is_transformed is True

def test_interaction_transformation_fail(engine):
    """
    验证合而不化场景: 丙辛合，生于午月 (不助水)
    """
    req = BaziRequest(
        name="合化失败测试",
        birth_datetime="1991-06-25 12:00:00" # 辛未年 甲午月 丙寅日 甲午时
    )
    res = engine.arrange(req)
    
    # 辛(年) 丙(日) 合
    combos = [i for i in res.interactions if i.type == "合"]
    target = next((c for c in combos if "丙辛" in c.desc or "辛丙" in c.desc), None)
    
    assert target is not None
    # 应该是 False, 因为月令午火克金耗水，不支持化水
    assert target.is_transformed is False
