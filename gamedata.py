# gamedata.py

# 任務編碼表 (無紙化系統的核心資料庫)
NW_CODES = {
    "NW0100": {"name": "建築工程開工申報書", "type": "doc", "required": True},
    "NW0200": {"name": "起造人名冊", "type": "doc", "required": False},
    "NW3300": {"name": "施工計畫書", "type": "doc", "required": True},
    "NW5000": {"name": "配筋圖", "type": "drawing", "format": "A3", "required": True},
    "NW5100": {"name": "圍籬綠美化圖說", "type": "drawing", "condition": "road_width >= 10"},
    "NW1100": {"name": "逕流廢水削減計畫核備函", "type": "doc", "condition": "large_scale"},
    "NW1500": {"name": "營造業承攬手冊", "type": "doc", "required": True},
    "NW3500": {"name": "工地主任證書", "type": "doc", "required": True},
}

# 可以在這裡擴充更多規則...