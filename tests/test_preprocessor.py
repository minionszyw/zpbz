from src.engine.preprocessor import Preprocessor
from src.engine.models import BaziRequest, CalendarType, TimeMode

def test_preprocessor_integration():
    # 测试成都 农历输入
    req = BaziRequest(
        name="测试",
        calendar_type=CalendarType.LUNAR,
        birth_datetime="1990-01-05 12:00:00", # 农历正月初五 -> 公历 1990-01-31
        birth_location="成都",
        time_mode=TimeMode.TRUE_SOLAR
    )
    
    pre = Preprocessor()
    ctx = pre.process(req)
    
    # 1. 验证日期转换: 1990-01-31
    assert ctx.solar.getYear() == 1990
    assert ctx.solar.getMonth() == 1
    assert ctx.solar.getDay() == 31
    
    # 2. 验证真太阳时校正 (成都经度 104.06)
    # 12:00 -> 约 10:43 (经度 -64分, 1月31日 EoT 约 -13分)
    # 这里我们只验证小时变化
    assert ctx.solar.getHour() == 10
    assert ctx.longitude == 104.06
