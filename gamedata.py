# gamedata.py

# === Chapter 2: 六大寶石 (施工計畫子任務) ===
GEMS = {
    "GEM_GUILD": {"name": "公會寶石", "desc": "鄰房說明會 & 施工計畫外審", "type": "social"},
    "GEM_PIPE": {"name": "管線寶石", "desc": "五大管線圖資查詢", "type": "explore"},
    "GEM_TRAFFIC": {"name": "交通寶石", "desc": "交通維持計畫 (含塔吊)", "type": "strategy"},
    "GEM_SURVEY": {"name": "測量寶石", "desc": "路心樁及地界點復原", "type": "precision"},
    "GEM_SAFETY": {"name": "勞安寶石", "desc": "危險場所評估", "type": "defense"},
    "GEM_ADMIN": {"name": "建管寶石", "desc": "施工計畫書文件彙整", "type": "doc"},
}

# === Chapter 4: 放樣勘驗五大關卡 ===
SETTING_OUT_STEPS = [
    {"id": "S1", "name": "網路掛件", "desc": "系統檢核文件齊全度", "hp": 20},
    {"id": "S2", "name": "紙本掛件", "desc": "物理送件，承辦人核對", "hp": 20},
    {"id": "S3", "name": "現場會勘", "desc": "建築師與公務員親臨工地", "hp": 30}, # 魔王關
    {"id": "S4", "name": "文案核對", "desc": "圖說與現場一致性檢查", "hp": 15},
    {"id": "S5", "name": "簽核准用", "desc": "獲得最終核准函", "hp": 15},
]

# 保留原本的資料，以免舊程式報錯 (如果有的話)
TRIALS = {} 
NW_CODES = {}