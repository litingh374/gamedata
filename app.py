import streamlit as st
import time
import random

# ==========================================
# 1. 遊戲資料庫 (Data) - 已加入新手注意事項
# ==========================================

REGIONS = ["台北市 (Taipei)", "新北市 (New Taipei)"]
PROJECT_TYPES = ["素地新建 (Empty Land)", "拆併建照 (Demolition & Build)"]

THRESHOLDS = {
    "POLLUTION_FACTOR": 4600,
    "B8_AREA": 500,
    "B8_COST": 5000000,
    "TRAFFIC_AREA": 10000,
    "GREEN_BUILDING_COST": 50000000
}

RESOURCE_RATES = {"STEEL": 0.15, "CONCRETE": 0.8}

ENV_OPTIONS = {
    "LOW": {"name": "基本防護 (帆布+人工沖洗)", "cost": 50000, "risk": 40, "desc": "省錢，但容易被環保局開單。"},
    "MID": {"name": "標準防護 (洗車台+沉澱池)", "cost": 150000, "risk": 10, "desc": "CP值高，符合法規要求。"},
    "HIGH": {"name": "完美防護 (自動洗車+汙水處理機)", "cost": 400000, "risk": 0, "desc": "極致環保，稽查員看了都比讚。"}
}

DIPLOMACY_STRATEGIES = {
    "HAWK": {"name": "依法行政 (鷹派)", "cost": 0, "anger": 30, "desc": "不囉嗦，照規矩來。容易累積民怨。"},
    "DOVE": {"name": "敦親睦鄰 (鴿派)", "cost": 80000, "anger": -20, "desc": "送禮賠笑，花錢消災。鄰居心情好。"}
}

DEMO_SEALS = {
    "D01": {"name": "鄰房現況鑑定報告書", "code": "NW2300"},
    "D02": {"name": "營建剩餘土石方(B5)處理計畫", "code": "NW2600"},
    "D03": {"name": "營建混合物(B8)處理計畫", "code": "NW2700"},
    "D04": {"name": "防空避難室撤除核准函", "code": "Doc_Police"},
    "D05": {"name": "建築師監拆報告書", "code": "NW2500"},
    "D06": {"name": "建築物拆除施工計畫書", "code": "NW2400"},
    "D07": {"name": "行政驗收 (建照科圖說抽查)", "code": "Check_Arch"},
}

CONSTRUCTION_METHODS = {
    "BOTTOM_UP": {
        "name": "順打工法 (Bottom-Up)",
        "desc": "傳統工法，先挖到底再蓋上來。技術成熟但開挖風險高。",
        "cost_mod": 0, "time_mod": 0, "risk_mod": 10
    },
    "TOP_DOWN": {
        "name": "逆打工法 (Top-Down)",
        "desc": "地上地下同時施工。速度快，但技術難度高，需額外設備。",
        "cost_mod": 5000000, "time_mod": -8, "risk_mod": 20
    }
}

TEAM_MEMBERS = {
    "DIRECTOR": [
        {"id": "DIR_SENIOR", "name": "資深主任 (老王)", "salary": 80000, "skill": "免疫刁難", "req": "NW3500"},
        {"id": "DIR_JUNIOR", "name": "菜鳥主任 (阿明)", "salary": 40000, "skill": "容易忘記帶章", "req": "NW3500"}
    ],
    "PE": [
        {"id": "PE_FULL", "name": "專任技師 (強哥)", "salary": 60000, "skill": "審查加速"},
        {"id": "PE_PART", "name": "兼職技師 (小林)", "salary": 20000, "skill": "無"}
    ],
    "SAFETY": [
        {"id": "SAF_PRO", "name": "專職勞安 (安安)", "salary": 45000, "skill": "意外防護罩"},
        {"id": "SAF_NONE", "name": "無 (違法省錢)", "salary": 0, "skill": "高風險"}
    ]
}

GEMS = {
    "GEM_GUILD": {"name": "公會寶石", "desc": "施工計畫外審"},
    "GEM_PIPE": {"name": "管線寶石", "desc": "五大管線查詢"},
    "GEM_TRAFFIC": {"name": "交通寶石", "desc": "交維計畫"},
    "GEM_SURVEY": {"name": "測量寶石", "desc": "路心樁復原"},
    "GEM_SAFETY": {"name": "勞安寶石", "desc": "危險場所評估"},
    "GEM_ADMIN": {"name": "建管寶石", "desc": "計畫書彙整"},
}

RANDOM_EVENTS = [
    {"id": "E01", "title": "👻 幽靈管線突襲", "desc": "怪手挖到不明電纜！圖資上明明沒有...", "options": [{"text": "停工通報", "effect": "delay", "val": 2, "msg": "工期延誤2週"}, {"text": "偷埋回去", "effect": "risk", "val": 30, "msg": "風險+30%"}]},
    {"id": "E06", "title": "🚛 違規傾倒", "desc": "土方司機把廢土倒在路邊被抓到了！", "options": [{"text": "繳罰單並悔過", "effect": "cost", "val": 100000, "msg": "罰款10萬"}, {"text": "說是司機個人行為", "effect": "risk", "val": 20, "msg": "推卸責任，風險+20%"}]},
    {"id": "E07", "title": "🧱 氯離子超標", "desc": "混凝土車快篩發現數值異常！", "options": [{"text": "整車退貨", "effect": "delay", "val": 1, "msg": "進度延誤1週"}, {"text": "賭一把灌下去", "effect": "disaster", "val": 0, "msg": "變成海砂屋！Game Over"}]}
]

