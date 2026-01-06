import pytest
from src.engine.core import BaziEngine
from src.engine.models import BaziRequest

@pytest.fixture
def engine():
    return BaziEngine()

def test_geju_inner_eight_logic(engine):
    """
    验证正八格判定逻辑: 月令透干优先
    案例: 1990-05-20 12:00 (庚午年 辛巳月 乙酉日 壬午时)
    月令巳火，藏丙庚戊。天干透出庚(年干)，庚为乙之正官。
    预期: 正官格
    """
    req = BaziRequest(
        name="正官格测试",
        birth_datetime="1990-05-20 12:00:00"
    )
    res = engine.arrange(req)
    
    assert "正官" in res.geju.name
    assert res.geju.status == "成格"

def test_geju_main_air_logic(engine):
    """
    验证无透干时取本气逻辑
    案例: 1990-01-01 12:00 (己巳年 丙子月 丙寅日 甲午时)
    月令子水，藏癸水。天干无壬癸透出。
    预期: 正官格 (癸水为丙火之正官)
    """
    req = BaziRequest(
        name="本气格测试",
        birth_datetime="1990-01-01 12:00:00"
    )
    res = engine.arrange(req)
    
    # 子月藏癸水，对丙火而言是正官
    assert "正官" in res.geju.name
