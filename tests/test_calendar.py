from src.engine.preprocessor import CalendarConverter, DSTCorrector
from src.engine.models import CalendarType
from lunar_python import Solar

def test_calendar_conversion():
    # 公历转换
    s1 = CalendarConverter.to_solar("1990-01-01 12:00:00", CalendarType.SOLAR)
    assert s1.toYmdHms() == "1990-01-01 12:00:00"
    
    # 农历转换 (1990年正月初五 -> 1990-01-31)
    s2 = CalendarConverter.to_solar("1990-01-05 12:00:00", CalendarType.LUNAR)
    assert s2.getYear() == 1990
    assert s2.getMonth() == 1
    assert s2.getDay() == 31

def test_dst_correction():
    # 1988年5月1日 处于夏令时
    s_dst = Solar.fromYmdHms(1988, 5, 1, 12, 0, 0)
    s_corrected = DSTCorrector.check_and_correct(s_dst)
    # 应该回拨 1 小时变为 11:00
    assert s_corrected.getHour() == 11
    
    # 1990年1月1日 不处于夏令时
    s_normal = Solar.fromYmdHms(1990, 1, 1, 12, 0, 0)
    s_corrected2 = DSTCorrector.check_and_correct(s_normal)
    assert s_corrected2.getHour() == 12