# === [重要更新] 依據真實公文增加「新手注意事項 (tips)」 ===
NW_CODES = {
    "NW0100": {
        "name": "B11-1 建築工程開工申報書", 
        "type": "doc",
        "tips": "⚠️ 需一式7份(山坡地8份)。起造人、承造人、監造人皆需用印。若為變更設計案，需確認是否已完成變更程序。"
    },
    "NW0300": {
        "name": "承造人施工計畫書簽章負責表", 
        "type": "doc",
        "tips": "⚠️ 確認表上人員(專任工程人員、工地主任)與營造業手冊登記一致。簽名欄位不可蓋章代替。"
    },
    "NW1000": {
        "name": "營建工程空氣污染防制費繳款收據", 
        "type": "doc",
        "tips": "⚠️ 這是「第一級」或「第二級」費率？請先上環保局網站試算。繳費後需掃描收據上傳，不可只傳申報單。"
    },
    "NW1100": {
        "name": "逕流廢水削減計畫核備函", 
        "type": "doc",
        "tips": "⚠️ 觸發門檻：基地面積 × 工期 > 4600。必須先向環保局取得「核備函」才能報開工，注意公文往返時間約需 14-21 天。"
    },
    "NW2300": {
        "name": "鄰房現況鑑定報告書 (公會備查函)", 
        "type": "doc",
        "tips": "⚠️ 拆除工程的「保命符」。必須在拆除前完成鑑定並取得公會備查函。若因鄰居拒絕鑑定，需檢附「存證信函」證明已盡力。"
    },
    "NW2400": {
        "name": "建築物拆除施工計畫書 (B14-5)", 
        "type": "doc",
        "tips": "⚠️ 需依內政部訂頒格式撰寫。若有地下室，需包含地下室回填或支撐計畫。"
    },
    "NW2500": {
        "name": "建築物監拆報告書 (B14-3)", 
        "type": "doc",
        "tips": "⚠️ 由建築師簽證。需檢附現場拆除前照片，證明尚未動工。"
    },
    "NW2600": {
        "name": "營建剩餘土石方處理計畫 (B5核准函)", 
        "type": "doc",
        "tips": "⚠️ 俗稱「棄土證明」。需確認土資場是否有剩餘收容容量。兩階段申報：先報計畫(取得核准函)，開挖前再報流向。"
    },
    "NW2700": {
        "name": "營建混合物(廢棄物)處理計畫 (B8核准函)", 
        "type": "doc",
        "tips": "⚠️ 俗稱「垃圾處理」。環保局管轄。若新建工程面積>500m²或造價>500萬即需辦理。"
    },
    "NW3300": {
        "name": "建築工程施工計畫書 (含防災/品管)", 
        "type": "doc",
        "tips": "⚠️ 核心文件。若基地開挖深度>12m或樓高>50m，需先完成「施工計畫外審」(需公會召開委員會審查)。"
    },
    "NW3500": {
        "name": "工地主任執業證 (含公會會員證)", 
        "type": "doc",
        "tips": "⚠️ 需檢附：1.執業證(有效期限內) 2.公會會員證 3.回訓證明。工地主任必須是「專任」，不能掛名其他案子。"
    },
    "NW5000": {
        "name": "結構配筋圖 (A3掃描檔)", 
        "type": "drawing",
        "tips": "⚠️ 必須掃描成 A3 格式 (300dpi 以上)。需包含柱、樑、版、牆配筋詳圖。電子檔名編碼務必正確。"
    },
    "NW5100": {
        "name": "安全圍籬綠美化及防溢座圖說", 
        "type": "drawing",
        "tips": "⚠️ 台北市規定：臨路寬度>10公尺，圍籬需50%以上綠美化。防溢座高度需符合規定(通常30-60cm)。"
    },
    "NS1300": {
        "name": "鋼筋無輻射證明書", 
        "type": "doc",
        "tips": "⚠️ 每一批進場鋼筋都要附。需確認爐號與出廠證明相符。"
    },
    "NS1900": {
        "name": "混凝土抗壓強度試驗報告", 
        "type": "doc",
        "tips": "⚠️ 時間差陷阱！28天強度報告出來後才能報下一層樓。記得提早送實驗室。"
    },
    "NS2200": {
        "name": "建築師公會抽查紀錄表", 
        "type": "doc",
        "tips": "⚠️ 2樓版(或其他指定樓層)勘驗前，需由公會派員抽查。缺失改善完畢才能申報勘驗。"
    },
    "NS2400": {
        "name": "紅火蟻清查紀錄表", 
        "type": "doc",
        "tips": "⚠️ 每月1-5號需重新填寫並上傳。若發現紅火蟻需通報並投藥。"
    },
}

