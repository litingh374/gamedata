import streamlit as st
import time
import random
from gamedata import REGIONS, PROJECT_TYPES, THRESHOLDS, DEMO_SEALS, GREEN_QUEST, GEMS, SETTING_OUT_STEPS, NW_CODES, RANDOM_EVENTS, STRUCTURE_ITEMS

# ==========================================
# 0. 核心狀態管理
# ==========================================
if 'game_state' not in st.session_state:
    st.session_state.game_state = {
        "stage": "Launcher",
        "config": {},
        
        # --- 經營模擬 ---
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
        
        # --- 新增關卡狀態 (Ch6~Ch7) ---
        "excavation_progress": 0,     # 開挖進度
        "shoring_installed": False,   # 安全支撐
        "foundation_done": False,     # 基礎完成
        
        "current_floor": "B1",        # 當前樓層
        "floor_status": {             # 各樓層狀態
            "B1": {"rebar": False, "form": False, "pour": False, "report": False, "test_week": None},
            "1F": {"rebar": False, "form": False, "pour": False, "report": False, "test_week": None},
            "2F": {"rebar": False, "form": False, "pour": False, "report": False, "test_week": None},
        },
        
        "logs": [],
        
        # 無紙化檔案
        "paperless_raw_files": [
            "開工申報書.docx", "空污費收據.jpg", "拆除施工計畫.pdf",
            "鄰房鑑定報告.pdf", "逕流廢水核備函.jpg", "自拍照.jpg"
        ],
        "paperless_processed_files": [],
    }

def main():
    st.set_page_config(page_title="跑照大作戰：巴別塔試煉", layout="wide", page_icon="🏗️")
    
    if st.session_state.game_state["active_event"]:
        render_event_dialog()
        return

    if st.session_state.game_state["stage"] == "Launcher":
        render_launcher()
    else:
        render_main_game()

# ==========================================
# 隨機事件與 Launcher (保持不變，省略以節省篇幅)
# ==========================================
# (此處請保留上一版的 render_event_dialog, resolve_event, render_launcher, set_preset 函式)
# 為求完整性，請將上一版這部分的代碼貼過來，或直接使用上一版檔案，只修改 render_main_game 及新增 Ch6/7

def render_event_dialog():
    evt = st.session_state.game_state["active_event"]
    st.error(f"🚨 {evt['title']}")
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
    st.title("專案啟動")
    if st.button("🚀 快速開始 (素地)", type="primary"):
        st.session_state.game_state["config"] = {"region": "台北市", "type": "素地新建 (Empty Land)", "is_mrt": False}
        st.session_state.game_state["project_data"] = {"area":100, "duration":6, "cost":3000000, "floor_area":300, "area_unknown":False, "duration_unknown":False, "cost_unknown":False, "floor_area_unknown":False}
        st.session_state.game_state["demo_phase_passed"] = True
        st.session_state.game_state["b5_closed"] = True
        st.session_state.game_state["stage"] = "MainGame"
        st.rerun()

# ==========================================
# 主遊戲介面 (新增 Tabs)
# ==========================================
def render_main_game():
    cfg = st.session_state.game_state["config"]
    
    if st.session_state.game_state["doing_paperless"]:
        render_paperless_minigame()
        return

    with st.sidebar:
        st.title(f"Week {st.session_state.game_state['current_week']}")
        st.metric("風險值", f"{st.session_state.game_state['risk_level']}%")
        if st.button("📅 推進一週 (晨會)", type="primary"):
            advance_week()
        
        st.divider()
        st.caption("專案日誌")
        for log in st.session_state.game_state["logs"][-5:]:
            st.text(log)

    st.title(f"🏗️ {cfg['type']}")
    
    # 擴增 Tabs
    tabs = st.tabs(["Ch1 開工", "Ch2 計畫", "Ch3 拆除", "Ch4 導溝", "Ch5 放樣", "Ch6 地下城", "Ch7 巴別塔"])
    
    with tabs[0]: render_chapter_1()
    with tabs[1]: render_chapter_2()
    with tabs[2]: render_chapter_3()
    with tabs[3]: render_chapter_4()
    with tabs[4]: render_chapter_5()
    with tabs[5]: render_chapter_6() # 新增
    with tabs[6]: render_chapter_7() # 新增

# ==========================================
# Ch1~Ch5 (簡化保留，請使用上一版的完整代碼)
# ==========================================
# (為確保程式碼能執行，這裡提供極簡版，請務必將上一版的完整邏輯貼回)
def render_chapter_1():
    st.header("Ch1 開工申報")
    if st.button("完成開工 (跳過)"): st.session_state.game_state["commencement_done"] = True
def render_chapter_2():
    st.header("Ch2 施工計畫")
    if st.button("核定計畫 (跳過)"): st.session_state.game_state["plan_approved"] = True
