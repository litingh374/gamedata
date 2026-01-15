import streamlit as st
import time
import random
from gamedata import REGIONS, PROJECT_TYPES, THRESHOLDS, DEMO_SEALS, GREEN_QUEST, GEMS, SETTING_OUT_STEPS, NW_CODES, RANDOM_EVENTS

# ==========================================
# 0. 核心狀態管理
# ==========================================
if 'game_state' not in st.session_state:
    st.session_state.game_state = {
        "stage": "Launcher",
        "config": {},
        
        # --- 經營模擬數據 ---
        "current_week": 1,            # 當前週數
        "total_weeks": 52,            # 總工期 (預設)
        "budget_used": 0,             # 已用預算
        "risk_level": 0,              # 風險值
        "active_event": None,         # 當前觸發的事件
        
        # --- 專案數值 ---
        "project_data": {
            "area": 0, "area_unknown": False,
            "duration": 0, "duration_unknown": False,
            "cost": 0, "cost_unknown": False,
            "floor_area": 0, "floor_area_unknown": False,
        },

        # --- 關卡狀態 ---
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
        "logs": [],
        
        # 無紙化檔案
        "paperless_raw_files": [
            "開工申報書.docx", "空污費收據.jpg", "拆除施工計畫.pdf",
            "鄰房鑑定報告.pdf", "逕流廢水核備函.jpg", "自拍照.jpg"
        ],
        "paperless_processed_files": [],
    }

def main():
    st.set_page_config(page_title="跑照大作戰：生存模擬版", layout="wide", page_icon="🏗️")
    
    # 處理隨機事件彈窗 (必須在最上層)
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
    st.image("https://placeholder.co/600x200?text=EMERGENCY", use_container_width=True)
    st.markdown(f"**{evt['desc']}**")
    
    st.markdown("### ⚠️ 請選擇處置方案：")
    
    col1, col2 = st.columns(2)
    with col1:
        opt1 = evt['options'][0]
        if st.button(f"🅰️ {opt1['text']}", use_container_width=True):
            resolve_event(opt1)
            
    with col2:
        opt2 = evt['options'][1]
        if st.button(f"🅱️ {opt2['text']}", use_container_width=True):
            resolve_event(opt2)

def resolve_event(option):
    """處理事件結果"""
    msg = option['msg']
    effect = option['effect']
    val = option['val']
    
    if effect == "delay":
        st.session_state.game_state["current_week"] += val
        st.toast(f"工期延誤 {val} 週！", icon="🐢")
    elif effect == "risk":
        st.session_state.game_state["risk_level"] += val
        st.toast(f"風險值增加 {val}%！", icon="🔥")
    elif effect == "cost":
        st.session_state.game_state["budget_used"] += val
        st.toast(f"花費 {val} 元！", icon="💸")
    elif effect == "disaster":
        st.session_state.game_state["risk_level"] = 100
        st.session_state.game_state["budget_used"] += 200000
        st.error("災難發生！賠償鉅款！")
    
    add_log(f"事件處置：{option['text']} -> {msg}")
    st.session_state.game_state["active_event"] = None
    st.rerun()

