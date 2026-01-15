# gamedata.py

# 1. 任務編碼表 (無紙化系統的核心)
NW_CODES = {
    "NW0100": {"name": "建築工程開工申報書", "type": "doc", "required": True},
    "NW3300": {"name": "施工計畫書", "type": "doc", "required": True},
    "NW5000": {"name": "配筋圖", "type": "drawing", "format": "A3", "required": True},
    "NW5100": {"name": "圍籬綠美化圖說", "type": "drawing", "condition": "road_width >= 10"},
    # ... 把您提供的所有 NW 編碼填入這裡
}

# 2. 劇本設定 (Scenario)
SCENARIOS = {
    "Taipei_Standard": {
        "region": "Taipei",
        "strict_mode": True, # 開啟嚴格檢查
        "paperless": True
    },
    "NewTaipei_Lite": {
        "region": "NewTaipei",
        "strict_mode": False
    }
}