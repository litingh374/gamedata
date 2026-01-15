# gamedata.py

# 定義 Stage 2 的七大試煉任務
TRIALS = {
    "T01": {"name": "繳交空污費", "category": "環保局 (綠)", "color": "success", "desc": "計算規模 -> 繳費 -> 取得收據"},
    "T02": {"name": "逕流廢水削減計畫", "category": "環保局 (綠)", "color": "success", "desc": "撰寫計畫 -> 上傳 -> 取得核定函"},
    "T03": {"name": "廢棄物處理計畫 (拆+建)", "category": "環保局 (綠)", "color": "success", "desc": "預估量 -> 尋找處理場 -> 取得管制編號"},
    "T04": {"name": "建管開工(無紙化)準備", "category": "建管處 (藍)", "color": "primary", "desc": "圖說掃描 -> 上傳系統 -> 狀態 Ready"},
    "T05": {"name": "拆除土方外運審查 (B5)", "category": "建管處 (藍)", "color": "primary", "desc": "規劃路線 -> 取得土方憑證"},
    "T06": {"name": "鄰房現況鑑定", "category": "公會/第三方 (橘)", "color": "warning", "desc": "聯絡公會 -> 拍照 -> 取得鑑定報告"},
    "T07": {"name": "拆除施工計畫", "category": "公會/第三方 (橘)", "color": "warning", "desc": "說明會 -> 審查會 -> 取得核備公文"},
}

# 建築師信物 (Stage 1)
ARCHITECT_ITEM = "建造執照 (Building Permit)"