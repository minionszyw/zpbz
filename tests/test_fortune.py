from src.engine.preprocessor import Preprocessor
from src.engine.models import BaziRequest
from src.engine.extractor import FortuneExtractor

def test_fortune_extraction():
    # 1990-01-01 12:00:00 男命
    req = BaziRequest(
        name="测试",
        birth_datetime="1990-01-01 12:00:00",
        calendar_type="SOLAR",
        gender=1
    )
    pre = Preprocessor()
    ctx = pre.process(req)
    
    fortune = FortuneExtractor.extract(ctx)
    
    assert len(fortune.da_yun) > 0
    # 第一步大运
    dy1 = fortune.da_yun[0]
    assert dy1.index == 1
    assert len(dy1.liu_nian) > 0
