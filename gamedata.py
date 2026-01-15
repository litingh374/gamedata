# gamedata.py

# === 基礎設定 ===
REGIONS = ["台北市 (Taipei)", "新北市 (New Taipei)"]
PROJECT_TYPES = ["素地新建 (Empty Land)", "拆併建照 (Demolition & Build)"]

# === 法規與判定門檻 ===
THRESHOLDS = {
    "POLLUTION_FACTOR": 4600,  # 面積 x 工期 > 4600 需逕流廢水
    "B8_AREA": 500,            # 面積 > 500m2 需 B8
    "B8_COST": 5000000,        # 造價 > 500萬 需 B8
    "TRAFFIC_AREA": 10000,     # 樓地板 > 10000 需交維
    "GREEN_BUILDING_COST": 50000000 # 造價 > 5000萬 需綠建築
}

# === Chapter 1: 戰略部署資料 ===
RESOURCE_RATES = {
    "STEEL": 0.15,   # 每 m2 約需 0.15 噸鋼筋
    "CONCRETE": 0.8, # 每 m2 約需 0.8 m3 混凝土
}

ENV_OPTIONS = {
    "LOW": {"name": "基本防護 (帆布+人工沖洗)", "cost": 50000, "risk": 40, "desc": "省錢，但容易被環保局開單。"},
    "MID": {"name": "標準防護 (洗車台+沉澱池)", "cost": 150000, "risk": 10, "desc": "CP值高，符合法規要求。"},
    "HIGH": {"name": "完美防護 (自動洗車+汙水處理機)", "cost": 400000, "risk": 0, "desc": "極致環保，稽查員看了都比讚。"}
}

DIPLOMACY_STRATEGIES = {
    "HAWK": {"name": "依法行政 (鷹派)", "cost": 0, "anger": 30, "desc": "不囉嗦，照規矩來。容易累積民怨。"},
    "DOVE": {"name": "敦親睦鄰 (鴿派)", "cost": 80000, "anger": -20, "desc": "送禮賠笑，花錢消災。鄰居心情好。"}
}

# === Chapter 1: 任務清單 ===
DEMO_SEALS = {
    "D01": {"name": "鄰房鑑定報告", "code": "NW2300", "desc": "必備！除非你敢簽切結書"},
    "D02": {"name": "B5 土方流向", "code": "NW2600", "desc": "確認廢土去處"},
    "D03": {"name": "B8 廢棄物計畫", "code": "NW2700", "desc": "確認垃圾去處"},
    "D04": {"name": "防空避難室撤除", "code": "Doc_Police", "desc": "向警察局申請(若有)"},
    "D05": {"name": "監拆報告書", "code": "NW2500", "desc": "建築師簽證"},
    "D06": {"name": "拆除施工計畫", "code": "NW2400", "desc": "營造廠撰寫"},
    "D07": {"name": "行政驗收(圖說抽查)", "code": "Check_Arch", "desc": "建照科圖說抽查"},
}

GREEN_QUEST = {
    "G01": {"name": "空污費申報 (Level 1)", "code": "NW1000", "desc": "基本款，繳費取得收據"},
    "G02": {"name": "逕流廢水計畫 (Level 2)", "code": "NW1100", "desc": "門檻：面積x工期 > 4600"},
    "G03": {"name": "營建混合物 B8 (Level 3)", "code": "NW2700", "desc": "門檻：拆除或大型工程"},
}

# === Chapter 2: 施工戰略資料 ===
CONSTRUCTION_METHODS = {
    "BOTTOM_UP": {
        "name": "順打工法 (Bottom-Up)",
        "desc": "傳統工法，先挖到底再蓋上來。技術成熟但開挖風險高。",
        "cost_mod": 0,       # 成本變動
        "time_mod": 0,       # 工期變動
        "risk_mod": 10       # 基礎開挖風險增加
    },
    "TOP_DOWN": {
        "name": "逆打工法 (Top-Down)",
        "desc": "地上地下同時施工。速度快，但技術難度高，需額外設備。",
        "cost_mod": 5000000, # 鋼柱成本高
        "time_mod": -8,      # 工期減少 8 週
        "risk_mod": 20       # 結構體品質風險增加
    }
}

