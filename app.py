import streamlit as st
import time
import random
from gamedata import REGIONS, PROJECT_TYPES, THRESHOLDS, DEMO_SEALS, GREEN_QUEST, GEMS, SETTING_OUT_STEPS, NW_CODES, RANDOM_EVENTS, CONSTRUCTION_METHODS, TEAM_MEMBERS, RESOURCE_RATES, ENV_OPTIONS, DIPLOMACY_STRATEGIES

# ==========================================
# 0. 核心狀態管理 (初始化)
# ==========================================
if 'game_state' not in st.session_state:
    st.session_state.game_state = {
        "stage": "Launcher",
        "config": {},
        
        # --- 經營模擬數據 ---
        "current_week": 1,
        "total_weeks": 52,
        "budget_used": 0,
        "risk_level": 0,
        "active_event": None,
        
        # --- 專案數值 ---
        "project_data": {
            "area": 0, "area_unknown": False,
            "duration": 0, "duration_unknown": False,
            "cost": 0, "cost_unknown": False,
            "floor_area": 0, "floor_area_unknown": False,
        },

        # --- Ch1: 開工申報 (修正重點：新增任務狀態字典) ---
        "hicos_connected": False,
        "demo_seals_cleared": [],
        "doing_paperless": False,
        "commencement_done": False,
        "ch1_strategy_done": False,
        "ch1_tasks": {"G02": False, "G03": False}, # [修正] 強制記錄任務狀態
        "resource_accurate": False,
        
        # --- Ch2: 施工計畫 ---
        "collected_gems": [],
        "plan_approved": False,
        "strategy": {"method": None, "team": {}, "layout": {}}, 
        
        # --- Ch3~5 ---
        "is_demo_shield_active": False,
        "demo_progress": 0,
        "b5_closed": False,
        "demo_phase_passed": False,
        "guide_wall_progress": 0,
        "guide_wall_inspected": False,
        "boss_hp": 100,
        
        # --- Ch6~7 ---
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
        
        # 無紙化檔案
        "paperless_raw_files": [
            "開工申報書_用印.docx", "空污費收據.jpg", "拆除施工計畫_核定.pdf",
            "鄰房鑑定報告.pdf", "逕流廢水核備函.jpg", "工地主任證書_含勞保.pdf",
            "配筋圖_A3.dwg", "工地主任自拍照.jpg"
        ],
        "paperless_processed_files": [],
    }

def main():
    st.set_page_config(page_title="跑照大作戰：完全體", layout="wide", page_icon="🏗️")
    
    if st.session_state.game_state["active_event"]:
        render_event_dialog()
        return

    if st.session_state.game_state["stage"] == "Launcher":
        render_launcher()
    else:
        render_main_game()

# ==========================================
# 隨機事件與 Launcher (保持不變)
# ==========================================
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

# ==========================================
# 主遊戲介面
# ==========================================
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
    
    tabs = st.tabs(["Ch1 開工", "Ch2 計畫", "Ch3 拆除", "Ch4 導溝", "Ch5 放樣", "Ch6 地下城", "Ch7 巴別塔"])
    
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
# Ch1: 開工申報 (修正：狀態保存邏輯)
# ==========================================
def render_chapter_1():
    st.header("📂 第一章：開工申報 (戰略部署)")
    p_data = st.session_state.game_state["project_data"]
    
    # 1. 資源與外交 (戰略)
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
            
            # 簡單判定準確度
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

    # 2. 行政程序
    col_quest, col_system = st.columns([3, 2])
    
    with col_quest:
        config_type = st.session_state.game_state["config"]["type"]
        
        # A. 拆除封印
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

        # B. 環保任務 (修正重點：使用 persistent state)
        st.subheader("🌳 環保任務")
        with st.container(border=True):
            st.checkbox("G01 空污費", value=True, disabled=True)
            
            # --- 修正邏輯開始 ---
            # 讀取目前 G02 狀態
            current_g02_status = st.session_state.game_state["ch1_tasks"].get("G02", False)
            
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
                    # 使用 value=current_status 來保持狀態
                    is_checked = st.checkbox(f"G02 逕流廢水 (係數{f})", value=current_g02_status, key="chk_g02")
                    if is_checked:
                        st.session_state.game_state["ch1_tasks"]["G02"] = True
                    else:
                        st.session_state.game_state["ch1_tasks"]["G02"] = False
                else:
                    st.write("~~G02 逕流廢水~~ (免辦)")
                    st.session_state.game_state["ch1_tasks"]["G02"] = True # 免辦視同完成
            
            # 更新 green_ok 變數
            green_ok = st.session_state.game_state["ch1_tasks"]["G02"]
            # --- 修正邏輯結束 ---

    with col_system:
        st.subheader("💻 數位憑證")
        if not st.session_state.game_state["hicos_connected"]:
            if st.button("插入：工商憑證卡"):
                time.sleep(0.5)
                st.session_state.game_state["hicos_connected"] = True
                st.rerun()
        else:
            st.success("🟢 HiCOS 連線")
            
            if seals_ok and green_ok:
                st.info("條件符合，請進入系統。")
                if st.button("進入虛擬桌面 (上傳)", type="primary"):
                    st.session_state.game_state["doing_paperless"] = True
                    st.rerun()
            else:
                st.warning("🔒 任務未解鎖 (請完成左側任務)")
                
            if st.session_state.game_state["commencement_done"]:
                # 戰略結算
                if not st.session_state.game_state.get("ch1_strategy_done"):
                    st.session_state.game_state["ch1_strategy_done"] = True
                    st.session_state.game_state["budget_used"] += ENV_OPTIONS[env_choice]["cost"]
                    st.session_state.game_state["budget_used"] += DIPLOMACY_STRATEGIES[dip_choice]["cost"]
                    st.session_state.game_state["risk_level"] += DIPLOMACY_STRATEGIES[dip_choice]["anger"]
                    if st.session_state.game_state.get("resource_accurate"):
                        st.toast("🎯 資源預估神準！獎勵預算！")
                        st.session_state.game_state["budget_used"] -= 50000
                st.success("🎉 開工申報完成！請前往第二章。")

