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
        day_gan = eight_char.getDayGan()
        
        # 1. 基础格获取 (月令透干或本气)
        month_all_gans = eight_char.getMonthHideGan()
        geju_name = ""
        check_list = [
            (eight_char.getYearGan(), eight_char.getYearShiShenGan),
            (eight_char.getMonthGan(), eight_char.getMonthShiShenGan),
            (eight_char.getTimeGan(), eight_char.getTimeShiShenGan)
        ]

        for gan, shi_shen_func in check_list:
            if gan in month_all_gans:
                ss = shi_shen_func()
                if any(k in ss for k in ["官", "财", "印", "食", "杀", "伤"]):
                    geju_name = ss
                    break
        
        if not geju_name:
            main_ss = eight_char.getMonthShiShenZhi()[0]
            # 如果主气是比劫，则不以比劫定格
            if "比" in main_ss or "劫" in main_ss:
                geju_name = "建禄格" if "比" in main_ss else "月刃格"
            else:
                geju_name = main_ss

        # 2. 意象组合升级 (DESIGN 4.6 补强)
        all_stems_ss = [eight_char.getYearShiShenGan(), eight_char.getMonthShiShenGan(), eight_char.getTimeShiShenGan()]
        
        if "伤官" in geju_name or "伤官" in all_stems_ss:
            if any("印" in s for s in all_stems_ss):
                geju_name = "伤官佩印"
        elif "食神" in geju_name:
            if any("财" in s for s in all_stems_ss):
                geju_name = "食神生财"
        elif "杀" in geju_name:
            if any("印" in s for s in all_stems_ss):
                geju_name = "杀印相生"

        if not geju_name.endswith("格") and "佩印" not in geju_name and "相生" not in geju_name and "生财" not in geju_name:
            geju_name += "格"

        # 3. 质量审计 (简易)
        status = "成格"
        # 检查天干是否有克损
        if "正官" in geju_name and "伤官" in all_stems_ss:
            status = "破格 (伤官见官)"
        
        return GejuResult(
            name=geju_name,
            type="INNER_EIGHT",
            status=status,
            detail=f"综合月令与天干意象判定为[{geju_name}]"
        )
