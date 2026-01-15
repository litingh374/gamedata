# gamedata.py

# === 基礎設定 ===
REGIONS = ["台北市 (Taipei)", "新北市 (New Taipei)"]
PROJECT_TYPES = ["素地新建 (Empty Land)", "拆併建照 (Demolition & Build)"]

# === 法規門檻 (Thresholds) ===
THRESHOLDS = {
    "POLLUTION_FACTOR": 4600,  # 面積 x 工期
    "B8_AREA": 500,            # B8 列管面積
    "B8_COST": 5000000,        # B8 列管造價 (500萬)
    "TRAFFIC_AREA": 10000,     # 交維計畫面積 (10000m2)
    "GREEN_BUILDING_COST": 50000000 # 綠建築 (5000萬 - 假設公有或特定條件)
}

# === Chapter 1: 拆除七大封印 ===
DEMO_SEALS = {
    "D01": {"name": "鄰房鑑定報告", "code": "NW2300", "desc": "必備！除非你敢簽切結書"},
    "D02": {"name": "B5 土方流向", "code": "NW2600", "desc": "確認廢土去處"},
    "D03": {"name": "B8 廢棄物計畫", "code": "NW2700", "desc": "確認垃圾去處"},
    "D04": {"name": "防空避難室撤除", "code": "Doc_Police", "desc": "向警察局申請(若有)"},
    "D05": {"name": "監拆報告書", "code": "NW2500", "desc": "建築師簽證"},
    "D06": {"name": "拆除施工計畫", "code": "NW2400", "desc": "營造廠撰寫"},
    "D07": {"name": "行政驗收(圖說抽查)", "code": "Check_Arch", "desc": "建照科圖說抽查"},
}

# === Chapter 2: 六大寶石 (施工計畫) ===
# 更新：交通寶石會根據面積變更難度
GEMS = {
    "GEM_GUILD": {"name": "公會寶石", "desc": "施工計畫外審"},
    "GEM_PIPE": {"name": "管線寶石", "desc": "五大管線查詢"},
    "GEM_TRAFFIC": {"name": "交通寶石", "desc": "交維計畫 (難度視規模而定)"},
    "GEM_SURVEY": {"name": "測量寶石", "desc": "路心樁復原"},
    "GEM_SAFETY": {"name": "勞安寶石", "desc": "危險場所評估"},
    "GEM_ADMIN": {"name": "建管寶石", "desc": "計畫書彙整"},
}

# === Chapter 5: 放樣 BOSS ===
SETTING_OUT_STEPS = [
    {"id": "S1", "name": "網路掛件", "desc": "系統檢核", "hp": 20},
    {"id": "S2", "name": "紙本掛件", "desc": "承辦核對", "hp": 20},
    {"id": "S3", "name": "現場會勘", "desc": "BOSS 現身", "hp": 30},
    {"id": "S4", "name": "文案核對", "desc": "圖說檢查", "hp": 15},
    {"id": "S5", "name": "簽核准用", "desc": "核准函", "hp": 15},
]

# === 無紙化編碼表 ===
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