# ==========================================
# 2. 核心程式邏輯 (Game Logic)
# ==========================================

if 'game_state' not in st.session_state:
    st.session_state.game_state = {
        "stage": "Launcher",
        "config": {},
        "current_week": 1,
        "total_weeks": 52,
        "budget_used": 0,
        "risk_level": 0,
        "active_event": None,
        "project_data": {
            "area": 0, "area_unknown": False,
            "duration": 0, "duration_unknown": False,
            "cost": 0, "cost_unknown": False,
            "floor_area": 0, "floor_area_unknown": False,
        },
        "hicos_connected": False,
        "demo_seals_cleared": [],
        "doing_paperless": False,
        "commencement_done": False,
        "ch1_strategy_done": False,
        "ch1_tasks": {}, 
        "resource_accurate": False,
        "collected_gems": [],
        "plan_approved": False,
        "strategy": {"method": None, "team": {}, "layout": {}}, 
        "is_demo_shield_active": False,
        "demo_progress": 0,
        "b5_closed": False,
        "demo_phase_passed": False,
        "guide_wall_progress": 0,
        "guide_wall_inspected": False,
        "boss_hp": 100,
        "excavation_progress": 0,
        "shoring_installed": False,
        "foundation_done": False,
        "current_floor": "B1",
        "floor_status": {
            "B1": {"rebar": False, "form": False, "pour": False, "report": False, "test_week": None},
            "1F": {"rebar": False, "form": False, "pour": False, "report": False, "test_week": None},
            "2F": {"rebar": False, "form": False, "pour": False, "report": False, "test_week": None},
        },
        "logs": [],
        "paperless_raw_files": [
            "B11-1_開工申報書_已用印.docx", 
            "空污費繳款收據_109年.jpg", 
            "拆除施工計畫書_核定版.pdf",
            "鄰房鑑定報告_公會函.pdf", 
            "逕流廢水核備函.jpg", 
            "工地主任執業證_阿明.pdf",
            "結構配筋圖_V2_A3.dwg", 
            "工地主任自拍照.jpg"
        ],
        "paperless_processed_files": [],
        "g02_checked": False,
    }

def main():
    st.set_page_config(page_title="跑照大作戰：完全修復版", layout="wide", page_icon="🏗️")
    
    if st.session_state.game_state["active_event"]:
        render_event_dialog()
        return

    if st.session_state.game_state["stage"] == "Launcher":
        render_launcher()
    else:
        render_main_game()

# --- 隨機事件處理 ---
def render_event_dialog():
    evt = st.session_state.game_state["active_event"]
    st.error(f"🚨 突發狀況：{evt['title']}")
    st.markdown(f"**{evt['desc']}**")
    c1, c2 = st.columns(2)
    if c1.button(f"🅰️ {evt['options'][0]['text']}", use_container_width=True): resolve_event(evt['options'][0])
    if c2.button(f"🅱️ {evt['options'][1]['text']}", use_container_width=True): resolve_event(evt['options'][1])

def resolve_event(opt):
    eff, val, msg = opt['effect'], opt['val'], opt['msg']
    if eff == "delay": 
        st.session_state.game_state["current_week"] += val
        st.toast(msg, icon="🐢")
    elif eff == "risk":
        st.session_state.game_state["risk_level"] += val
        st.toast(msg, icon="🔥")
    elif eff == "cost":
        st.session_state.game_state["budget_used"] += val
        st.toast(msg, icon="💸")
    elif eff == "disaster":
        st.error("災難發生！Game Over")
        st.session_state.game_state["risk_level"] = 100
    st.session_state.game_state["active_event"] = None
    add_log(f"事件：{msg}")
    st.rerun()

# --- 遊戲大廳 ---
def render_launcher():
    st.title("🏗️ 專案啟動：工程情報輸入")
    c1, c2 = st.columns(2)
    if c1.button("🟢 新手村 (小型透天)", use_container_width=True): set_preset("small")
    if c2.button("🔴 挑戰模式 (大型建案)", use_container_width=True): set_preset("large")

    st.markdown("---")
    st.subheader("📝 自定義參數")
    with st.container(border=True):
        rc1, rc2 = st.columns(2)
        region = rc1.radio("伺服器", REGIONS)
        p_type = rc2.radio("劇本", PROJECT_TYPES)
        
        cc1, cc2 = st.columns([3, 1])
        area_unk = cc2.checkbox("不清楚面積")
        area = cc1.number_input("基地面積", value=100, disabled=area_unk)
        cc3, cc4 = st.columns([3, 1])
        dur_unk = cc4.checkbox("不清楚工期")
        dur = cc3.number_input("預計工期", value=6, disabled=dur_unk)
        cc5, cc6 = st.columns([3, 1])
        floor_unk = cc6.checkbox("不清楚樓地板")
        floor_area = cc5.number_input("總樓地板面積", value=300, disabled=floor_unk)

        if not area_unk and not dur_unk and area * dur >= THRESHOLDS["POLLUTION_FACTOR"]:
            st.error("⚠️ 係數過高：將觸發逕流廢水副本！")

    if st.button("🚀 生成專案", type="primary", use_container_width=True):
        st.session_state.game_state["config"] = {"region": region, "type": p_type, "is_mrt": False}
        st.session_state.game_state["project_data"] = {
            "area": area, "area_unknown": area_unk,
            "duration": dur, "duration_unknown": dur_unk,
            "cost": 3000000, "cost_unknown": False,
            "floor_area": floor_area, "floor_area_unknown": floor_unk
        }
        if "素地" in p_type:
            st.session_state.game_state["demo_phase_passed"] = True
            st.session_state.game_state["b5_closed"] = True
            st.session_state.game_state["is_demo_shield_active"] = True
        st.session_state.game_state["stage"] = "MainGame"
        st.rerun()

