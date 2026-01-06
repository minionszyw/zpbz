from src.engine.preprocessor import SolarTimeCalculator
from lunar_python import Solar

def test_eot_calculation():
    # 验证均时差计算是否有输出且在合理范围内 (-20 到 20 分钟)
    s = Solar.fromYmdHms(2023, 1, 1, 12, 0, 0)
    eot = SolarTimeCalculator.get_eot(s)
    assert -20 < eot < 20

def test_true_solar_time_longitude():
    # 成都 (104.06) 约比 120度 晚 (120 - 104.06) * 4 = 63.76 分钟
    s = Solar.fromYmdHms(2023, 3, 20, 12, 0, 0) # 春分附近 EoT 接近 0
    true_solar = SolarTimeCalculator.get_true_solar_time(s, 104.06)
    
    # 12:00 - 约 72 分钟 (64分经度 + 8分EoT) = 10:48 左右
    assert true_solar.getHour() == 10
    assert 45 <= true_solar.getMinute() <= 55
