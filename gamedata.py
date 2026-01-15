# gamedata.py

# === 基礎設定 ===
REGIONS = ["台北市 (Taipei)", "新北市 (New Taipei)"]
PROJECT_TYPES = ["素地新建 (Empty Land)", "拆併建照 (Demolition & Build)"]

# === 任務大水庫 (Master Task List) ===
# tags: 標記此任務屬於哪個地區或案型
# phase: 屬於遊戲的哪個階段 (Plan=計畫, Demo=拆除, Construct=放樣)
MASTER_TASKS = [
    # --- 通用任務 ---
    {"id": "T01", "name": "結構外審 (建築師)", "phase": "Plan", "type": "ALL", "region": "ALL", "desc": "等待建築師完成圖說"},
    {"id": "T02", "name": "跑照寶石收集", "phase": "Plan", "type": "ALL", "region": "ALL", "desc": "收集交通、公會等六大寶石"},
    
    # --- 拆除專屬任務 (只在拆併建出現) ---
    {"id": "D01", "name": "拆除執照申請", "phase": "Demo", "type": "DEMO", "region": "ALL", "desc": "取得拆除許可Buff"},
    {"id": "D02", "name": "B5 拆除廢棄物結案", "phase": "Demo", "type": "DEMO", "region": "ALL", "desc": "關鍵！未完成無法放樣"},
    {"id": "D03", "name": "鄰房鑑定 (拆除前)", "phase": "Demo", "type": "DEMO", "region": "ALL", "desc": "開啟防禦護盾"},

    # --- 地區特殊任務 ---
    {"id": "R01", "name": "台北市無紙化上傳", "phase": "Plan", "type": "ALL", "region": "Taipei", "desc": "使用虛擬桌面系統"},
    {"id": "R02", "name": "新北水土保持計畫", "phase": "Plan", "type": "ALL", "region": "New Taipei", "desc": "山坡地特殊任務"},
]

# === 放樣 BOSS 關卡資料 ===
SETTING_OUT_STEPS = [
    {"id": "S1", "name": "網路掛件", "desc": "系統檢核", "hp": 20},
    {"id": "S2", "name": "紙本掛件", "desc": "承辦核對", "hp": 20},
    {"id": "S3", "name": "現場會勘", "desc": "建築師與公務員到場", "hp": 30},
    {"id": "S4", "name": "文案核對", "desc": "圖說一致性", "hp": 15},
    {"id": "S5", "name": "簽核准用", "desc": "取得放樣核准函", "hp": 15},
]

# === 無紙化小遊戲資料 (保留) ===
NW_CODES = {
    "NW0100": {"name": "建築工程開工申報書", "type": "doc"},
    "NW3300": {"name": "施工計畫書", "type": "doc"},
    "NW5000": {"name": "配筋圖", "type": "drawing"},
}