# ==========================================
# 遊戲大廳
# ==========================================
def render_launcher():
    st.title("🏗️ 專案啟動：工程情報輸入")
    
    st.subheader("🏁 快速開始 (選擇樣板)")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        if st.button("🟢 新手村 (小型透天)", use_container_width=True):
            set_preset("small")
    with col_p2:
        if st.button("🔴 挑戰模式 (大型建案)", use_container_width=True):
            set_preset("large")

    st.markdown("---")
    st.subheader("📝 自定義專案參數")
    
    with st.container(border=True):
        c1, c2 = st.columns(2)
        region = c1.radio("伺服器", REGIONS)
        p_type = c2.radio("劇本", PROJECT_TYPES)
        
        st.markdown("#### 📐 規模數值")
        cc1, cc2 = st.columns([3, 1])
        area_unk = cc2.checkbox("不清楚面積")
        area = cc1.number_input("基地面積 (m²)", value=100, disabled=area_unk)
        
        cc3, cc4 = st.columns([3, 1])
        dur_unk = cc4.checkbox("不清楚工期")
        dur = cc3.number_input("預計工期 (月)", value=6, disabled=dur_unk)
        
        # Live Feedback
        if not area_unk and not dur_unk:
            factor = area * dur
            if factor >= THRESHOLDS["POLLUTION_FACTOR"]:
                st.error(f"⚠️ 係數 {factor}：觸發逕流廢水！")
            else:
                st.success(f"✅ 係數 {factor}：免辦逕流廢水。")

    if st.button("🚀 確認並生成專案", type="primary", use_container_width=True):
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
        cfg = {"region": "台北市 (Taipei)", "type": "素地新建 (Empty Land)", "is_mrt": False}
        p_data = {"area": 100, "duration": 6, "cost": 3000000, "floor_area": 300, 
                  "area_unknown":False, "duration_unknown":False, "cost_unknown":False, "floor_area_unknown":False}
        st.session_state.game_state["demo_phase_passed"] = True
        st.session_state.game_state["b5_closed"] = True
        st.session_state.game_state["is_demo_shield_active"] = True
    else:
        cfg = {"region": "台北市 (Taipei)", "type": "拆併建照 (Demolition & Build)", "is_mrt": True}
        p_data = {"area": 3000, "duration": 24, "cost": 200000000, "floor_area": 15000,
                  "area_unknown":False, "duration_unknown":False, "cost_unknown":False, "floor_area_unknown":False}
    
    st.session_state.game_state["config"] = cfg
    st.session_state.game_state["project_data"] = p_data
    st.session_state.game_state["stage"] = "MainGame"
    st.rerun()

# ==========================================
# 主遊戲介面 (含 Sidebar 晨會系統)
# ==========================================
def render_main_game():
    cfg = st.session_state.game_state["config"]
    
    if st.session_state.game_state["doing_paperless"]:
        render_paperless_minigame()
        return

    # --- 側邊欄經營儀表板 ---
    with st.sidebar:
        st.title("📊 專案儀表板")
        
        # 1. 工期狀態
        curr = st.session_state.game_state["current_week"]
        total = st.session_state.game_state["total_weeks"]
        st.metric("當前週數", f"Week {curr}", f"剩餘 {total - curr} 週")
        st.progress(min(curr/total, 1.0))
        
        # 2. 風險與預算
        risk = st.session_state.game_state["risk_level"]
        st.metric("風險指數", f"{risk}%", delta_color="inverse")
        if risk > 50: st.warning("🔥 風險過高！容易發生災害！")
        
        budget = st.session_state.game_state["budget_used"]
        st.metric("額外支出", f"${budget:,}")
        
        st.markdown("---")
        
        # 3. 每週晨會 (核心機制)
        if st.button("📅 召開週會 (推進一週)", type="primary", use_container_width=True):
            advance_week()
            
        st.markdown("---")
        st.write("📜 **專案日誌**")
        for log in st.session_state.game_state["logs"][-5:]:
            st.caption(log)
        
        if st.button("🔄 重置遊戲"):
            st.session_state.clear()
            st.rerun()

    st.title(f"🏗️ 專案執行中：{cfg['type']}")
    
    tabs = st.tabs(["Ch1 開工申報", "Ch2 施工計畫", "Ch3 拆除整備", "Ch4 導溝勘驗", "Ch5 放樣 BOSS"])
    with tabs[0]: render_chapter_1()
    with tabs[1]: render_chapter_2()
    with tabs[2]: render_chapter_3()
    with tabs[3]: render_chapter_4()
    with tabs[4]: render_chapter_5()

def advance_week():
    """推進時間並觸發隨機事件"""
    st.session_state.game_state["current_week"] += 1
    
    # 隨機觸發事件 (20% 機率)
    if random.random() < 0.2:
        event = random.choice(RANDOM_EVENTS)
        st.session_state.game_state["active_event"] = event
        st.rerun()
    else:
        # 平安無事
        msgs = [
            "本週進度順利，工地主任心情不錯。", 
            "沒有特殊狀況，大家準時下班。", 
            "天氣晴朗，施工進度超前。",
            "跑照人員去買了下午茶。"
        ]
        add_log(f"Week {st.session_state.game_state['current_week']}: {random.choice(msgs)}")
        st.toast("本週平安無事！", icon="🕊️")

