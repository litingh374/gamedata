import streamlit as st
import time
import random
# 確保您的 gamedata.py 已經包含上一回新增的 RANDOM_EVENTS, STRUCTURE_ITEMS 等資料
from gamedata import REGIONS, PROJECT_TYPES, THRESHOLDS, DEMO_SEALS, GREEN_QUEST, GEMS, SETTING_OUT_STEPS, NW_CODES, RANDOM_EVENTS

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

        # --- 關卡狀態 (Ch1~Ch5) ---
        "hicos_connected": False,
        "demo_seals_cleared": [],
        "doing_paperless": False,
        "commencement_done": False,
        "collected_gems": [],
        "plan_approved": False,
        "is_demo_shield_active": False,
        "demo_progress": 0,
        "b5_closed": False,
        "demo_phase_passed": False,
        "guide_wall_progress": 0,
        "guide_wall_inspected": False,
        "boss_hp": 100,
        
        # --- 關卡狀態 (Ch6~Ch7) ---
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
        
        # --- 無紙化檔案 (關鍵修復：恢復原始檔列表) ---
        "paperless_raw_files": [
            "開工申報書_用印.docx", "空污費收據.jpg", "拆除施工計畫_核定.pdf",
            "鄰房鑑定報告.pdf", "逕流廢水核備函.jpg", "工地主任自拍照.jpg",
            "配筋圖_A3.dwg"
        ],
        "paperless_processed_files": [],
    }

def main():
    st.set_page_config(page_title="跑照大作戰：完全體", layout="wide", page_icon="🏗️")
    
    # 優先處理隨機事件彈窗
    if st.session_state.game_state["active_event"]:
        render_event_dialog()
        return

    if st.session_state.game_state["stage"] == "Launcher":
        render_launcher()
    else:
        render_main_game()

# ==========================================
# 隨機事件處理 (Dialog)
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

# ==========================================
# 遊戲大廳 (恢復完整參數輸入)
# ==========================================
def render_launcher():
    st.title("🏗️ 專案啟動：工程情報輸入")
    
    st.subheader("🏁 快速開始")
    c1, c2 = st.columns(2)
    if c1.button("🟢 新手村 (小型透天)", use_container_width=True): set_preset("small")
    if c2.button("🔴 挑戰模式 (大型建案)", use_container_width=True): set_preset("large")

    st.markdown("---")
    st.subheader("📝 自定義參數")
    with st.container(border=True):
        rc1, rc2 = st.columns(2)
        region = rc1.radio("伺服器", REGIONS)
        p_type = rc2.radio("劇本", PROJECT_TYPES)
        
        st.markdown("#### 📐 規模數值")
        cc1, cc2 = st.columns([3, 1])
        area_unk = cc2.checkbox("不清楚面積")
        area = cc1.number_input("基地面積", value=100, disabled=area_unk)
        
        cc3, cc4 = st.columns([3, 1])
        dur_unk = cc4.checkbox("不清楚工期")
        dur = cc3.number_input("預計工期", value=6, disabled=dur_unk)
        
        # 即時回饋
        if not area_unk and not dur_unk:
            if area * dur >= THRESHOLDS["POLLUTION_FACTOR"]:
                st.error("⚠️ 係數過高：將觸發逕流廢水副本！")
            else:
                st.success("✅ 免辦逕流廢水")

    if st.button("🚀 生成專案", type="primary", use_container_width=True):
        st.session_state.game_state["config"] = {"region": region, "type": p_type, "is_mrt": False}
        st.session_state.game_state["project_data"] = {
            "area": area, "area_unknown": area_unk,
            "duration": dur, "duration_unknown": dur_unk,
            "cost": 3000000, "cost_unknown": False,
            "floor_area": 300, "floor_area_unknown": False
        }
        if "素地" in p_type:
            st.session_state.game_state["demo_phase_passed"] = True
            st.session_state.game_state["b5_closed"] = True
            st.session_state.game_state["is_demo_shield_active"] = True
        
        st.session_state.game_state["stage"] = "MainGame"
        st.rerun()

def set_preset(mode):
    if mode == "small":
        cfg = {"region": "台北市", "type": "素地新建 (Empty Land)", "is_mrt": False}
        p_data = {"area": 100, "duration": 6, "cost": 3000000, "floor_area": 300, "area_unknown":False, "duration_unknown":False, "cost_unknown":False, "floor_area_unknown":False}
        st.session_state.game_state["demo_phase_passed"] = True
        st.session_state.game_state["b5_closed"] = True
        st.session_state.game_state["is_demo_shield_active"] = True
    else:
        cfg = {"region": "台北市", "type": "拆併建照 (Demolition & Build)", "is_mrt": True}
        p_data = {"area": 3000, "duration": 24, "cost": 200000000, "floor_area": 15000, "area_unknown":False, "duration_unknown":False, "cost_unknown":False, "floor_area_unknown":False}
    
    st.session_state.game_state["config"] = cfg
    st.session_state.game_state["project_data"] = p_data
    st.session_state.game_state["stage"] = "MainGame"
    st.rerun()

