from typing import List, Dict, Optional, Tuple
from pydantic import BaseModel
from src.engine.preprocessor import BaziContext
from src.engine.utils import Tracer
from src.engine.algorithms.interactions import Interaction

class GejuResult(BaseModel):
    name: str
    type: str # INNER_EIGHT (正八格), SPECIAL (特殊外格)
    status: str # 成格, 破格, 带病, 败格
    is_transformed: bool = False
    detail: str

class GejuAnalyzer:
    """
    格局分析器 (遵循《渊海子平》标准)
    """
    
    @staticmethod
    def analyze(ctx: BaziContext, interactions: List[Interaction], tracer: Tracer = None) -> GejuResult:
        lunar = ctx.solar.getLunar()
        eight_char = lunar.getEightChar()
        
        # 1. 优先神检测: 有官莫寻格局
        # (简化实现: 暂跳过)

        # 2. 正八格判定逻辑 (月令为纲)
        month_zhi = eight_char.getMonthZhi()
        month_all_gans = eight_char.getMonthHideGan()
        
        geju_name = ""
        geju_type = "INNER_EIGHT"
        
        # 检查透干: 年, 月, 时
        # 定义检查列表: (天干值, 获取该干十神的方法)
        check_list = [
            (eight_char.getYearGan(), eight_char.getYearShiShenGan),
            (eight_char.getMonthGan(), eight_char.getMonthShiShenGan),
            (eight_char.getTimeGan(), eight_char.getTimeShiShenGan)
        ]

        for gan, shi_shen_func in check_list:
            if gan in month_all_gans:
                ss = shi_shen_func()
                # 官、财、印、食、杀、伤 均可成格
                if any(k in ss for k in ["官", "财", "印", "食", "杀", "伤"]):
                    geju_name = f"{ss}格"
                    if tracer: tracer.record("格局分析", f"月令藏干[{gan}]透出为{ss}，定格为[{geju_name}]")
                    break
        
        if not geju_name:
            # 无透干，取本气 (库中 getShiShenZhi[1] 通常是月令本气十神)
            main_ss = eight_char.getMonthShiShenZhi()[0] # 主气十神
            geju_name = f"{main_ss}格"
            if tracer: tracer.record("格局分析", f"月令无透干，取本气十神[{main_ss}]定格")

        # 3. 质量审计 (简易逻辑)
        status = "成格"
        # 检查是否有冲破月令的情况
        for inter in interactions:
            if inter.type == "冲" and ("月支" in [inter.source, inter.target]):
                status = "破格"
                if tracer: tracer.record("格局分析", f"格局 [{geju_name}] 因月令被冲而破损")

        return GejuResult(
            name=geju_name,
            type=geju_type,
            status=status,
            detail=f"取自月令{month_zhi}中{geju_name}"
        )