# ==========================================
# 無紙化小遊戲
# ==========================================
def render_paperless_minigame():
    st.title("💻 台北市無紙化上傳系統")
    if st.button("🔙 放棄"): st.session_state.game_state["doing_paperless"] = False; st.rerun()

    c_ws, c_list = st.columns([2, 1])
    with c_ws:
        st.subheader("🛠️ 轉檔工作區")
        with st.container(border=True):
            col_a, col_b, col_c = st.columns([2, 2, 1])
            raws = st.session_state.game_state["paperless_raw_files"]
            sel_raw = col_a.selectbox("原始檔", raws) if raws else None
            sel_code = col_b.selectbox("NW 編碼", ["請選擇..."] + list(NW_CODES.keys()))
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
                st.error("退件：缺少 NW0100！")

    with c_list:
        st.markdown("📜 **編碼對照表**")
        data = [{"代碼": k, "名稱": v["name"]} for k, v in NW_CODES.items()]
        st.dataframe(data, hide_index=True)

# ==========================================
# Chapter 2~7 (保持之前的功能)
# ==========================================
# ... (請將上一版 Ch2~Ch7 的程式碼貼於此處) ...
# 為了節省您的複製時間，我這裡直接把後面的程式碼也補上：

def render_chapter_2():
    st.header("📜 第二章：施工計畫 (戰略部署)")
    if not st.session_state.game_state["commencement_done"]:
        st.warning("🔒 鎖定中：請先完成第一章。")
        return
    
    st.subheader("1. 決定施工戰略")
    curr_method = st.session_state.game_state["strategy"].get("method", "BOTTOM_UP")
    m_opts = list(CONSTRUCTION_METHODS.keys())
    m_lbls = [f"{k}: {v['name']}" for k, v in CONSTRUCTION_METHODS.items()]
    sel_lbl = st.radio("選擇工法", m_lbls, index=m_opts.index(curr_method))
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
            st.success("✅ 計畫核定！")
            st.rerun()

    if st.session_state.game_state["plan_approved"]: st.success("✅ 施工計畫已核定")

def render_chapter_3():
    st.header("🚜 第三章：拆除整備")
    if not st.session_state.game_state["plan_approved"]: st.warning("🔒 鎖定中：請先完成第二章。"); return
    config_type = st.session_state.game_state["config"]["type"]
    if "素地" in config_type: st.success("✅ 素地自動通過"); st.session_state.game_state["demo_phase_passed"] = True; return

    has_shield = st.session_state.game_state["is_demo_shield_active"]
    risk = st.session_state.game_state["risk_level"]
    c1, c2 = st.columns(2)
    with c1:
        st.write(f"🛡️ 護盾：{'✅ 開啟' if has_shield else '❌ 無'}")
        if st.button("B5 廢棄物結案"): st.session_state.game_state["b5_closed"] = True; st.success("B5 已結案")
    with c2:
        if st.button("執行拆除作業"):
            strat = st.session_state.game_state.get("strategy", {})
            no_saf = strat.get("team", {}).get("saf", {}).get("id") == "SAF_NONE"
            actual_risk = risk + (50 if no_saf else 0)
            if actual_risk > 0 and random.random() < (actual_risk / 100):
                st.error("💥 發生意外！"); st.session_state.game_state["risk_level"] += 20; add_log("鄰損發生！")
            else:
                st.session_state.game_state["demo_progress"] = 100; st.success("拆除完成！"); add_log("拆除完成")

    if st.session_state.game_state["demo_progress"] >= 100: st.session_state.game_state["demo_phase_passed"] = True; st.success("🌟 拆除完成！")