def set_preset(mode):
    if mode == "small":
        cfg = {"region": "台北市", "type": "素地新建", "is_mrt": False}
        p_data = {"area": 100, "duration": 6, "cost": 3000000, "floor_area": 300, "area_unknown":False, "duration_unknown":False, "cost_unknown":False, "floor_area_unknown":False}
        st.session_state.game_state["demo_phase_passed"] = True
        st.session_state.game_state["b5_closed"] = True
        st.session_state.game_state["is_demo_shield_active"] = True
    else:
        cfg = {"region": "台北市", "type": "拆併建照", "is_mrt": True}
        p_data = {"area": 3000, "duration": 24, "cost": 200000000, "floor_area": 15000, "area_unknown":False, "duration_unknown":False, "cost_unknown":False, "floor_area_unknown":False}
    st.session_state.game_state["config"] = cfg
    st.session_state.game_state["project_data"] = p_data
    st.session_state.game_state["stage"] = "MainGame"
    st.rerun()

# --- 主遊戲介面 ---
def render_main_game():
    if st.session_state.game_state["doing_paperless"]:
        render_paperless_minigame()
        return

    cfg = st.session_state.game_state["config"]
    
    with st.sidebar:
        st.title(f"Week {st.session_state.game_state['current_week']}")
        st.metric("風險值", f"{st.session_state.game_state['risk_level']}%")
        st.metric("已用預算", f"${st.session_state.game_state['budget_used']:,}")
        
        if st.button("📅 推進一週 (晨會)", type="primary"):
            advance_week()
        st.divider()
        st.caption("專案日誌")
        for log in st.session_state.game_state["logs"][-5:]:
            st.text(log)
        if st.button("🔄 重置遊戲"):
            st.session_state.clear()
            st.rerun()

    st.title(f"🏗️ {cfg['type']}")
    
    tabs = st.tabs(["Ch1 開工", "Ch2 計畫(戰略)", "Ch3 拆除", "Ch4 導溝", "Ch5 放樣", "Ch6 地下城", "Ch7 巴別塔"])
    
    with tabs[0]: render_chapter_1()
    with tabs[1]: render_chapter_2()
    with tabs[2]: render_chapter_3()
    with tabs[3]: render_chapter_4()
    with tabs[4]: render_chapter_5()
    with tabs[5]: render_chapter_6()
    with tabs[6]: render_chapter_7()

def advance_week():
    st.session_state.game_state["current_week"] += 1
    if random.random() < 0.2:
        st.session_state.game_state["active_event"] = random.choice(RANDOM_EVENTS)
    st.rerun()

