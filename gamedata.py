# gamedata.py

# === Stage 1 & 2: 任務試煉資料 ===
TRIALS = {
    "T01": {"name": "繳交空污費", "category": "環保局 (綠)", "color": "success", "desc": "計算規模 -> 繳費 -> 取得收據"},
    "T02": {"name": "逕流廢水削減計畫", "category": "環保局 (綠)", "color": "success", "desc": "撰寫計畫 -> 上傳 -> 取得核定函"},
    "T03": {"name": "廢棄物處理計畫 (拆+建)", "category": "環保局 (綠)", "color": "success", "desc": "預估量 -> 尋找處理場 -> 取得管制編號"},
    "T04": {"name": "建管開工(無紙化)準備", "category": "建管處 (藍)", "color": "primary", "desc": "圖說掃描 -> 上傳系統 -> 狀態 Ready"},
    "T05": {"name": "拆除土方外運審查 (B5)", "category": "建管處 (藍)", "color": "primary", "desc": "規劃路線 -> 取得土方憑證"},
    "T06": {"name": "鄰房現況鑑定", "category": "公會/第三方 (橘)", "color": "warning", "desc": "聯絡公會 -> 拍照 -> 取得鑑定報告"},
    "T07": {"name": "拆除施工計畫", "category": "公會/第三方 (橘)", "color": "warning", "desc": "說明會 -> 審查會 -> 取得核備公文"},
}

ARCHITECT_ITEM = "建造執照 (Building Permit)"

# === Stage 2: 無紙化系統編碼表 ===
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