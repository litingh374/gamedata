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

# === 隨機事件庫 (Random Encounters) ===
RANDOM_EVENTS = [
    {
        "id": "E01",
        "title": "👻 幽靈管線突襲",
        "desc": "怪手挖到不明電纜！圖資上明明沒有...",
        "options": [
            {"text": "停工通報台電 (正規)", "effect": "delay", "val": 2, "msg": "工期延誤 2 週，但安全過關。"},
            {"text": "假裝沒看到埋回去 (賭博)", "effect": "risk", "val": 30, "msg": "省下時間，但風險值暴增 30%！"}
        ]
    },
    {
        "id": "E02",
        "title": "🐜 紅火蟻入侵",
        "desc": "工地發現紅火蟻丘！依規定需通報。",
        "options": [
            {"text": "聘請除蟲公司 (花錢)", "effect": "cost", "val": 50000, "msg": "花費 5 萬元，危機解除。"},
            {"text": "叫工班用熱水燙 (無效)", "effect": "fail", "val": 0, "msg": "被環保局稽查發現，勒令停工消毒！"}
        ]
    },
    {
        "id": "E03",
        "title": "🚪 拒絕鑑定戶",
        "desc": "隔壁 305 號住戶死不開門，無法鑑定。",
        "options": [
            {"text": "寄存證信函 (自保)", "effect": "safe", "val": 0, "msg": "已保留法律證據，未來免責。"},
            {"text": "不管他直接拆 (高風險)", "effect": "risk", "val": 50, "msg": "未來鄰損求償無抗辯能力！風險+50%"}
        ]
    },
    {
        "id": "E04",
        "title": "🌪️ 颱風警報",
        "desc": "強颱來襲！需進行防颱措施。",
        "options": [
            {"text": "全面巡檢加固 (耗時)", "effect": "delay", "val": 1, "msg": "花費 1 週做防颱，平安度過。"},
            {"text": "賭它不會來 (賭博)", "effect": "disaster", "val": 0, "msg": "圍籬倒塌壓壞路邊名車！賠償 20 萬！"}
        ]
    },
    {
        "id": "E05",
        "title": "👮‍♂️ 承辦人換人",
        "desc": "原本的承辦人退休了，新來的超級嚴格...",
        "options": [
            {"text": "配合補件 (認命)", "effect": "delay", "val": 3, "msg": "審查重新起算，延誤 3 週。"},
            {"text": "找議員關切 (特權)", "effect": "karma", "val": 0, "msg": "雖然過了，但被建管處列入黑名單。"}
        ]
    }
]

# === 其他資料 (Demo Seals, Gems, Steps, NW Codes 保持不變) ===
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

GEMS = {
    "GEM_GUILD": {"name": "公會寶石", "desc": "施工計畫外審"},
    "GEM_PIPE": {"name": "管線寶石", "desc": "五大管線查詢"},
    "GEM_TRAFFIC": {"name": "交通寶石", "desc": "交維計畫"},
    "GEM_SURVEY": {"name": "測量寶石", "desc": "路心樁復原"},
    "GEM_SAFETY": {"name": "勞安寶石", "desc": "危險場所評估"},
    "GEM_ADMIN": {"name": "建管寶石", "desc": "計畫書彙整"},
}

SETTING_OUT_STEPS = [
    {"id": "S1", "name": "網路掛件", "desc": "系統檢核", "hp": 20},
    {"id": "S2", "name": "紙本掛件", "desc": "承辦核對", "hp": 20},
    {"id": "S3", "name": "現場會勘", "desc": "BOSS 現身", "hp": 30},
    {"id": "S4", "name": "文案核對", "desc": "圖說檢查", "hp": 15},
    {"id": "S5", "name": "簽核准用", "desc": "核准函", "hp": 15},
]

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
}