# ==========================================
# Ch1: 開工申報
# ==========================================
def render_chapter_1():
    st.header("📂 第一章：開工申報 (戰略部署)")
    p_data = st.session_state.game_state["project_data"]
    
    env_choice = "LOW"
    dip_choice = "HAWK"
    g02 = False
    green_ok = False
    seals_ok = False
    
    with st.expander("📊 戰略與資源配置", expanded=True):
        if p_data["floor_area_unknown"]:
            st.warning("🔒 樓地板面積不明，無法進行資源精算。")
        else:
            col_r1, col_r2 = st.columns(2)
            with col_r1:
                ref_steel = p_data["floor_area"] * RESOURCE_RATES["STEEL"]
                est_steel = st.slider("預估鋼筋 (噸)", int(ref_steel*0.5), int(ref_steel*2.0), int(ref_steel*0.8))
            with col_r2:
                ref_conc = p_data["floor_area"] * RESOURCE_RATES["CONCRETE"]
                est_conc = st.slider("預估混凝土 (m³)", int(ref_conc*0.5), int(ref_conc*2.0), int(ref_conc*1.2))
            
            steel_acc = abs(est_steel - ref_steel) / ref_steel
            conc_acc = abs(est_conc - ref_conc) / ref_conc
            st.session_state.game_state["resource_accurate"] = steel_acc < 0.1 and conc_acc < 0.1

        col_e1, col_e2 = st.columns(2)
        with col_e1:
            st.markdown("**環保防禦**")
            env_choice = st.radio("選擇防護", list(ENV_OPTIONS.keys()), format_func=lambda x: f"{ENV_OPTIONS[x]['name']} (${ENV_OPTIONS[x]['cost']:,})")
            st.caption(ENV_OPTIONS[env_choice]['desc'])
        with col_e2:
            st.markdown("**鄰里外交**")
            dip_choice = st.select_slider("外交手段", options=list(DIPLOMACY_STRATEGIES.keys()), format_func=lambda x: DIPLOMACY_STRATEGIES[x]['name'])
            st.caption(DIPLOMACY_STRATEGIES[dip_choice]['desc'])

    st.markdown("---")

    col_quest, col_system = st.columns([3, 2])
    
    with col_quest:
        config_type = st.session_state.game_state["config"]["type"]
        
        if "拆併建" in config_type:
            st.subheader("🔥 拆除七大封印")
            with st.container(border=True):
                cols = st.columns(3)
                completed = st.session_state.game_state["demo_seals_cleared"]
                for sid, data in DEMO_SEALS.items():
                    is_done = sid in completed
                    icon = "✅" if is_done else "🔒"
                    with cols[int(sid[-1])%3]:
                        st.markdown(f"**{icon} {data['name']}**")
                        if not is_done:
                            if sid == "D01":
                                if st.button("鑑定", key=sid):
                                    st.session_state.game_state["demo_seals_cleared"].append(sid)
                                    st.session_state.game_state["is_demo_shield_active"] = True
                                    st.rerun()
                                if st.button("簽切結", key=f"{sid}_risk"):
                                    st.session_state.game_state["demo_seals_cleared"].append(sid)
                                    st.session_state.game_state["risk_level"] += 50
                                    st.rerun()
                            else:
                                if st.button("執行", key=sid):
                                    st.session_state.game_state["demo_seals_cleared"].append(sid)
                                    st.rerun()
            seals_ok = len(completed) == 7
        else:
            seals_ok = True

        st.subheader("🌳 環保任務")
        with st.container(border=True):
            st.checkbox("G01 空污費申報 (NW1000)", value=True, disabled=True)
            
            g02 = False 
            
            if p_data["area_unknown"] or p_data["duration_unknown"]:
                st.info("🔒 G02: 資料不明...")
                if st.button("📞 打電話確認"):
                    p_data["area"], p_data["duration"] = 1000, 10
                    p_data["area_unknown"] = False
                    p_data["duration_unknown"] = False
                    st.rerun()
            else:
                f = p_data["area"] * p_data["duration"]
                if f >= THRESHOLDS["POLLUTION_FACTOR"]:
                    chk_val = st.session_state.game_state.get("g02_checked", False)
                    g02 = st.checkbox(f"G02 逕流廢水 (係數{f}) (NW1100)", value=chk_val, key="g02_box")
                    st.session_state.game_state["g02_checked"] = g02
                else:
                    st.write("~~G02 逕流廢水~~ (免辦)")
                    g02 = True
            
            green_ok = g02

    with col_system:
        st.subheader("💻 數位憑證")
        if not st.session_state.game_state["hicos_connected"]:
            if st.button("插入：工商憑證卡"):
                time.sleep(0.5)
                st.session_state.game_state["hicos_connected"] = True
                st.rerun()
        else:
            st.success("🟢 HiCOS 已連線")
            if seals_ok and green_ok:
                if st.button("進入虛擬桌面 (上傳)", type="primary"):
                    st.session_state.game_state["doing_paperless"] = True
                    st.rerun()
            else:
                st.warning("🔒 任務未解鎖")
                
            if st.session_state.game_state["commencement_done"]:
                if not st.session_state.game_state.get("ch1_strategy_done"):
                    st.session_state.game_state["ch1_strategy_done"] = True
                    st.session_state.game_state["budget_used"] += ENV_OPTIONS[env_choice]["cost"]
                    st.session_state.game_state["budget_used"] += DIPLOMACY_STRATEGIES[dip_choice]["cost"]
                    st.session_state.game_state["risk_level"] += DIPLOMACY_STRATEGIES[dip_choice]["anger"]
                    if st.session_state.game_state.get("resource_accurate"):
                        st.toast("🎯 資源預估神準！獎勵預算！")
                        st.session_state.game_state["budget_used"] -= 50000
                st.success("🎉 開工申報完成！請前往第二章。")

