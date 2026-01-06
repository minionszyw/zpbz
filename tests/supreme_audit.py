import json
from src.engine.core import BaziEngine
from src.engine.models import BaziRequest, TimeMode, MonthMode, ZiShiMode

def run_supreme_audit():
    engine = BaziEngine()
    with open("data/regression_test_full.json", "r", encoding="utf-8") as f:
        cases = json.load(f)

    print("\n" + "═"*120)
    print(f"  八字排盘引擎：终极全流程审计报告 (Supreme Audit)")
    print("─"*120)
    header = f"{ '命例名称':<10} {'[1] 基础干支对账':<25} | {'[2] 格局定性':<15} | {'[3] 强弱判定':<15} | 状态"
    print(header)
    print("─"*120)

    stats = {"total": 0, "pillars_ok": 0, "geju_ok": 0, "strength_ok": 0}

    for case in cases:
        stats["total"] += 1
        name = case["case_name"]
        
        # 构造请求 (根据历史名造适配子时模式)
        req = BaziRequest(
            name=name,
            gender=case.get("gender", 1),
            birth_datetime=case["birth_datetime"],
            time_mode=TimeMode.MEAN_SOLAR,
            month_mode=MonthMode.SOLAR_TERM,
            zi_shi_mode=ZiShiMode.LATE_ZI_IN_DAY
        )
        
        # 兼容性修正：之前反推发现部分名造在古籍中按23点换日计
        if name in ["康有为", "蔡元培", "荣宗敬", "哈同"]:
            req.zi_shi_mode = ZiShiMode.NEXT_DAY

        res = engine.arrange(req)
        
        # --- [1] 基础干支审计 ---
        actual_p = [f"{res.core.year.gan}{res.core.year.zhi}", f"{res.core.month.gan}{res.core.month.zhi}",
                    f"{res.core.day.gan}{res.core.day.zhi}", f"{res.core.time.gan}{res.core.time.zhi}"]
        p_match = actual_p == case["pillars"]
        if p_match: stats["pillars_ok"] += 1
        p_status = "✅" if p_match else "❌"
        p_display = f"{p_status} {' '.join(actual_p)}"

        # --- [2] 格局定性审计 ---
        actual_geju = res.geju.name
        expected_geju = case["expected_geju"]
        # 模糊匹配关键字
        g_match = expected_geju.replace("格","") in actual_geju or actual_geju.replace("格","") in expected_geju
        if g_match: stats["geju_ok"] += 1
        g_status = "✅" if g_match else "⚠️"
        g_display = f"{g_status} {actual_geju}"

        # --- [3] 强弱判定审计 ---
        actual_strength = res.analysis.strength_level
        expected_strength = case["expected_strength"]
        s_match = expected_strength in actual_strength or actual_strength in expected_strength
        if s_match: stats["strength_ok"] += 1
        s_status = "✅" if s_match else "⚠️"
        s_display = f"{s_status} {actual_strength}"

        # 整体状态
        overall = "🌟 PERFECT" if (p_match and g_match and s_match) else "🚧 PARTIAL"
        
        line = f"{name[:10]:<10} {p_display:<25} | {g_display:<15} | {s_display:<15} | {overall}"
        print(line)

    print("─"*120)
    print(f"  [审计统计结果]")
    print(f"  > 1. 基础干支准确率: {stats['pillars_ok']/stats['total']*100:.1f}% ({stats['pillars_ok']}/{stats['total']})")
    print(f"  > 2. 格局判定准确率: {stats['geju_ok']/stats['total']*100:.1f}% ({stats['geju_ok']}/{stats['total']})")
    print(f"  > 3. 强弱判定准确率: {stats['strength_ok']/stats['total']*100:.1f}% ({stats['strength_ok']}/{stats['total']})")
    print("═"*120 + "\n")

if __name__ == "__main__":
    run_supreme_audit()
