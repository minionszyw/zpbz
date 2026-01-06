import pytest
import json
import re
from src.engine.core import BaziEngine
from src.engine.models import BaziRequest, Gender, CalendarType, TimeMode, MonthMode, ZiShiMode

@pytest.fixture
def engine():
    return BaziEngine()

def test_structural_audit(engine):
    """
    1. 结构审计：确保输出 JSON 包含 DESIGN.md 要求的所有核心板块和细分字段。
    """
    req = BaziRequest(
        name="审计员",
        birth_datetime="1990-01-01 12:00:00",
        birth_location="北京"
    )
    result = engine.arrange(req)
    data = result.model_dump()

    # A. 预处理板块 (DESIGN 3.0 - 0)
    assert "environment" in data, "缺失环境记录板块"
    assert "processed_at" in data["environment"]
    assert "original_request" in data["environment"]
    assert "birth_solar_datetime" in data, "缺失校正后公历时间"
    assert "birth_lunar_datetime" in data, "缺失校正后农历时间"

    # B. 核心命盘板块 (DESIGN 3.0 - 1)
    core = data["core"]
    for col in ["year", "month", "day", "time"]:
        fields = ["gan", "zhi", "shi_shen_gan", "shi_shen_zhi", "hide_gan", "na_yin", "xun_kong"]
        for f in fields:
            assert f in core[col], f"核心命盘 {col} 缺失字段: {f}"
    
    assert "jie_qi" in core, "缺失节气板块"
    assert "prev_name" in core["jie_qi"] and "next_name" in core["jie_qi"], "缺失节气名称"

    # C. 动态运程板块 (DESIGN 3.0 - 2)
    fortune = data["fortune"]
    assert "start_solar" in fortune, "缺失起运时间"
    assert "da_yun" in fortune and len(fortune["da_yun"]) > 0, "缺失大运列表"
    assert "before_start_xiao_yun" in fortune, "缺失起运前小运"
    
    # D. 辅助命盘板块 (DESIGN 3.0 - 3)
    aux = data["auxiliary"]
    assert all(k in aux for k in ["year_di_shi", "tai_yuan", "ming_gong", "shen_gong"]), "辅助命盘字段不全"

def test_logic_dst_audit(engine):
    """
    2. 逻辑审计：验证 1988 年夏令时自动回拨逻辑。
    """
    # 1988年5月20日 12:00 北京时间 -> 夏令时回拨后应为 11:00
    req = BaziRequest(
        name="夏令时审计",
        birth_datetime="1988-05-20 12:00:00",
        time_mode=TimeMode.MEAN_SOLAR # 仅测试夏令时
    )
    result = engine.arrange(req)
    assert "11:00:00" in result.birth_solar_datetime

def test_logic_true_solar_audit(engine):
    """
    3. 逻辑审计：验证喀什（极西地区）真太阳时大幅度修正。
    """
    # 喀什经度约 75.9, 与 120度 差 44.1度 -> 约 176 分钟 (近3小时)
    req = BaziRequest(
        name="喀什审计",
        birth_location="喀什市", # 匹配 data/latlng.json
        birth_datetime="1990-01-01 12:00:00",
        time_mode=TimeMode.TRUE_SOLAR
    )
    result = engine.arrange(req)
    # 12:00 减去近 3 小时，应该在 09:00 左右
    assert "09:" in result.birth_solar_datetime

def test_logic_lunar_month_mode_audit(engine):
    """
    4. 逻辑审计：验证 LUNAR_MONTH 模式强制换月。
    """
    # 1990年2月3日，立春前，但已过农历正月初一。
    # SOLAR_TERM 模式应为 丁丑月，LUNAR_MONTH 模式应为 戊寅月。
    req_lunar = BaziRequest(
        name="换月审计",
        birth_datetime="1990-02-03 12:00:00",
        month_mode=MonthMode.LUNAR_MONTH
    )
    result = engine.arrange(req_lunar)
    assert result.core.month.gan == "戊"
    assert result.core.month.zhi == "寅"

def test_logic_no_zodiac_audit(engine):
    """
    5. 安全审计：确保所有输出中已无“星座”信息。
    """
    req = BaziRequest(name="星座清理审计", birth_datetime="1990-05-20 12:00:00")
    result = engine.arrange(req)
    output_str = result.model_dump_json()
    zodiacs = ["白羊", "金牛", "双子", "巨蟹", "狮子", "处女", "天秤", "天蝎", "射手", "摩羯", "水瓶", "双鱼"]
    for z in zodiacs:
        assert z + "座" not in output_str, f"输出中残留星座信息: {z}"

if __name__ == "__main__":
    # 如果直接运行，使用 pytest 执行
    import sys
    sys.exit(pytest.main([__file__, "-v"]))