# --- 無紙化小遊戲 ---
def render_paperless_minigame():
    st.title("💻 台北市無紙化上傳系統")
    st.info("任務：請選擇左側文件，並配對正確的 NW 編碼。注意右側的「小撇步」提示！")
    
    if st.button("🔙 放棄"): st.session_state.game_state["doing_paperless"] = False; st.rerun()

    c_ws, c_list = st.columns([2, 1])
    with c_ws:
        st.subheader("🛠️ 轉檔工作區")
        with st.container(border=True):
            col_a, col_b, col_c = st.columns([2, 2, 1])
            raws = st.session_state.game_state["paperless_raw_files"]
            sel_raw = col_a.selectbox("選擇原始檔", raws) if raws else None
            
            # 這裡顯示正式名稱
            code_opts = ["請選擇..."] + list(NW_CODES.keys())
            sel_code = col_b.selectbox("NW 編碼", code_opts)
            
            # --- [新增] 動態顯示新手注意事項 (Tips) ---
            if sel_code != "請選擇...":
                item_data = NW_CODES[sel_code]
                st.info(f"💡 **申辦小撇步**\n\n{item_data['tips']}")
                st.caption(f"正式名稱：{item_data['name']}")
            # ----------------------------------------

            if col_c.button("轉檔 ➡️", type="primary", disabled=not sel_raw):
                st.session_state.game_state["paperless_raw_files"].remove(sel_raw)
                clean_name = sel_raw.split('.')[0].replace("_用印","").replace("_核定","")
                new_name = f"{sel_code}_{clean_name}.pdf"
                st.session_state.game_state["paperless_processed_files"].append(new_name)
                st.toast(f"已轉檔：{new_name}")
                st.rerun()
        
        st.write("#### 準備上傳")
        processed = st.session_state.game_state["paperless_processed_files"]
        to_upload = st.multiselect("勾選上傳", processed, default=processed)
        
        if st.button("🚀 確認送出", type="primary", use_container_width=True):
            if any("NW0100" in f for f in to_upload):
                st.session_state.game_state["commencement_done"] = True
                st.session_state.game_state["doing_paperless"] = False
                st.balloons()
                add_log("線上掛號成功。")
                st.rerun()
            else:
                st.error("退件：缺少 NW0100 (開工申報書)！")

    with c_list:
        st.markdown("📜 **文件編碼速查**")
        # 顯示完整名稱
        data = [{"代碼": k, "文件名稱": v["name"]} for k, v in NW_CODES.items()]
        st.dataframe(data, hide_index=True)

# --- Ch2: 施工計畫 ---
def render_chapter_2():
    st.header("📜 第二章：施工計畫 (戰略部署)")
    if not st.session_state.game_state["commencement_done"]:
        st.warning("🔒 鎖定中：請先完成第一章。")
        return
    
    sel_key = "BOTTOM_UP"
    dir_valid = False
    layout_valid = False
    sel_dir = TEAM_MEMBERS["DIRECTOR"][0]
    sel_pe = TEAM_MEMBERS["PE"][0]
    sel_saf = TEAM_MEMBERS["SAFETY"][0]
    m_data = CONSTRUCTION_METHODS[sel_key]

    st.subheader("1. 決定施工戰略")
    curr_method = st.session_state.game_state["strategy"].get("method", "BOTTOM_UP")
    m_opts = list(CONSTRUCTION_METHODS.keys())
    m_lbls = [f"{k}: {v['name']}" for k, v in CONSTRUCTION_METHODS.items()]
    try:
        idx = m_opts.index(curr_method)
    except ValueError:
        idx = 0
    sel_lbl = st.radio("選擇工法", m_lbls, index=idx)
    sel_key = m_opts[m_lbls.index(sel_lbl)]
    m_data = CONSTRUCTION_METHODS[sel_key]
    st.info(f"💡 {m_data['desc']} | 成本 {m_data['cost_mod']:,} | 風險 +{m_data['risk_mod']}%")
    
    st.markdown("---")
    st.subheader("2. 組建黃金陣容")
    c_p1, c_p2, c_p3 = st.columns(3)
    
    with c_p1:
        st.markdown("👷 **工地主任**")
        has_cert = any("NW3500" in f for f in st.session_state.game_state["paperless_processed_files"])
        dir_opts = {m["name"]: m for m in TEAM_MEMBERS["DIRECTOR"]}
        sel_dir_name = st.selectbox("指派人選", list(dir_opts.keys()))
        sel_dir = dir_opts[sel_dir_name]
        
        if sel_dir["id"] == "DIR_SENIOR" and not has_cert:
            st.error("❌ 資格不符：缺少 NW3500 (請回 Ch1 製作)")
            dir_valid = False
        else:
            st.caption(f"薪資: {sel_dir['salary']}")
            dir_valid = True

    with c_p2:
        st.markdown("🏗️ **專任技師**")
        pe_opts = {m["name"]: m for m in TEAM_MEMBERS["PE"]}
        sel_pe_name = st.selectbox("指派技師", list(pe_opts.keys()))
        sel_pe = pe_opts[sel_pe_name]

    with c_p3:
        st.markdown("⛑️ **勞安人員**")
        saf_opts = {m["name"]: m for m in TEAM_MEMBERS["SAFETY"]}
        sel_saf_name = st.selectbox("指派勞安", list(saf_opts.keys()))
        sel_saf = saf_opts[sel_saf_name]
        if sel_saf["id"] == "SAF_NONE": st.warning("⚠️ 高風險！")

    st.markdown("---")
    st.subheader("3. 工地配置")
    l1, l2, l3 = st.columns(3)
    gate = l1.selectbox("大門", ["臨路側(正確)", "轉角(違規)"])
    office = l2.selectbox("工務所", ["空地(正確)", "開挖區(危險)"])
    crane = l3.selectbox("塔吊", ["基地中心(正確)", "路邊(違法)"])
    layout_valid = (gate == "臨路側(正確)") and (office == "空地(正確)") and (crane == "基地中心(正確)")

    st.markdown("---")
    st.subheader("4. 文件彙整")
    collected = st.session_state.game_state["collected_gems"]
    cols = st.columns(3)
    for i, (k, d) in enumerate(GEMS.items()):
        with cols[i%3]:
            if k in collected:
                st.button(f"✅ {d['name']}", key=k, disabled=True)
            else:
                if st.button(f"獲取 {d['name']}", key=k):
                    st.session_state.game_state["collected_gems"].append(k)
                    st.rerun()
    
    st.markdown("---")
    if st.button("✨ 送出施工計畫書 (合成)", type="primary", use_container_width=True):
        if len(collected) < 6:
            st.error("文件未齊！")
        elif not dir_valid:
            st.error("主任資格不符！")
        elif not layout_valid:
            st.error("配置違規！")
        else:
            st.session_state.game_state["plan_approved"] = True
            st.session_state.game_state["strategy"] = {"method": sel_key, "team": {"dir": sel_dir, "pe": sel_pe, "saf": sel_saf}}
            cost = m_data['cost_mod'] + sel_dir['salary'] + sel_pe['salary'] + sel_saf['salary']
            st.session_state.game_state["budget_used"] += cost
            st.session_state.game_state["total_weeks"] += m_data['time_mod']
            st.session_state.game_state["risk_level"] += m_data['risk_mod']
            if sel_dir["id"] == "DIR_JUNIOR": st.session_state.game_state["risk_level"] += 10
            if sel_saf["id"] == "SAF_NONE": st.session_state.game_state["risk_level"] += 50
            
            st.balloons()
            st.success("✅ 計畫核定！戰略生效。")
            st.rerun()

    if st.session_state.game_state["plan_approved"]:
        st.success("✅ 施工計畫已核定")

