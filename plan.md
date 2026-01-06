# 八字排盘引擎开发计划 (Phase 1 & 2) - 完整对账版

## 0. 项目目标 (Overall Goal)
**构建一个遵循《渊海子平》标准的专业级八字排盘引擎。**
实现从原始输入到高精度命盘输出的全流程自动化。本次更新确保完全覆盖 `DESIGN.md` 中的所有预处理逻辑与数据提取项。

---

## 第一阶段：输入预处理 (Input Preprocessing)
**目标**：将用户输入标准化为 `BaziContext`，并保留环境快照。

### 1.1 定义请求模型与配置
- [x] **任务 1.1.1**: 定义 `BaziRequest` 模型。
- [x] **任务 1.1.2**: 创建 `BaziConfig` 处理经纬度。
- [ ] **任务 1.1.3 (补)**: 增加 `EnvironmentSnapshot` 模型。
    - **说明**: 记录系统处理时间（`processed_at`）、原始参数备份。

### 1.2 时间与历法标准化
- [x] **任务 1.2.1**: 实现 `CalendarConverter`。
- [x] **任务 1.2.2**: 夏令时 (DST) 修正。

### 1.3 真太阳时 (True Solar Time) 模块
- [x] **任务 1.3.1**: 实现均时差 (EoT) 计算。
- [x] **任务 1.3.2**: 实现经度修正。

---

## 第二阶段：lunar_python 核心集成 (Data Extraction)
**目标**：完全映射 `DESIGN.md` 规定的所有数据字段。

### 2.1 核心命盘提取 (Core Chart)
- [x] **任务 2.1.1**: 定义 `Column` 和 `CoreChart` 模型。
- [ ] **任务 2.1.2 (补)**: 增加 `JieQiContext`。
    - **字段**: `prev_jie` (前一个节气时刻), `next_jie` (后一个节气时刻)。
- [ ] **任务 2.1.3 (补)**: 实现月柱模式分支逻辑。
    - **逻辑**: 若 `month_mode == LUNAR_MONTH`，需强制提取农历月干支。

### 2.2 动态运程提取 (Fortune Data)
- [ ] **任务 2.2.1 (补)**: 完善多级流转模型。
    - **LiuNian**: 增加 `liu_yue: List[LiuYue]` 结构。
    - **LiuYue**: 增加 `liu_ri: List[LiuRi]` 结构。
- [ ] **任务 2.2.2 (补)**: 实现小运 (Minor Luck) 系统。
    - **结构**: 包含 `before_start_xiao_yun` (起运前) 和 `da_yun_xiao_yun` (大运期间)。
- [ ] **任务 2.2.3 (补)**: 修正 `FortuneData` 起运年龄。
    - **说明**: 从库获取精确起运时间。

### 2.3 辅助命盘提取 (Auxiliary Chart)
- [x] **任务 2.3.1**: 定义 `AuxiliaryChart` 模型。
- [x] **任务 2.3.2**: 完成数据填充。

### 2.4 引擎 API 封装与“设计对账”
- [ ] **任务 2.4.1 (补)**: 实现 `BaziResult` 完整聚合模型。
    - **包含**: `request`, `environment`, `core`, `fortune`, `auxiliary` 五大板块。
- [ ] **任务 2.4.2 (强推)**: **设计对账审计测试 (Design Alignment Audit)**。
    - **说明**: 编写 `tests/test_design_alignment.py`，遍历 `DESIGN.md` 的表格，确保每一个提到的“具体项目”在 JSON 输出中都有对应的 Key。

---

## 质量保障：如何防止犯低级错误？
1.  **逐项对账**：每次模型修改后，必须重新阅读 `DESIGN.md` 的对应章节。
2.  **强制测试覆盖**：新补全的字段（如节气、小运）必须有独立断言。
3.  **模型先行**：严禁在代码中临时拼凑字典，必须通过 Pydantic 模型强制契约。
