import pytest
import json
from src.engine.core import BaziEngine
from src.engine.models import BaziRequest, Gender, CalendarType, TimeMode, MonthMode, ZiShiMode

@pytest.fixture
def engine():
    return BaziEngine()

def test_full_parameter_combinations(engine):
    """
    全参数集成测试：覆盖所有输入参数及其核心逻辑分支
    """
    
    # 场景 1: 基础公历 + 平太阳时 + 晚子时不换日
    req1 = BaziRequest(
        name="测试1",
        gender=Gender.MALE,
        calendar_type=CalendarType.SOLAR,
        birth_datetime="1990-01-01 12:00:00",
        birth_location="北京",
        time_mode=TimeMode.MEAN_SOLAR,
        month_mode=MonthMode.SOLAR_TERM,
        zi_shi_mode=ZiShiMode.LATE_ZI_IN_DAY
    )
    res1 = engine.arrange(req1)
    assert res1.core.day.gan == "丙" # 1990-01-01 是丙寅日
    assert res1.core.time.gan == "甲" # 12:00 是甲午时
    
    # 场景 2: 夏令时修正 (1988年夏令时期间)
    # 1988-05-20 12:00:00 (夏令时) -> 实际应为 11:00:00 (平太阳时)
    req2 = BaziRequest(
        name="夏令时测试",
        gender=Gender.FEMALE,
        calendar_type=CalendarType.SOLAR,
        birth_datetime="1988-05-20 12:00:00",
        birth_location="北京",
        time_mode=TimeMode.MEAN_SOLAR
    )
    res2 = engine.arrange(req2)
    # 11:00 应该是午时 (11:00-13:00) 的开始，或者是巳时的结束？ 
    # 11:00 正好是午时的起点。
    assert res2.core.time.zhi == "午" 

    # 场景 3: 真太阳时修正 (成都经度偏移)
    # 成都 104.06, 12:00 北京时间 -> 约 10:56 真太阳时
    req3 = BaziRequest(
        name="真太阳时测试",
        birth_location="成都",
        birth_datetime="1990-01-01 12:00:00",
        time_mode=TimeMode.TRUE_SOLAR
    )
    res3 = engine.arrange(req3)
    assert res3.core.time.zhi == "巳" # 10:56 属于巳时 (9-11)

    # 场景 4: 农历输入转换
    # 农历 1990-01-05 12:00 -> 公历 1990-01-31 12:00
    req4 = BaziRequest(
        name="农历测试",
        calendar_type=CalendarType.LUNAR,
        birth_datetime="1990-01-05 12:00:00"
    )
    res4 = engine.arrange(req4)
    assert res4.core.day.gan == "丙" # 1990-01-31 是丙寅日

    # 场景 5: 子时换日模式 (Sect 1)
    req5 = BaziRequest(
        name="换日测试",
        birth_datetime="1990-01-01 23:30:00",
        zi_shi_mode=ZiShiMode.NEXT_DAY,
        time_mode=TimeMode.MEAN_SOLAR # 确保不使用真太阳时
    )
    res5 = engine.arrange(req5)
    assert res5.core.day.gan == "丁"
    assert res5.core.day.zhi == "卯"

    # 场景 6: 月柱模式 (农历月定月)
    # 1990-02-04 是立春，正月初九。
    # 假设测试 1990-02-03 (农历正月初八)，此时立春未到。
    # SOLAR_TERM 模式下应为 丙子月(1989年的月)，LUNAR_MONTH 模式下应为 戊寅月(1990年的月)。
    req6_term = BaziRequest(
        name="节气月",
        birth_datetime="1990-02-03 12:00:00",
        month_mode=MonthMode.SOLAR_TERM
    )
    res6_term = engine.arrange(req6_term)
    
    req6_lunar = BaziRequest(
        name="农历月",
        birth_datetime="1990-02-03 12:00:00",
        month_mode=MonthMode.LUNAR_MONTH
    )
    res6_lunar = engine.arrange(req6_lunar)
    
    assert res6_term.core.month.gan != res6_lunar.core.month.gan
    assert res6_lunar.core.month.gan == "戊" # 1990年正月干支是戊寅

def test_full_output_structure(engine):
    """
    验证输出结构是否包含 DESIGN.md 3.0 节要求的全量板块
    """
    req = BaziRequest(
        name="结构测试",
        birth_datetime="1990-01-01 12:00:00"
    )
    res = engine.arrange(req)
    
    # 环境快照
    assert res.environment.original_request.name == "结构测试"
    # 核心命盘
    assert res.core.jie_qi.prev_jie != ""
    # 动态运程
    assert len(res.fortune.da_yun) > 0
    assert len(res.fortune.before_start_xiao_yun) > 0
    # 辅助命盘
    assert res.auxiliary.ming_gong != ""
