from src.engine.core import BaziEngine
from src.engine.models import BaziRequest, TimeMode, MonthMode, ZiShiMode, CalendarType

def verify_modes():
    engine = BaziEngine()
    
    print("\n" + "═"*60)
    print("  引擎模式切换验证 (Mode Switching Audit)")
    print("═"*60)

    # --- 1. 验证真太阳时切换 ---
    print("\n[1. 时间模式验证] 地点：成都市 (104.06°E)")
    base_params = {
        "name": "时间测试",
        "birth_datetime": "1990-01-01 12:00:00",
        "birth_location": "成都市"
    }
    
    res_mean = engine.arrange(BaziRequest(**base_params, time_mode=TimeMode.MEAN_SOLAR))
    res_true = engine.arrange(BaziRequest(**base_params, time_mode=TimeMode.TRUE_SOLAR))
    
    print(f"  > 平太阳时输出: {res_mean.birth_solar_datetime}")
    print(f"  > 真太阳时输出: {res_true.birth_solar_datetime}")
    assert res_mean.birth_solar_datetime != res_true.birth_solar_datetime
    print("  验证结论：成功！经度修正已生效。")

    # --- 2. 验证月柱模式切换 ---
    print("\n[2. 月柱模式验证] 日期：1990-02-03 (立春前，正月初八)")
    month_params = {
        "name": "月柱测试",
        "birth_datetime": "1990-02-03 12:00:00"
    }
    
    res_term = engine.arrange(BaziRequest(**month_params, month_mode=MonthMode.SOLAR_TERM))
    res_lunar = engine.arrange(BaziRequest(**month_params, month_mode=MonthMode.LUNAR_MONTH))
    
    print(f"  > 节气定月 (SOLAR_TERM): {res_term.core.month.gan}{res_term.core.month.zhi}月")
    print(f"  > 农历月定月 (LUNAR_MONTH): {res_lunar.core.month.gan}{res_lunar.core.month.zhi}月")
    assert res_term.core.month.gan != res_lunar.core.month.gan
    print("  验证结论：成功！月柱判定标准已切换。")

    # --- 3. 验证子时模式切换 ---
    print("\n[3. 子时模式验证] 时间：1990-01-01 23:30 (晚子时)")
    zi_params = {
        "name": "子时测试",
        "birth_datetime": "1990-01-01 23:30:00",
        "time_mode": TimeMode.MEAN_SOLAR
    }
    
    res_late = engine.arrange(BaziRequest(**zi_params, zi_shi_mode=ZiShiMode.LATE_ZI_IN_DAY))
    res_next = engine.arrange(BaziRequest(**zi_params, zi_shi_mode=ZiShiMode.NEXT_DAY))
    
    print(f"  > 晚子时不换日 (LATE_ZI): 日柱为 {res_late.core.day.gan}{res_late.core.day.zhi}")
    print(f"  > 23点换日 (NEXT_DAY): 日柱为 {res_next.core.day.gan}{res_next.core.day.zhi}")
    assert res_late.core.day.gan != res_next.core.day.gan
    print("  验证结论：成功！子时换日逻辑已切换。")
    print("\n" + "═"*60)

if __name__ == "__main__":
    verify_modes()
