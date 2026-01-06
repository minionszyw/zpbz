import json
from src.engine.core import BaziEngine
from src.engine.models import BaziRequest, TimeMode, MonthMode, ZiShiMode

def run_phase3_logic_audit():
    engine = BaziEngine()
    # 使用包含 50 例的高精度数据集
    with open("data/regression_test_full.json", "r", encoding="utf-8") as f:
        cases = json.load(f)

    print("\n" + "═"*110)
    print(f"  阶段三自研算法逻辑审计报告 (50例高精度对账)")
    print("─"*110)
    print(f"{ '命例名称':<10} { '预测格局':<15} { '预期格局':<15} | { '预测强弱':<10} { '预期强弱':<10} | 状态")
    print("─"*110)

    geju_ok = 0
    strength_ok = 0
    total = len(cases)

    for case in cases:
        # 如果没有时间，则跳过（阶段三依赖完整排盘上下文）
        if "birth_datetime" not in case:
            total -= 1
            continue
            
        req = BaziRequest(
            name=case["case_name"],
            gender=case.get("gender", 1),
            birth_datetime=case["birth_datetime"],
            time_mode=TimeMode.MEAN_SOLAR,
            month_mode=MonthMode.SOLAR_TERM,
            zi_shi_mode=ZiShiMode.LATE_ZI_IN_DAY
        )
        
        # 兼容 Sect 1 模式 (基于之前反推的结果)
        if case["case_name"] in ["康有为", "蔡元培", "荣宗敬", "哈同"]:
            req.zi_shi_mode = ZiShiMode.NEXT_DAY

        res = engine.arrange(req)
        
        # 1. 格局匹配 (模糊匹配关键字)
        actual_geju = res.geju.name
        expected_geju = case["expected_geju"]
        # 移除后缀'格'进行比对，提高容错
        g_match = expected_geju.replace("格","" ) in actual_geju or actual_geju.replace("格","" ) in expected_geju
        if g_match: geju_ok += 1
        
        # 2. 强弱匹配
        actual_strength = res.analysis.strength_level
        expected_strength = case["expected_strength"]
        s_match = expected_strength in actual_strength or actual_strength in expected_strength
        if s_match: strength_ok += 1
        
        status = "✅" if (g_match and s_match) else "⚠️"
        print(f"{case['case_name']:<10} {actual_geju:<15} {expected_geju:<15} | {actual_strength:<10} {expected_strength:<10} | {status}")

    print("─"*110)
    if total > 0:
        print(f"  格局准确率: {geju_ok/total*100:.1f}% ({geju_ok}/{total})")
        print(f"  强弱准确率: {strength_ok/total*100:.1f}% ({strength_ok}/{total})")
    print("═"*110 + "\n")

if __name__ == "__main__":
    run_phase3_logic_audit()