def render_chapter_3():
    st.header("Ch3 拆除整備")
    if st.button("拆除完成 (跳過)"): st.session_state.game_state["demo_phase_passed"] = True
def render_chapter_4():
    st.header("Ch4 導溝勘驗")
    if st.button("導溝完成 (跳過)"): st.session_state.game_state["guide_wall_inspected"] = True
def render_chapter_5():
    st.header("Ch5 放樣勘驗")
    if st.button("放樣通過 (跳過)"): 
        st.session_state.game_state["boss_hp"] = 0
        st.balloons()

# ==========================================
# Ch6: 地下城危機 (B5與支撐)
# ==========================================
def render_chapter_6():
    st.header("🚜 Ch6: 地下城危機 (基礎開挖)")
    
    # 前置檢查
    if st.session_state.game_state["boss_hp"] > 0:
        st.warning("🔒 請先完成 Ch5 放樣勘驗。")
        return

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🛡️ 安全支撐 (The Shoring)")
        if st.session_state.game_state["shoring_installed"]:
            st.success("✅ 安全支撐已架設")
        else:
            st.warning("⚠️ 尚未架設支撐！")
            if st.button("架設 H 型鋼支撐"):
                st.session_state.game_state["shoring_installed"] = True
                add_log("安全支撐架設完成。")
                st.rerun()

    with col2:
        st.subheader("🏗️ 土方開挖 (Excavation)")
        prog = st.session_state.game_state["excavation_progress"]
        st.progress(prog / 100, text=f"開挖進度: {prog}%")
        
        if prog < 100:
            if st.button("挖土 & 運棄 (B5)"):
                # 風險檢查：沒架支撐就挖土
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
# Ch7: 巴別塔試煉 (結構體循環)
# ==========================================
def render_chapter_7():
    st.header("🏢 Ch7: 巴別塔試煉 (結構體)")
    
    if not st.session_state.game_state.get("foundation_done"):
        st.warning("🔒 請先完成 Ch6 基礎開挖。")
        return

    # 樓層選擇器
    floors = ["B1", "1F", "2F"]
    curr_floor = st.selectbox("選擇施工樓層", floors, index=floors.index(st.session_state.game_state["current_floor"]))
    st.session_state.game_state["current_floor"] = curr_floor
    
    status = st.session_state.game_state["floor_status"][curr_floor]
    
    # 顯示樓層狀態
    st.subheader(f"目前樓層：{curr_floor}")
    c1, c2, c3, c4 = st.columns(4)
    
    # 1. 綁紮 (Rebar)
    with c1:
        st.markdown("#### 1. 綁紮")
        if status["rebar"]:
            st.success("已完成")
        else:
            if st.button("綁鋼筋"):
                status["rebar"] = True
                st.rerun()
                
    # 2. 封模 (Formwork)
    with c2:
        st.markdown("#### 2. 封模")
        if status["form"]:
            st.success("已完成")
        else:
            if not status["rebar"]:
                st.caption("先綁筋")
            else:
                if st.button("封板模"):
                    status["form"] = True
                    st.rerun()

    # 3. 勘驗申報 (Report) - 核心文書
    with c3:
        st.markdown("#### 3. 勘驗")
        if status["report"]:
            st.success("已核准")
        else:
            if not status["form"]:
                st.caption("先封模")
            else:
                # 特殊：2F 公會抽查
                if curr_floor == "2F":
                    st.info("🔥 此層需公會抽查！")
                
                # 檢查時間差 (28天試體)
                # 假設上一層樓是 curr_floor 的前一個
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
                        add_log(f"{curr_floor} 勘驗通過。")
                        st.rerun()

    # 4. 澆置 (Pour) & 試體製作
    with c4:
        st.markdown("#### 4. 澆置")
        if status["pour"]:
            st.success("已完成")
        else:
            if not status["report"]:
                st.caption("先勘驗")
            else:
                if st.button("灌漿 & 做試體"):
                    status["pour"] = True
                    # 記錄試體製作時間 (關鍵)
                    status["test_week"] = st.session_state.game_state["current_week"]
                    add_log(f"{curr_floor} 灌漿完成，試體製作 (Week {status['test_week']})")
                    st.rerun()

def advance_week():
    st.session_state.game_state["current_week"] += 1
    # 隨機事件邏輯...
    if random.random() < 0.2:
        st.toast("發生隨機事件！", icon="🚨")
    st.rerun()

def render_paperless_minigame():
    st.title("無紙化上傳")
    if st.button("返回"): st.session_state.game_state["doing_paperless"] = False; st.rerun()

def add_log(msg):
    st.session_state.game_state["logs"].append(f"Week {st.session_state.game_state['current_week']}: {msg}")

if __name__ == "__main__":
    main()