# --- Ch3: 拆除整備 ---
def render_chapter_3():
    st.header("🚜 第三章：拆除整備")
    if not st.session_state.game_state["plan_approved"]:
        st.warning("🔒 鎖定中：請先完成第二章。")
        return

    config_type = st.session_state.game_state["config"]["type"]
    if "素地" in config_type:
        st.success("✅ 素地新建：本章節自動通過。")
        st.session_state.game_state["demo_phase_passed"] = True
        return

    st.info("⚠️ 拆併建模式：請執行拆除。")
    has_shield = st.session_state.game_state["is_demo_shield_active"]
    risk = st.session_state.game_state["risk_level"]
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("辦公室作業")
        st.write(f"🛡️ 護盾狀態：{'✅ 開啟' if has_shield else '❌ 無 (風險!)'}")
        if st.button("B5 廢棄物結案"):
            st.session_state.game_state["b5_closed"] = True
            st.success("B5 已結案")
            add_log("B5 結案完成。")
        
        if st.session_state.game_state["b5_closed"]:
            st.info("✅ B5 狀態：已結案")
        else:
            st.warning("❌ B5 狀態：未結案 (影響放樣)")

    with c2:
        st.subheader("現場作業")
        if st.button("執行拆除作業"):
            strat = st.session_state.game_state.get("strategy", {})
            no_saf = strat.get("team", {}).get("saf", {}).get("id") == "SAF_NONE"
            actual_risk = risk + (50 if no_saf else 0)
            
            if actual_risk > 0 and random.random() < (actual_risk / 100):
                st.error("💥 發生嚴重鄰損/工安意外！")
                st.session_state.game_state["risk_level"] += 20
                add_log("鄰損發生！工程暫停。")
            else:
                st.session_state.game_state["demo_progress"] = 100
                st.success("拆除完成！(運氣不錯)")
                add_log("拆除作業完成。")

    if st.session_state.game_state["demo_progress"] >= 100:
        st.session_state.game_state["demo_phase_passed"] = True
        st.success("🌟 拆除階段完成！")

# --- Ch4: 導溝勘驗 ---
def render_chapter_4():
    st.header("🧱 第四章：導溝勘驗")
    if not st.session_state.game_state["plan_approved"]:
        st.warning("🔒 鎖定中：請先完成第二章。")
        return
    if not st.session_state.game_state["demo_phase_passed"]:
        st.warning("🔒 鎖定中：請先完成第三章。")
        return

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("現場施作")
        gw_prog = st.session_state.game_state["guide_wall_progress"]
        st.progress(gw_prog / 100, text=f"進度: {gw_prog}%")
        if gw_prog < 100:
            if st.button("施工：挖溝&澆置"):
                st.session_state.game_state["guide_wall_progress"] += 50
                st.rerun()
    with col2:
        st.subheader("行政查驗")
        if gw_prog >= 100:
            if st.button("📞 申報導溝勘驗", type="primary"):
                config_type = st.session_state.game_state["config"]["type"]
                b5_ok = st.session_state.game_state["b5_closed"]
                if "拆併建" in config_type and not b5_ok:
                    st.error("🚫 退件！拆除廢棄物 (B5) 尚未結案。")
                else:
                    st.session_state.game_state["guide_wall_inspected"] = True
                    st.balloons()
                    st.success("🎉 勘驗合格！")
                    add_log("導溝勘驗通過。")
        else:
            st.info("請先完成施作。")

