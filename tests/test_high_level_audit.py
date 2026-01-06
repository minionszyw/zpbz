import pytest
import time
from src.engine.core import BaziEngine
from src.engine.models import BaziRequest, CalendarType, MonthMode

@pytest.fixture
def engine():
    return BaziEngine()

def test_leap_month_logic(engine):
    """
    验证 1993 年闰三月 (1993-03-22 Lunar) 在 LUNAR_MONTH 模式下的表现。
    """
    # 1. 1993年三月 (非闰)
    req_march = BaziRequest(
        name="三月",
        calendar_type=CalendarType.LUNAR,
        birth_datetime="1993-03-15 12:00:00",
        month_mode=MonthMode.LUNAR_MONTH
    )
    res_march = engine.arrange(req_march)
    # 1993年三月是 丙辰月
    assert res_march.core.month.gan == "丙"
    assert res_march.core.month.zhi == "辰"

    # 2. 1993年闰三月 (Leap)
    # 闰三月依然跟随三月的干支 (丙辰)，但我们要确保它能被正确提取且不报错
    req_leap = BaziRequest(
        name="闰三月",
        calendar_type=CalendarType.LUNAR,
        birth_datetime="1993-03-22 12:00:00", # 注意：birth_datetime 传入的是名义日期，模型会转公历
        month_mode=MonthMode.LUNAR_MONTH
    )
    # 由于 birth_datetime 解析目前不支持直接传 '闰' 标志字符串，
    # 我们通过构造公历来验证 (1993年闰三月廿二 = 公历 1993-05-13)
    req_leap_solar = BaziRequest(
        name="闰三月公历",
        calendar_type=CalendarType.SOLAR,
        birth_datetime="1993-05-13 12:00:00",
        month_mode=MonthMode.LUNAR_MONTH
    )
    res_leap = engine.arrange(req_leap_solar)
    assert res_leap.core.month.gan == "丙" # 依然是丙辰
    assert "一九九三年闰三月廿二" in res_leap.birth_lunar_datetime

def test_performance_stress(engine):
    """
    性能验收：连续执行 1000 次排盘，计算耗时。
    """
    req = BaziRequest(
        name="压力测试",
        birth_datetime="1990-01-01 12:00:00"
    )
    
    count = 1000
    start_time = time.time()
    
    for _ in range(count):
        engine.arrange(req)
        
    end_time = time.time()
    total_time = end_time - start_time
    avg_time = (total_time / count) * 1000 # 毫秒
    
    print(f"\n[性能报告]")
    print(f"  > 总执行次数: {count}")
    print(f"  > 总耗时: {total_time:.2f} 秒")
    print(f"  > 平均耗时: {avg_time:.2f} 毫秒/次")
    
    # 验收标准：单次排盘平均应小于 20ms (在现代 CPU 上通常 < 5ms)
    assert avg_time < 20, f"性能未达标: {avg_time:.2f}ms"

if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-s"]))
