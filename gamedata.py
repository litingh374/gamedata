# gamedata.py

# === 基礎設定 ===
REGIONS = ["台北市 (Taipei)", "新北市 (New Taipei)"]
PROJECT_TYPES = ["素地新建 (Empty Land)", "拆併建照 (Demolition & Build)"]

# === Chapter 1: 開工申報 ===
TRIALS = {
    "T01": {"name": "空污費申報", "color": "success", "desc": "繳費取得收據"},
    "T02": {"name": "逕流廢水計畫", "color": "success", "desc": "環保局核定函"},
    "T03": {"name": "廢棄物計畫", "color": "success", "desc": "取得管制編號"},
    "T04": {"name": "建管開工(無紙化)", "color": "primary", "desc": "關鍵！上傳圖說"},
    "T05": {"name": "土方計畫 (B5)", "color": "primary", "desc": "土方憑證"},
    "T06": {"name": "鄰房現況鑑定", "color": "warning", "desc": "取得鑑定報告"},
    "T07": {"name": "施工前說明會", "color": "warning", "desc": "里長簽名確認"},
}

# === Chapter 2: 六大寶石 ===
GEMS = {
    "GEM_GUILD": {"name": "公會寶石", "desc": "施工計畫外審"},
    "GEM_PIPE": {"name": "管線寶石", "desc": "五大管線查詢"},
    "GEM_TRAFFIC": {"name": "交通寶石", "desc": "交維計畫"},
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

# === 無紙化小遊戲資料 ===
NW_CODES = {
    "NW0100": {"name": "建築工程開工申報書", "type": "doc"},
    "NW3300": {"name": "施工計畫書", "type": "doc"},
    "NW5000": {"name": "配筋圖", "type": "drawing"},
}