TEAM_MEMBERS = {
    "DIRECTOR": [
        {"id": "DIR_SENIOR", "name": "資深主任 (老王)", "salary": 80000, "skill": "免疫刁難", "req": "NW3500"},
        {"id": "DIR_JUNIOR", "name": "菜鳥主任 (阿明)", "salary": 40000, "skill": "容易忘記帶章", "req": "NW3500"}
    ],
    "PE": [ # Professional Engineer
        {"id": "PE_FULL", "name": "專任技師 (強哥)", "salary": 60000, "skill": "審查加速"},
        {"id": "PE_PART", "name": "兼職技師 (小林)", "salary": 20000, "skill": "無"}
    ],
    "SAFETY": [
        {"id": "SAF_PRO", "name": "專職勞安 (安安)", "salary": 45000, "skill": "意外防護罩"},
        {"id": "SAF_NONE", "name": "無 (違法省錢)", "salary": 0, "skill": "高風險"}
    ]
}

GEMS = {
    "GEM_GUILD": {"name": "公會寶石", "desc": "施工計畫外審"},
    "GEM_PIPE": {"name": "管線寶石", "desc": "五大管線查詢"},
    "GEM_TRAFFIC": {"name": "交通寶石", "desc": "交維計畫"},
    "GEM_SURVEY": {"name": "測量寶石", "desc": "路心樁復原"},
    "GEM_SAFETY": {"name": "勞安寶石", "desc": "危險場所評估"},
    "GEM_ADMIN": {"name": "建管寶石", "desc": "計畫書彙整"},
}

# === 隨機事件庫 ===
RANDOM_EVENTS = [
    {"id": "E01", "title": "👻 幽靈管線突襲", "desc": "怪手挖到不明電纜！圖資上明明沒有...", "options": [{"text": "停工通報", "effect": "delay", "val": 2, "msg": "工期延誤2週"}, {"text": "偷埋回去", "effect": "risk", "val": 30, "msg": "風險+30%"}]},
    {"id": "E06", "title": "🚛 違規傾倒", "desc": "土方司機把廢土倒在路邊被抓到了！", "options": [{"text": "繳罰單並悔過", "effect": "cost", "val": 100000, "msg": "罰款10萬"}, {"text": "說是司機個人行為", "effect": "risk", "val": 20, "msg": "推卸責任，風險+20%"}]},
    {"id": "E07", "title": "🧱 氯離子超標", "desc": "混凝土車快篩發現數值異常！", "options": [{"text": "整車退貨", "effect": "delay", "val": 1, "msg": "進度延誤1週"}, {"text": "賭一把灌下去", "effect": "disaster", "val": 0, "msg": "變成海砂屋！Game Over"}]}
]

# === 其他資料 ===
SETTING_OUT_STEPS = [{"id": "S1", "name": "網路掛件", "desc": "系統檢核", "hp": 20}, {"id": "S2", "name": "紙本掛件", "desc": "承辦核對", "hp": 20}, {"id": "S3", "name": "現場會勘", "desc": "BOSS 現身", "hp": 30}, {"id": "S4", "name": "文案核對", "desc": "圖說檢查", "hp": 15}, {"id": "S5", "name": "簽核准用", "desc": "核准函", "hp": 15}]

NW_CODES = {
    "NW0100": {"name": "開工申報書", "type": "doc"},
    "NW1000": {"name": "空污費收據", "type": "doc"},
    "NW1100": {"name": "逕流廢水核備函", "type": "doc"},
    "NW2300": {"name": "鄰房鑑定報告", "type": "doc"},
    "NW2400": {"name": "拆除施工計畫書", "type": "doc"},
    "NW2500": {"name": "監拆報告書", "type": "doc"},
    "NW2600": {"name": "B5土方核准函", "type": "doc"},
    "NW2700": {"name": "B8廢棄物核准函", "type": "doc"},
    "NW3300": {"name": "施工計畫書", "type": "doc"},
    "NW5000": {"name": "配筋圖", "type": "drawing"},
    "NW3500": {"name": "工地主任證書", "type": "doc"},
    "NS1300": {"name": "鋼筋無輻射證明", "type": "doc"},
    "NS1900": {"name": "混凝土抗壓報告", "type": "doc"},
    "NS2200": {"name": "公會抽查紀錄表", "type": "doc"},
    "NS2400": {"name": "紅火蟻清查紀錄表", "type": "doc"},
}

STRUCTURE_ITEMS = {
    "NS1300": {"name": "鋼筋無輻射證明", "desc": "每批鋼筋必備"},
    "NS1900": {"name": "混凝土抗壓報告", "desc": "需28天養護 (時間差陷阱)"},
    "NS2200": {"name": "公會抽查紀錄", "desc": "2F及特定樓層必備"},
    "NS2400": {"name": "紅火蟻清查紀錄", "desc": "每月重置，容易忘記"},
}