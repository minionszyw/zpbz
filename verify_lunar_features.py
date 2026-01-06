from lunar_python import Solar, Lunar, EightChar
import datetime

def test_lunar_features():
    # 使用 1990-01-01 12:00:00 作为测试基准
    solar = Solar.fromYmdHms(1990, 1, 1, 12, 0, 0)
    lunar = solar.getLunar()
    # 默认配置
    eight_char = lunar.getEightChar()
    
    print(f"--- 验证 lunar_python 数据来源 ---")
    
    # 1. 核心命盘
    print(f"\n[1. 核心命盘]")
    print(f"四柱: {eight_char.getYear()} {eight_char.getMonth()} {eight_char.getDay()} {eight_char.getTime()}")
    print(f"日干十神: {eight_char.getDayShiShenGan()}")
    print(f"年支藏干十神: {eight_char.getYearShiShenZhi()}")
    print(f"日柱纳音: {eight_char.getDayNaYin()}")
    print(f"日柱空亡: {eight_char.getDayXunKong()}")
    print(f"年柱空亡: {eight_char.getYearXunKong()}")

    # 2. 动态运程
    print(f"\n[2. 动态运程]")
    # 假设为男命 (1)
    yun = eight_char.getYun(1)
    print(f"起运时间: {yun.getStartSolar().toFullString()}")
    
    da_yun_list = yun.getDaYun()
    if da_yun_list:
        # 起运前的小运 (index 0)
        dy_before = da_yun_list[0]
        xiao_yun_before = dy_before.getXiaoYun()
        print(f"起运前小运示例: {xiao_yun_before[0].getGanZhi() if xiao_yun_before else 'None'}")
        
        dy = da_yun_list[1] # 第一步大运 (注意 index 1 才是第一步正式大运)
        print(f"第一步大运: {dy.getGanZhi()} (起于 {dy.getStartYear()} 年)")
        
        liu_nian_list = dy.getLiuNian()
        if liu_nian_list:
            ln = liu_nian_list[0]
            print(f"流年示例: {ln.getGanZhi()}")
            
            xiao_yun_list = dy.getXiaoYun()
            print(f"大运期间小运示例: {xiao_yun_list[0].getGanZhi() if xiao_yun_list else 'None'}")

    # 3. 辅助元素
    print(f"\n[3. 辅助元素]")
    print(f"年柱地势(长生): {eight_char.getYearDiShi()}")
    print(f"胎元: {eight_char.getTaiYuan()} ({eight_char.getTaiYuanNaYin()})")
    print(f"胎息: {eight_char.getTaiXi()} ({eight_char.getTaiXiNaYin()})")
    print(f"命宫: {eight_char.getMingGong()} ({eight_char.getMingGongNaYin()})")
    print(f"身宫: {eight_char.getShenGong()} ({eight_char.getShenGongNaYin()})")

    # 4. 模式验证
    print(f"\n[4. 模式验证 - 子时与 Sect]")
    # 晚子时测试: 1990-01-01 23:30
    solar_late_zi = Solar.fromYmdHms(1990, 1, 1, 23, 30, 0)
    lunar_late_zi = solar_late_zi.getLunar()
    
    ec2 = lunar_late_zi.getEightChar()
    ec2.setSect(2) # 默认
    print(f"23:30 (Sect 2 - 晚子时不换日) 日柱: {ec2.getDay()}")
    
    ec1 = lunar_late_zi.getEightChar()
    ec1.setSect(1) # 换日?
    print(f"23:30 (Sect 1 - 换日模式?) 日柱: {ec1.getDay()}")

    print(f"\n[5. 模式验证 - 月柱模式]")
    # 验证 Exact vs 非 Exact (手动通过 Lunar 对象验证)
    print(f"Lunar 默认月柱(节气): {lunar.getMonthInGanZhiExact()}")
    print(f"Lunar 农历月柱(初一): {lunar.getMonthInGanZhi()}")

if __name__ == "__main__":
    test_lunar_features()
