from typing import Dict, List, Tuple
from src.engine.preprocessor import BaziContext
from src.engine.utils import Tracer

class EnergyModel:
    """
    五行能量量化与状态机模型 (基于《渊海子平》)
    """
    
    # 十天干生旺死绝表 (天干: {地支: 状态})
    # 状态：长、沐、冠、临、旺、衰、病、死、墓、绝、胎、养
    SHENG_WANG_TABLE = {
        "甲": {"亥": "长生", "子": "沐浴", "丑": "冠带", "寅": "临官", "卯": "帝旺", "辰": "衰", "巳": "病", "午": "死", "未": "墓", "申": "绝", "酉": "胎", "戌": "养"},
        "丙": {"寅": "长生", "卯": "沐浴", "辰": "冠带", "巳": "临官", "午": "帝旺", "未": "衰", "申": "病", "酉": "死", "戌": "墓", "亥": "绝", "子": "胎", "丑": "养"},
        "戊": {"寅": "长生", "卯": "沐浴", "辰": "冠带", "巳": "临官", "午": "帝旺", "未": "衰", "申": "病", "酉": "死", "戌": "墓", "亥": "绝", "子": "胎", "丑": "养"},
        "庚": {"巳": "长生", "午": "沐浴", "未": "冠带", "申": "临官", "酉": "帝旺", "戌": "衰", "亥": "病", "子": "死", "丑": "墓", "寅": "绝", "卯": "胎", "辰": "养"},
        "壬": {"申": "长生", "酉": "沐浴", "戌": "冠带", "亥": "临官", "子": "帝旺", "丑": "衰", "寅": "病", "卯": "死", "辰": "墓", "巳": "绝", "午": "胎", "未": "养"},
        "乙": {"午": "长生", "巳": "沐浴", "辰": "冠带", "卯": "临官", "寅": "帝旺", "丑": "衰", "子": "病", "亥": "死", "戌": "墓", "酉": "绝", "申": "胎", "未": "养"},
        "丁": {"酉": "长生", "申": "沐浴", "未": "冠带", "午": "临官", "巳": "帝旺", "辰": "衰", "卯": "病", "寅": "死", "丑": "墓", "子": "绝", "亥": "胎", "戌": "养"},
        "己": {"酉": "长生", "申": "沐浴", "未": "冠带", "午": "临官", "巳": "帝旺", "辰": "衰", "卯": "病", "寅": "死", "丑": "墓", "子": "绝", "亥": "胎", "戌": "养"},
        "辛": {"子": "长生", "亥": "沐浴", "戌": "冠带", "酉": "临官", "申": "帝旺", "未": "衰", "午": "病", "巳": "死", "辰": "墓", "卯": "绝", "寅": "胎", "丑": "养"},
        "癸": {"卯": "长生", "寅": "沐浴", "丑": "冠带", "子": "临官", "亥": "帝旺", "戌": "衰", "酉": "病", "申": "死", "未": "墓", "午": "绝", "巳": "胎", "辰": "养"},
    }

    # 五行与天干映射
    ELEMENT_MAP = {
        "木": ["甲", "乙"], "火": ["丙", "丁"], "土": ["戊", "己"], "金": ["庚", "辛"], "水": ["壬", "癸"]
    }
    
    # 支藏干对应分值权重 (用于通根计算)
    ROOT_WEIGHTS = {
        "MAIN": 3.0,   # 本气
        "MEDIUM": 1.5, # 中气
        "RESIDUAL": 1.0 # 余气
    }

    @staticmethod
    def get_state(gan: str, zhi: str) -> str:
        return EnergyModel.SHENG_WANG_TABLE.get(gan, {}).get(zhi, "未知")

    @staticmethod
    def calculate_scores(ctx: BaziContext, tracer: Tracer = None) -> Dict[str, Dict]:
        """
        计算五行综合能量分值。
        """
        lunar = ctx.solar.getLunar()
        eight_char = lunar.getEightChar()
        month_zhi = eight_char.getMonthZhi()
        day_gan = eight_char.getDayGan()
        
        scores = {elem: 0.0 for elem in EnergyModel.ELEMENT_MAP.keys()}
        states = {}

        # 1. 扫描天干
        stems = [
            (eight_char.getYearGan(), 1.0, "年干"),
            (eight_char.getMonthGan(), 1.2, "月干"),
            (eight_char.getTimeGan(), 1.0, "时干"),
            (eight_char.getDayGan(), 0.5, "日主(自身气势)") # 日主自身也占少量基础分
        ]
        
        for gan, weight, pos in stems:
            elem = EnergyModel._gan_to_elem(gan)
            base_val = 10.0 * weight
            scores[elem] += base_val

        # 2. 扫描地支通根 (强化月令权重)
        branches = [
            (eight_char.getYearZhi(), 1.0, "年支", eight_char.getYearHideGan),
            (eight_char.getMonthZhi(), 4.0, "月支", eight_char.getMonthHideGan), # 提升月令从 3.0 到 4.0
            (eight_char.getDayZhi(), 1.5, "日支", eight_char.getDayHideGan),
            (eight_char.getTimeZhi(), 1.0, "时支", eight_char.getTimeHideGan)
        ]
        
        for zhi, weight, pos, hide_func in branches:
            hide_gans = hide_func() 
            for i, gan in enumerate(hide_gans):
                elem = EnergyModel._gan_to_elem(gan)
                if i == 0: root_type = "MAIN"
                elif i == 1: root_type = "MEDIUM"
                else: root_type = "RESIDUAL"
                
                root_val = 10.0 * weight * EnergyModel.ROOT_WEIGHTS[root_type]
                scores[elem] += root_val

        # 3. 状态惩罚与修正 (核心改进)
        for elem in scores.keys():
            rep_gan = EnergyModel.ELEMENT_MAP[elem][0]
            state = EnergyModel.get_state(rep_gan, month_zhi)
            states[elem] = state
            
            # 如果处于 死、绝、病 地，能量有效性减扣 30% (符合'根本极轻'论述)
            if state in ["死", "绝", "病"]:
                old_score = scores[elem]
                scores[elem] *= 0.7
                if tracer and elem == EnergyModel._gan_to_elem(day_gan):
                    tracer.record("五行评分", f"日主处于月令[{state}]地，属于'根本极轻'，分值修正: {old_score:.1f} -> {scores[elem]:.1f}")
            
        return {elem: {"score": round(scores[elem], 2), "state": states[elem]} for elem in scores.keys()}

    @staticmethod
    def _gan_to_elem(gan: str) -> str:
        for elem, gans in EnergyModel.ELEMENT_MAP.items():
            if gan in gans: return elem
        return ""