# ==========================================
# 以下為各章節渲染 (簡化版，邏輯同前，但加入參數依賴)
# ==========================================
def render_chapter_1():
    st.header("📂 第一章：開工申報")
    p_data = st.session_state.game_state["project_data"]
    
    col_quest, col_system = st.columns([3, 2])
    with col_quest:
        config_type = st.session_state.game_state["config"]["type"]
        if "拆併建" in config_type:
            st.subheader("🔥 拆除七大封印")
            with st.container(border=True):
                cols = st.columns(3)
                completed = st.session_state.game_state["demo_seals_cleared"]
                for i, (sid, data) in enumerate(DEMO_SEALS.items()):
                    is_done = sid in completed
                    icon = "✅" if is_done else "🔒"
                    with cols[i%3]:
                        st.markdown(f"**{icon} {data['name']}**")
                        if not is_done:
                            if sid == "D01":
                                if st.button("鑑定", key=sid):
                                    st.session_state.game_state["demo_seals_cleared"].append(sid)
                                    st.session_state.game_state["is_demo_shield_active"] = True
                                    st.rerun()
                                if st.button("簽切結", key=f"{sid}_r"):
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
            st.checkbox("G01 空污費", value=True, disabled=True)
            
            # 迷霧機制
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
            if st.button("插卡"):
                time.sleep(0.5)
                st.session_state.game_state["hicos_connected"] = True
                st.rerun()
        else:
            st.success("HiCOS 連線")
            if seals_ok and green_ok:
                if st.button("上傳文件"):
                    st.session_state.game_state["doing_paperless"] = True
                    st.rerun()
            if st.session_state.game_state["commencement_done"]:
                st.success("開工申報完成")

def render_paperless_minigame():
    st.title("💻 無紙化上傳")
    if st.button("🔙 返回"):
        st.session_state.game_state["doing_paperless"] = False
        st.rerun()
    if st.button("🚀 送出 (模擬)"):
        st.session_state.game_state["commencement_done"] = True
        st.session_state.game_state["doing_paperless"] = False
        st.balloons()
        st.rerun()

def render_chapter_2():
    st.header("📜 第二章：施工計畫")
    if not st.session_state.game_state["commencement_done"]:
        st.warning("🔒 先完成 Ch1")
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
    
    if len(collected) == 6:
        if st.button("✨ 核定計畫"):
            st.session_state.game_state["plan_approved"] = True
            st.rerun()

def render_chapter_3():
    st.header("🚜 第三章：拆除")
    if not st.session_state.game_state["plan_approved"]:
        st.warning("🔒 先完成 Ch2")
        return
    if st.session_state.game_state["demo_phase_passed"]:
        st.success("本章節通過")
        return
    
    if st.button("B5 結案"):
        st.session_state.game_state["b5_closed"] = True
        st.success("B5 OK")
    
    if st.button("執行拆除"):
        if st.session_state.game_state["risk_level"] > 0 and random.random() < 0.5:
            st.error("💥 鄰損發生！")
            add_log("鄰損事故！")
        else:
            st.session_state.game_state["demo_progress"] = 100
            st.session_state.game_state["demo_phase_passed"] = True
            st.success("拆除完成")
            st.rerun()

def render_chapter_4():
    st.header("🧱 第四章：導溝")
    if not st.session_state.game_state["demo_phase_passed"]:
        st.warning("🔒 先完成 Ch3")
        return
    if st.button("施工"):
        st.session_state.game_state["guide_wall_progress"] = 100
        st.success("施工完成")
    if st.session_state.game_state["guide_wall_progress"] >= 100:
        if st.button("申報勘驗"):
            # B5 檢查
            if "拆併建" in st.session_state.game_state["config"]["type"] and not st.session_state.game_state["b5_closed"]:
                st.error("🚫 退件：B5 未結案")
            else:
                st.session_state.game_state["guide_wall_inspected"] = True
                st.balloons()

def render_chapter_5():
    st.header("🏯 終章：放樣")
    if not st.session_state.game_state["guide_wall_inspected"]:
        st.warning("🔒 先完成 Ch4")
        return
    if st.button("⚔️ 通關"):
        st.balloons()
        st.success("🏆 恭喜通關！")

def add_log(msg):
    st.session_state.game_state["logs"].append(f"Week {st.session_state.game_state['current_week']}: {msg}")

if __name__ == "__main__":
    main()