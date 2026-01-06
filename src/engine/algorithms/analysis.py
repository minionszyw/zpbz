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
        
        # 1. 获取日主五行
        day_elem = EnergyModel._gan_to_elem(day_gan)
        day_score = scores[day_elem]
        
        # 2. 判定强弱 (简易量化模型)
        # 假设总分在 100-500 之间波动，日主占 25% 以上为偏强
        total_score = sum(scores.values())
        ratio = day_score / total_score if total_score > 0 else 0
        
        level = "中和"
        if ratio > 0.4: level = "极强"
        elif ratio > 0.25: level = "偏强"
        elif ratio < 0.15: level = "极弱"
        elif ratio < 0.22: level = "偏弱"
        
        if tracer:
            tracer.record("强弱判定", f"日主[{day_gan}]({day_elem}) 得分: {day_score:.2f}, 占比: {ratio*100:.1f}%, 判定为: {level}")

        # 3. 喜用神推导 (扶抑为主)
        # 定义五行相生相克关系
        # 木 -> 火 -> 土 -> 金 -> 水 -> 木
        cycle = ["木", "火", "土", "金", "水"]
        idx = cycle.index(day_elem)
        
        sheng_me = cycle[(idx - 1) % 5] # 印
        me_sheng = cycle[(idx + 1) % 5] # 食伤
        ke_me = cycle[(idx - 2) % 5]    # 官杀
        me_ke = cycle[(idx + 2) % 5]    # 财
        
        yong, xi, ji, chou = "", "", "", ""
        logic = "扶抑平衡"

        if "强" in level:
            # 身强喜克泄耗
            yong = ke_me # 首选官杀
            xi = me_ke   # 次选财
            ji = sheng_me # 忌印
            chou = day_elem # 仇比
        else:
            # 身弱喜生扶
            yong = sheng_me # 首选印
            xi = day_elem   # 次选比劫
            ji = ke_me      # 忌官杀
            chou = me_ke    # 仇财

        # 护格优化 (DESIGN 4.7)
        if geju.status == "破格":
            logic = "病药护格"
            # 简化逻辑：如果是官格见伤，喜印制伤
            if "官" in geju.name:
                yong = "印" # 这是一个示意，实际需映射五行
        
        return AnalysisResult(
            strength_level=level,
            strength_score=round(ratio * 100, 2),
            yong_shen=yong,
            xi_shen=xi,
            ji_shen=ji,
            chou_shen=chou,
            logic_type=logic
        )