def render_chapter_4():
    st.header("🧱 第四章：導溝勘驗")
    if not st.session_state.game_state["plan_approved"]: st.warning("🔒 鎖定中"); return
    if not st.session_state.game_state["demo_phase_passed"]: st.warning("🔒 鎖定中"); return
    c1, c2 = st.columns(2)
    with c1:
        if st.button("施工：挖溝&澆置"): st.session_state.game_state["guide_wall_progress"] += 50; st.rerun()
        st.progress(st.session_state.game_state["guide_wall_progress"]/100)
    with c2:
        if st.session_state.game_state["guide_wall_progress"] >= 100:
            if st.button("申報勘驗"):
                config = st.session_state.game_state["config"]["type"]
                b5 = st.session_state.game_state["b5_closed"]
                if "拆併建" in config and not b5: st.error("🚫 退件：B5 未結案")
                else: st.session_state.game_state["guide_wall_inspected"] = True; st.balloons(); st.success("🎉 勘驗合格")

def render_chapter_5():
    st.header("🏯 終章：放樣勘驗")
    if not st.session_state.game_state["guide_wall_inspected"]: st.warning("🔒 鎖定中"); return
    st.success("🌟 准予掛號！")
    if st.button("⚔️ 發動攻擊"): st.session_state.game_state["boss_hp"] = 0; st.rerun()
    if st.session_state.game_state["boss_hp"] == 0: st.balloons(); st.success("🏆 恭喜通關！")

def render_chapter_6():
    st.header("🚜 Ch6: 地下城危機")
    if st.session_state.game_state["boss_hp"] > 0: st.warning("🔒 鎖定中"); return
    c1, c2 = st.columns(2)
    with c1:
        if st.button("架設支撐"): st.session_state.game_state["shoring_installed"] = True; st.success("安全支撐已架設")
    with c2:
        if st.button("挖土 (B5)"):
            if not st.session_state.game_state["shoring_installed"]: st.error("💥 危險！未架設支撐！"); st.session_state.game_state["risk_level"] += 20
            else: st.session_state.game_state["excavation_progress"] += 25; st.rerun()
        if st.session_state.game_state["excavation_progress"] >= 100:
            st.success("開挖完成"); 
            if st.button("前往結構體"): st.session_state.game_state["foundation_done"] = True; st.rerun()

def render_chapter_7():
    st.header("🏢 Ch7: 巴別塔試煉")
    if not st.session_state.game_state.get("foundation_done"): st.warning("🔒 鎖定中"); return
    floors = ["B1", "1F", "2F"]
    curr = st.selectbox("樓層", floors, index=floors.index(st.session_state.game_state["current_floor"]))
    st.session_state.game_state["current_floor"] = curr
    status = st.session_state.game_state["floor_status"][curr]
    c1, c2, c3, c4 = st.columns(4)
    with c1: 
        if st.button("綁鋼筋"): status["rebar"] = True; st.rerun()
        if status["rebar"]: st.success("OK")
    with c2: 
        if st.button("封板模"): status["form"] = True; st.rerun()
        if status["form"]: st.success("OK")
    with c3:
        if st.button("申報勘驗"):
            # 時間差檢查
            prev_map = {"1F": "B1", "2F": "1F"}
            can_rep = True
            if curr in prev_map:
                prev_test = st.session_state.game_state["floor_status"][prev_map[curr]]["test_week"]
                now = st.session_state.game_state["current_week"]
                if prev_test is None or (now - prev_test) < 4: st.warning("⏳ 試體養護中..."); can_rep = False
            if can_rep: status["report"] = True; st.balloons(); st.rerun()
        if status["report"]: st.success("OK")
    with c4:
        if st.button("灌漿"): status["pour"] = True; status["test_week"] = st.session_state.game_state["current_week"]; st.rerun()
        if status["pour"]: st.success("OK")

def add_log(msg):
    st.session_state.game_state["logs"].append(f"Week {st.session_state.game_state['current_week']}: {msg}")

if __name__ == "__main__":
    main()