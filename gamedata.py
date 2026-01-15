# gamedata.py

# === 基礎設定 ===
REGIONS = ["台北市 (Taipei)", "新北市 (New Taipei)"]
PROJECT_TYPES = ["素地新建 (Empty Land)", "拆併建照 (Demolition & Build)"]

# === 法規門檻 ===
THRESHOLDS = {
    "POLLUTION_FACTOR": 4600,
    "B8_AREA": 500,
    "B8_COST": 5000000,
    "TRAFFIC_AREA": 10000,
    "GREEN_BUILDING_COST": 50000000
}

# === 隨機事件庫 (Ch1~Ch7 通用) ===
RANDOM_EVENTS = [
    {
        "id": "E01", "title": "👻 幽靈管線突襲", "desc": "怪手挖到不明電纜！圖資上明明沒有...",
        "options": [{"text": "停工通報", "effect": "delay", "val": 2, "msg": "工期延誤2週"}, {"text": "偷埋回去", "effect": "risk", "val": 30, "msg": "風險+30%"}]
    },
    {
        "id": "E06", "title": "🚛 違規傾倒", "desc": "土方司機把廢土倒在路邊被抓到了！",
        "options": [{"text": "繳罰單並悔過", "effect": "cost", "val": 100000, "msg": "罰款10萬"}, {"text": "說是司機個人行為", "effect": "risk", "val": 20, "msg": "推卸責任，風險+20%"}]
    },
    {
        "id": "E07", "title": "🧱 氯離子超標", "desc": "混凝土車快篩發現數值異常！",
        "options": [{"text": "整車退貨", "effect": "delay", "val": 1, "msg": "進度延誤1週"}, {"text": "賭一把灌下去", "effect": "disaster", "val": 0, "msg": "變成海砂屋！Game Over"}]
    }
]

# === Ch1~Ch5 舊資料 (DEMO_SEALS, GREEN_QUEST, GEMS, SETTING_OUT_STEPS) 保持不變 ===
# (為了節省篇幅，這裡省略重複部分，請務必保留原本的內容)
DEMO_SEALS = {"D01": {"name": "鄰房鑑定報告", "code": "NW2300", "desc": "必備！"}, "D02": {"name": "B5 土方流向", "code": "NW2600", "desc": "確認去處"}, "D03": {"name": "B8 廢棄物計畫", "code": "NW2700", "desc": "確認垃圾"}, "D04": {"name": "防空避難室撤除", "code": "Doc_Police", "desc": "向警察局申請"}, "D05": {"name": "監拆報告書", "code": "NW2500", "desc": "建築師簽證"}, "D06": {"name": "拆除施工計畫", "code": "NW2400", "desc": "營造廠撰寫"}, "D07": {"name": "行政驗收", "code": "Check_Arch", "desc": "圖說抽查"}}
GREEN_QUEST = {"G01": {"name": "空污費申報", "code": "NW1000", "desc": "基本款"}, "G02": {"name": "逕流廢水計畫", "code": "NW1100", "desc": "規模觸發"}, "G03": {"name": "營建混合物 B8", "code": "NW2700", "desc": "拆除觸發"}}
GEMS = {"GEM_GUILD": {"name": "公會寶石", "desc": "施工計畫外審"}, "GEM_PIPE": {"name": "管線寶石", "desc": "五大管線"}, "GEM_TRAFFIC": {"name": "交通寶石", "desc": "交維計畫"}, "GEM_SURVEY": {"name": "測量寶石", "desc": "路心樁"}, "GEM_SAFETY": {"name": "勞安寶石", "desc": "危評"}, "GEM_ADMIN": {"name": "建管寶石", "desc": "計畫書"}}
SETTING_OUT_STEPS = [{"id": "S1", "name": "網路掛件", "desc": "系統檢核", "hp": 20}, {"id": "S2", "name": "紙本掛件", "desc": "承辦核對", "hp": 20}, {"id": "S3", "name": "現場會勘", "desc": "BOSS 現身", "hp": 30}, {"id": "S4", "name": "文案核對", "desc": "圖說檢查", "hp": 15}, {"id": "S5", "name": "簽核准用", "desc": "核准函", "hp": 15}]

# === Ch7: 結構體關鍵道具 (Key Items) ===
STRUCTURE_ITEMS = {
    "NS1300": {"name": "鋼筋無輻射證明", "desc": "每批鋼筋必備"},
    "NS1900": {"name": "混凝土抗壓報告", "desc": "需28天養護 (時間差陷阱)"},
    "NS2200": {"name": "公會抽查紀錄", "desc": "2F及特定樓層必備"},
    "NS2400": {"name": "紅火蟻清查紀錄", "desc": "每月重置，容易忘記"},
}

# === 無紙化編碼表 (更新 NS 系列) ===
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
    # 新增 NS 系列
    "NS1300": {"name": "鋼筋無輻射證明", "type": "doc"},
    "NS1900": {"name": "混凝土抗壓報告", "type": "doc"},
    "NS2200": {"name": "公會抽查紀錄表", "type": "doc"},
    "NS2400": {"name": "紅火蟻清查紀錄表", "type": "doc"},
}