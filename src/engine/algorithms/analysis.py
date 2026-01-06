from typing import List, Dict, Optional
from pydantic import BaseModel
from src.engine.preprocessor import BaziContext
from src.engine.utils import Tracer
from src.engine.algorithms.energy import EnergyModel
from src.engine.algorithms.geju import GejuResult

class AnalysisResult(BaseModel):
    strength_level: str  # 极强, 偏强, 中和, 偏弱, 极弱
    strength_score: float
    yong_shen: str
    xi_shen: str
    ji_shen: str
    chou_shen: str
    logic_type: str # 护格, 扶抑, 调候

class AnalysisEngine:
    """
    终极命理分析器：综合判定强弱与喜用 (基于《渊海子平》)
    """
    
    @staticmethod
    def analyze(ctx: BaziContext, scores: Dict[str, float], geju: GejuResult, tracer: Tracer = None) -> AnalysisResult:
        lunar = ctx.solar.getLunar()
        eight_char = lunar.getEightChar()
        day_gan = eight_char.getDayGan()
        
        # 1. 获取五行角色
        day_elem = EnergyModel._gan_to_elem(day_gan)
        cycle = ["木", "火", "土", "金", "水"]
        idx = cycle.index(day_elem)
        
        sheng_me = cycle[(idx - 1) % 5] # 印
        me_sheng = cycle[(idx + 1) % 5] # 食伤
        ke_me = cycle[(idx - 2) % 5]    # 官杀
        me_ke = cycle[(idx + 2) % 5]    # 财
        
        # 2. 核心：计算净能量平衡 (Net Balance)
        support_score = scores[day_elem] + scores[sheng_me]
        drain_score = scores[me_sheng] + scores[me_ke] + scores[ke_me]
        
        total_score = sum(scores.values())
        support_ratio = support_score / total_score if total_score > 0 else 0
        
        # 3. 判定强弱
        level = "中和"
        if support_ratio > 0.7: level = "极强"
        elif support_ratio > 0.52: level = "偏强"
        elif support_ratio < 0.3: level = "极弱"
        elif support_ratio < 0.45: level = "偏弱"
        
        # 食伤过重修正
        if scores[me_sheng] > support_score * 0.8:
            if level == "中和" or level == "偏强":
                level = "偏弱"
                if tracer: tracer.record("强弱判定", f"检测到食伤[{me_sheng:.1f}]泄气过重，强弱下调至偏弱")

        if tracer:
            tracer.record("强弱判定", f"生助[{support_score:.1f}] vs 泄耗[{drain_score:.1f}], 支持率: {support_ratio*100:.1f}%, 定性: {level}")

        # 4. 喜用神推导
        yong, xi, ji, chou = "", "", "", ""
        logic = "扶抑平衡"
        
        if "强" in level:
            yong, xi, ji, chou = ke_me, me_ke, sheng_me, day_elem
        else:
            yong, xi, ji, chou = sheng_me, day_elem, ke_me, me_ke

        # 护格/病药 优先级提升
        if "破格" in geju.status:
            logic = "病药护格"
            # 简化：官格被伤必取印
            if "官" in geju.name: yong = sheng_me
        elif "伤官佩印" in geju.name or "杀印相生" in geju.name:
            logic = "格局护卫"
            yong = sheng_me

        return AnalysisResult(
            strength_level=level,
            strength_score=round(support_ratio * 100, 2),
            yong_shen=yong,
            xi_shen=xi,
            ji_shen=ji,
            chou_shen=chou,
            logic_type=logic
        )