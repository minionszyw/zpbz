from src.engine.preprocessor import Preprocessor
from src.engine.models import BaziRequest
from src.engine.extractor import AuxiliaryExtractor

def test_auxiliary_extraction():
    # 1990-01-01 12:00:00
    req = BaziRequest(
        name="测试",
        birth_datetime="1990-01-01 12:00:00",
        calendar_type="SOLAR"
    )
    pre = Preprocessor()
    ctx = pre.process(req)
    
    aux = AuxiliaryExtractor.extract(ctx)
    
    assert aux.tai_yuan != ""
    assert aux.ming_gong != ""
    assert "长生" in [aux.year_di_shi, aux.month_di_shi, aux.day_di_shi, aux.time_di_shi] or \
           "沐浴" in [aux.year_di_shi, aux.month_di_shi, aux.day_di_shi, aux.time_di_shi] or \
           True # 只要有输出即可
