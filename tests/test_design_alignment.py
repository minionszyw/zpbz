import json
from src.engine.core import BaziEngine
from src.engine.models import BaziRequest, CalendarType, TimeMode, MonthMode, ZiShiMode

def test_design_alignment_audit():
    """
    审计测试：验证输出的 JSON 结构是否完整覆盖了 DESIGN.md 中的所有具体项目。
    """
    engine = BaziEngine()
    req = BaziRequest(
        name="审计测试",
        gender=1,
        calendar_type=CalendarType.SOLAR,
        birth_datetime="1990-05-20 12:00:00",
        birth_location="西安",
        time_mode=TimeMode.TRUE_SOLAR,
        month_mode=MonthMode.SOLAR_TERM,
        zi_shi_mode=ZiShiMode.LATE_ZI_IN_DAY
    )
    
    result = engine.arrange(req)
    data = json.loads(result.model_dump_json())

    # 1. 验证 0. 预处理阶段 (DESIGN 3.0)
    assert "environment" in data
    assert "processed_at" in data["environment"]
    assert "original_request" in data["environment"]
    
    # 2. 验证 1. 核心命盘 (DESIGN 3.0)
    core = data["core"]
    for col in ["year", "month", "day", "time"]:
        assert all(k in core[col] for k in ["gan", "zhi", "shi_shen_gan", "shi_shen_zhi", "hide_gan", "na_yin", "xun_kong"])
    
    # 验证补救项: 节气上下文
    assert "jie_qi" in core
    assert "prev_jie" in core["jie_qi"]
    assert "next_jie" in core["jie_qi"]

    # 3. 验证 2. 动态运程 (DESIGN 3.0)
    fortune = data["fortune"]
    assert "start_solar" in fortune
    assert "start_age" in fortune
    assert "da_yun" in fortune
    assert len(fortune["da_yun"]) > 0
    
    # 验证补救项: 小运
    assert "before_start_xiao_yun" in fortune
    assert "xiao_yun" in fortune["da_yun"][0]
    
    # 验证级联结构
    assert "liu_nian" in fortune["da_yun"][0]
    assert "liu_yue" in fortune["da_yun"][0]["liu_nian"][0]

    # 4. 验证 3. 辅助命盘 (DESIGN 3.0)
    aux = data["auxiliary"]
    assert all(k in aux for k in ["year_di_shi", "tai_yuan", "ming_gong", "shen_gong"])
    assert len(aux["tai_yuan_na_yin"]) >= 3 # 纳音通常为3个字