# --- Ch5: 放樣勘驗 ---
def render_chapter_5():
    st.header("🏯 終章：放樣勘驗")
    if not st.session_state.game_state["guide_wall_inspected"]:
        st.warning("🔒 鎖定中：請先完成第四章。")
        return
    st.success("🌟 准予掛號！")
    hp = st.session_state.game_state["boss_hp"]
    st.metric("BOSS HP", f"{hp}/100")
    if st.button("⚔️ 發動攻擊 (審查)"):
        st.session_state.game_state["boss_hp"] = max(0, hp - 20)
        st.rerun()
    if st.session_state.game_state["boss_hp"] == 0:
        st.balloons()
        st.success("🏆 恭喜通關！准予放樣！建築物正式長出來啦！")

# --- Ch6: 地下城 ---
def render_chapter_6():
    st.header("🚜 Ch6: 地下城危機 (基礎開挖)")
    if st.session_state.game_state["boss_hp"] > 0:
        st.warning("🔒 請先完成 Ch5 放樣勘驗。")
        return

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🛡️ 安全支撐")
        if st.session_state.game_state["shoring_installed"]:
            st.success("✅ 安全支撐已架設")
        else:
            st.warning("⚠️ 尚未架設支撐！")
            if st.button("架設 H 型鋼支撐"):
                st.session_state.game_state["shoring_installed"] = True
                add_log("安全支撐架設完成。")
                st.rerun()

    with col2:
        st.subheader("🏗️ 土方開挖")
        prog = st.session_state.game_state["excavation_progress"]
        st.progress(prog / 100, text=f"開挖進度: {prog}%")
        
        if prog < 100:
            if st.button("挖土 & 運棄 (B5)"):
                if not st.session_state.game_state["shoring_installed"]:
                    st.error("💥 危險！未架設支撐就開挖！")
                    st.session_state.game_state["risk_level"] += 20
                    add_log("違規開挖，風險激增！")
                else:
                    st.session_state.game_state["excavation_progress"] += 25
                    add_log("土方開挖進度 +25%")
                    st.rerun()
        else:
            st.success("開挖完成！")
            if st.button("前往結構體工程"):
                st.session_state.game_state["foundation_done"] = True
                st.rerun()

# --- Ch7: 巴別塔 ---
def render_chapter_7():
    st.header("🏢 Ch7: 巴別塔試煉 (結構體)")
    if not st.session_state.game_state.get("foundation_done"):
        st.warning("🔒 請先完成 Ch6 基礎開挖。")
        return

    floors = ["B1", "1F", "2F"]
    curr_floor = st.selectbox("選擇施工樓層", floors, index=floors.index(st.session_state.game_state["current_floor"]))
    st.session_state.game_state["current_floor"] = curr_floor
    
    status = st.session_state.game_state["floor_status"][curr_floor]
    
    st.subheader(f"目前樓層：{curr_floor}")
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown("#### 1. 綁紮")
        if status["rebar"]: st.success("已完成")
        else:
            if st.button("綁鋼筋"):
                status["rebar"] = True
                st.rerun()
                
    with c2:
        st.markdown("#### 2. 封模")
        if status["form"]: st.success("已完成")
        else:
            if not status["rebar"]: st.caption("先綁筋");
            else:
                if st.button("封板模"): status["form"] = True; st.rerun()

    with c3:
        st.markdown("#### 3. 勘驗")
        if status["report"]: st.success("已核准")
        else:
            if not status["form"]: st.caption("先封模");
            else:
                if curr_floor == "2F": st.info("🔥 此層需公會抽查！")
                
                prev_floor_map = {"1F": "B1", "2F": "1F"}
                can_report = True
                
                if curr_floor in prev_floor_map:
                    prev_f = prev_floor_map[curr_floor]
                    prev_test_week = st.session_state.game_state["floor_status"][prev_f]["test_week"]
                    current_week = st.session_state.game_state["current_week"]
                    
                    if prev_test_week is None:
                        st.error("上一層忘了做試體！")
                        can_report = False
                    elif (current_week - prev_test_week) < 4:
                        wait = 4 - (current_week - prev_test_week)
                        st.warning(f"⏳ 試體養護中...還需 {wait} 週")
                        can_report = False
                
                if can_report:
                    if st.button("申報勘驗"):
                        status["report"] = True
                        st.balloons()
                        add_log(f"{curr_floor} 勘驗通過。"); st.rerun()

    with c4:
        st.markdown("#### 4. 澆置")
        if status["pour"]: st.success("已完成")
        else:
            if not status["report"]: st.caption("先勘驗");
            else:
                if st.button("灌漿 & 做試體"):
                    status["pour"] = True
                    status["test_week"] = st.session_state.game_state["current_week"]
                    add_log(f"{curr_floor} 灌漿完成，試體製作"); st.rerun()

def add_log(msg):
    st.session_state.game_state["logs"].append(f"Week {st.session_state.game_state['current_week']}: {msg}")

if __name__ == "__main__":
    main()