# ==========================================
# 主遊戲介面
# ==========================================
def render_main_game():
    # 無紙化小遊戲路由 (優先顯示)
    if st.session_state.game_state["doing_paperless"]:
        render_paperless_minigame()
        return

    cfg = st.session_state.game_state["config"]
    
    with st.sidebar:
        st.title(f"Week {st.session_state.game_state['current_week']}")
        st.metric("風險值", f"{st.session_state.game_state['risk_level']}%")
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
# Ch1: 開工申報 (完整版：含封印、迷霧、數位門禁)
# ==========================================
def render_chapter_1():
    st.header("📂 第一章：開工申報")
    p_data = st.session_state.game_state["project_data"]
    
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
                    with cols[int(sid[-1])%3]: # 簡單排列
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

        # B. 環保任務 (迷霧版)
        st.subheader("🌳 環保任務")
        with st.container(border=True):
            st.checkbox("G01 空污費", value=True, disabled=True)
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
                    g02 = st.checkbox(f"G02 逕流廢水 (係數{f})")
                else:
                    st.write("~~G02 逕流廢水~~ (免辦)")
                    g02 = True
            green_ok = g02

    with col_system:
        st.subheader("💻 數位憑證")
        if not st.session_state.game_state["hicos_connected"]:
            st.error("⛔ 未偵測到憑證")
            if st.button("插入：工商憑證卡"):
                time.sleep(0.5)
                st.session_state.game_state["hicos_connected"] = True
                st.rerun()
        else:
            st.success("🟢 HiCOS 已連線")
            if seals_ok and green_ok:
                st.info("條件符合，請進入系統。")
                if st.button("進入虛擬桌面 (上傳)", type="primary"):
                    st.session_state.game_state["doing_paperless"] = True
                    st.rerun()
            else:
                st.warning("🔒 任務未解鎖")
                
            if st.session_state.game_state["commencement_done"]:
                st.success("🎉 開工申報完成！")

# ==========================================
# 無紙化小遊戲 (關鍵修復：功能回歸！)
# ==========================================
def render_paperless_minigame():
    st.title("💻 台北市無紙化上傳系統")
    st.info("任務：請將左側的原始檔案，配對正確的 NW 編碼進行轉檔，最後勾選送出。")
    
    if st.button("🔙 放棄並返回"):
        st.session_state.game_state["doing_paperless"] = False
        st.rerun()

    c_ws, c_list = st.columns([2, 1])
    with c_ws:
        st.subheader("🛠️ 轉檔工作區")
        with st.container(border=True):
            col_a, col_b, col_c = st.columns([2, 2, 1])
            
            raws = st.session_state.game_state["paperless_raw_files"]
            # 只有當還有原始檔時才顯示
            sel_raw = col_a.selectbox("選擇原始檔", raws) if raws else None
            sel_code = col_b.selectbox("NW 編碼", ["請選擇..."] + list(NW_CODES.keys()))
            
            if col_c.button("轉檔 ➡️", type="primary", disabled=not sel_raw):
                st.session_state.game_state["paperless_raw_files"].remove(sel_raw)
                # 模擬轉檔命名
                clean_name = sel_raw.split('.')[0].replace("_用印","").replace("_核定","")
                new_name = f"{sel_code}_{clean_name}.pdf"
                st.session_state.game_state["paperless_processed_files"].append(new_name)
                st.toast(f"已轉檔：{new_name}")
                st.rerun()
        
        st.write("#### 準備上傳的文件")
        processed = st.session_state.game_state["paperless_processed_files"]
        
        if not processed:
            st.caption("尚無已轉檔文件...")
        else:
            to_upload = st.multiselect("勾選上傳", processed, default=processed)
            
            if st.button("🚀 確認送出 (啟動計時)", type="primary", use_container_width=True):
                # 簡易檢查：必須要有開工申報書 (NW0100)
                if any("NW0100" in f for f in to_upload):
                    st.session_state.game_state["commencement_done"] = True
                    st.session_state.game_state["doing_paperless"] = False
                    st.balloons()
                    add_log("線上掛號成功！進入紙本倒數。")
                    st.rerun()
                else:
                    st.error("退件：缺少 NW0100 開工申報書！")

    with c_list:
        st.markdown("📜 **編碼對照表**")
        data = [{"代碼": k, "名稱": v["name"]} for k, v in NW_CODES.items()]
        st.dataframe(data, hide_index=True, use_container_width=True)

# ==========================================
# Ch2: 施工計畫 (完整版：含寶石收集)
# ==========================================
def render_chapter_2():
    st.header("📜 第二章：施工計畫")
    if not st.session_state.game_state["commencement_done"]:
        st.warning("🔒 鎖定中：請先完成第一章。")
        return
    
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
    if len(collected) == 6:
        if st.button("✨ 核定計畫", type="primary"):
            st.session_state.game_state["plan_approved"] = True
            st.balloons()
            st.rerun()
    else:
        st.info(f"收集進度：{len(collected)}/6")

    if st.session_state.game_state["plan_approved"]:
        st.success("✅ 施工計畫已核定")

# ==========================================
# Ch3: 拆除整備 (完整版：含B5陷阱與風險)
# ==========================================
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
            if risk > 0 and random.random() < 0.5:
                st.error("💥 發生鄰損！因為您之前簽切結書跳過鑑定...")
                st.session_state.game_state["risk_level"] += 20
                add_log("鄰損發生！工程暫停。")
            else:
                st.session_state.game_state["demo_progress"] = 100
                st.success("拆除完成！(運氣不錯)")
                add_log("拆除作業完成。")

    if st.session_state.game_state["demo_progress"] >= 100:
        st.session_state.game_state["demo_phase_passed"] = True
        st.success("🌟 拆除階段完成！")

# ==========================================
# Ch4: 導溝勘驗 (完整版：含雙重檢查)
# ==========================================
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

# ==========================================
# Ch5: 放樣 BOSS (完整版)
# ==========================================
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

# ==========================================
# Ch6: 地下城 (完整版)
# ==========================================
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

# ==========================================
# Ch7: 巴別塔 (完整版)
# ==========================================
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