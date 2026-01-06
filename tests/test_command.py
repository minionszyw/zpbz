import pytest
from src.engine.core import BaziEngine
from src.engine.models import BaziRequest, MonthMode

@pytest.fixture
def engine():
    return BaziEngine()

def test_month_command_switching(engine):
    """
    验证 1990 年正月 (寅月) 司令天干的随时间深度的精准切换
    1990年立春时刻: 2月4日 10:14:00
    分野规则: 戊(7), 丙(7), 甲(16)
    """
    
    # 1. 戊土司权期: 立春后 2 天 (2月6日)
    req_wu = BaziRequest(
        name="戊土司权",
        birth_datetime="1990-02-06 12:00:00",
        month_mode=MonthMode.SOLAR_TERM
    )
    res_wu = engine.arrange(req_wu)
    assert res_wu.month_command.current == "戊"
    assert "戊司权" in res_wu.month_command.detail

    # 2. 丙火司权期: 立春后 10 天 (2月14日)
    req_bing = BaziRequest(
        name="丙火司权",
        birth_datetime="1990-02-14 12:00:00",
        month_mode=MonthMode.SOLAR_TERM
    )
    res_bing = engine.arrange(req_bing)
    assert res_bing.month_command.current == "丙"
    assert "丙司权" in res_bing.month_command.detail

    # 3. 甲木司权期: 立春后 20 天 (2月24日)
    req_jia = BaziRequest(
        name="甲木司权",
        birth_datetime="1990-02-24 12:00:00",
        month_mode=MonthMode.SOLAR_TERM
    )
    res_jia = engine.arrange(req_jia)
    assert res_jia.month_command.current == "甲"
    assert "甲司权" in res_jia.month_command.detail

def test_command_induction(engine):
    """
    验证真气引出逻辑: 分野天干在原局天干透出
    案例: 1990-02-24 16:00 (甲申时)
    此时月令甲木司权，时干为甲，应触发引出。
    """
    req = BaziRequest(
        name="引出测试",
        birth_datetime="1990-02-24 16:00:00"
    )
    res = engine.arrange(req)
    
    # 确认八字: 庚午 戊寅 庚申 甲申 (时干透甲)
    assert res.core.time.gan == "甲"
    assert res.month_command.current == "甲"
    assert "真气引出" in res.month_command.detail
