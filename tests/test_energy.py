import pytest
from src.engine.core import BaziEngine
from src.engine.models import BaziRequest

@pytest.fixture
def engine():
    return BaziEngine()

def test_energy_scoring_and_states(engine):
    """
    验证五行能量评分与状态机输出
    案例: 1990-01-01 12:00 (丙火日主，子月)
    """
    req = BaziRequest(
        name="能量测试",
        birth_datetime="1990-01-01 12:00:00"
    )
    res = engine.arrange(req)
    
    # 1. 验证状态机
    # 丙火在子月应为 "胎"
    assert res.five_elements.states["火"] == "胎"
    # 壬水(水)在子月应为 "帝旺"
    assert res.five_elements.states["水"] == "帝旺"

    # 2. 验证评分 (定量)
    scores = res.five_elements.scores
    # 1990-01-01 12:00 火的力量应该很强 (地支巳、寅、午全是火根)
    assert scores["火"] > scores["金"] # 局中几乎无金
    assert scores["火"] > 50 # 至少应超过 50 分
    
    # 3. 验证 Trace 记录
    trace_msgs = [t.desc for t in res.analysis_trace if t.module == "五行评分"]
    assert len(trace_msgs) > 0
    assert any("通根" in msg for msg in trace_msgs)
