from src.engine.preprocessor import Preprocessor
from src.engine.models import BaziRequest, ZiShiMode
from src.engine.extractor import CoreExtractor

def test_core_chart_extraction():
    # 1990-01-01 12:00:00 (庚午年 戊子月 癸酉日 戊午时)
    req = BaziRequest(
        name="测试",
        birth_datetime="1990-01-01 12:00:00",
        calendar_type="SOLAR"
    )
    pre = Preprocessor()
    ctx = pre.process(req)
    
    chart = CoreExtractor.extract(ctx)
    
    assert chart.year.gan == "己"
    assert chart.year.zhi == "巳"
    assert chart.day.gan == "丙"
    assert chart.day.zhi == "寅"

def test_zi_shi_sect():
    # 晚子时测试: 1990-01-01 23:30
    req_late = BaziRequest(
        name="晚子时",
        birth_datetime="1990-01-01 23:30:00",
        calendar_type="SOLAR",
        zi_shi_mode=ZiShiMode.LATE_ZI_IN_DAY # 晚子时不换日
    )
    pre = Preprocessor()
    ctx = pre.process(req_late)
    chart = CoreExtractor.extract(ctx)
    
    # 不换日，日柱应该是 丙寅
    assert chart.day.gan == "丙"
    
    # 换日测试
    req_next = BaziRequest(
        name="换日",
        birth_datetime="1990-01-01 23:30:00",
        calendar_type="SOLAR",
        zi_shi_mode=ZiShiMode.NEXT_DAY
    )
    ctx_next = pre.process(req_next)
    chart_next = CoreExtractor.extract(ctx_next)
    
    # 换日，日柱应该是 丁卯 (丙寅的下一日)
    assert chart_next.day.gan == "丁"
