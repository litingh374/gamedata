import streamlit as st
import time
import random
from gamedata import REGIONS, PROJECT_TYPES, DEMO_SEALS, GREEN_QUEST, GEMS, SETTING_OUT_STEPS, NW_CODES

# ==========================================
# 0. 核心狀態管理
# ==========================================
if 'game_state' not in st.session_state:
    st.session_state.game_state = {
        "stage": "Launcher",
        "config": {},
        
        # --- Ch1: 開工申報 (大幅更新) ---
        "hicos_connected": False,     # 工商憑證是否插入
        "project_area": 500,          # 基地面積
        "project_duration": 10,       # 工期
        "green_quest_cleared": False, # 環保任務
        "demo_seals_cleared": [],     # 已解除的拆除封印
        "risk_level": 0,              # 風險值 (簽切結書會增加)
        "doing_paperless": False,
        "commencement_done": False,
        
        # 無紙化檔案
        "paperless_raw_files": [
            "開工申報書.docx", "空污費收據.jpg", "拆除施工計畫.pdf",
            "鄰房鑑定報告.pdf", "逕流廢水核備函.jpg", "自拍照.jpg"
        ],
        "paperless_processed_files": [],

        # --- Ch2~5 狀態 (保留) ---
        "collected_gems": [],
        "plan_approved": False,
        "is_demo_shield_active": False, # Ch3 使用
        "demo_progress": 0,
        "b5_closed": False,
        "demo_phase_passed": False,
        "guide_wall_progress": 0,
        "guide_wall_inspected": False,
        "boss_hp": 100,
        "logs": []
    }

def main():
    st.set_page_config(page_title="跑照大作戰：台北市特仕版", layout="wide", page_icon="🏗️")
    
    if st.session_state.game_state["stage"] == "Launcher":
        render_launcher()
    else:
        render_main_game()

# ==========================================
# 遊戲大廳
# ==========================================
def render_launcher():
    st.title("🏗️ 跑照大作戰：建立新專案")
    st.markdown("### 選擇伺服器與劇本")
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            region = st.radio("伺服器 (Server)", REGIONS)
            if "台北" in region:
                st.info("ℹ️ 難度 S：開啟「數位憑證」與「環保高標」機制。")
            is_mrt = st.checkbox("捷運沿線管制")
        with col2:
            p_type = st.radio("劇本 (Scenario)", PROJECT_TYPES)
            if "拆併建" in p_type:
                st.error("⚠️ 警告：開啟副本【拆除七大封印】。")
            else:
                st.success("✅ 提示：素地模式，流程較簡化。")
        
        if st.button("🚀 生成專案", type="primary", use_container_width=True):
            st.session_state.game_state["config"] = {"region": region, "type": p_type, "is_mrt": is_mrt}
            
            # 素地預設拆除相關Pass
            if "素地" in p_type:
                st.session_state.game_state["demo_phase_passed"] = True
                st.session_state.game_state["b5_closed"] = True
                st.session_state.game_state["is_demo_shield_active"] = True # 假設素地不需要護盾或預設安全
            
            st.session_state.game_state["stage"] = "MainGame"
            st.rerun()

# ==========================================
# 主遊戲介面
# ==========================================
def render_main_game():
    cfg = st.session_state.game_state["config"]
    
    if st.session_state.game_state["doing_paperless"]:
        render_paperless_minigame()
        return

    st.title(f"🏗️ 專案執行中：{cfg['type']}")
    
    # 顯示風險值
    risk = st.session_state.game_state["risk_level"]
    if risk > 0:
        st.warning(f"⚠️ 當前專案風險值：{risk}% (可能觸發鄰損事件)")

    tabs = st.tabs(["Ch1 開工申報", "Ch2 施工計畫", "Ch3 拆除整備", "Ch4 導溝勘驗", "Ch5 放樣 BOSS"])
    
    with tabs[0]: render_chapter_1()
    with tabs[1]: render_chapter_2()
    with tabs[2]: render_chapter_3()
    with tabs[3]: render_chapter_4()
    with tabs[4]: render_chapter_5()

    with st.sidebar:
        st.write("📜 **專案日誌**")
        for log in st.session_state.game_state["logs"][-5:]:
            st.caption(log)
        if st.button("🔄 重置遊戲"):
            st.session_state.clear()
            st.rerun()

# ==========================================
# Chapter 1: 開工申報 (重磅更新)
# ==========================================
def render_chapter_1():
    st.header("📂 第一章：開工申報 & 前置作業")
    
    # 1. 參數設定區 (決定環保任務難度)
    with st.expander("🛠️ 專案參數設定 (影響環保任務)", expanded=True):
        c1, c2, c3 = st.columns(3)
        area = c1.number_input("基地面積 (m²)", value=500, step=100)
        dur = c2.number_input("預計工期 (月)", value=10, step=1)
        # 計算門檻
        threshold = area * dur
        is_high_pollution = threshold > 4600
        c3.metric("污染係數 (面積x工期)", f"{threshold}", delta="高污染" if is_high_pollution else "一般", delta_color="inverse")
        
        # 更新 session state
        st.session_state.game_state["project_area"] = area
        st.session_state.game_state["project_duration"] = dur

    col_quest, col_system = st.columns([3, 2])
    
    # --- 左側：任務列表 ---
    with col_quest:
        config_type = st.session_state.game_state["config"]["type"]
        
        # A. 拆除副本 (Demolition Gauntlet)
        if "拆併建" in config_type:
            st.subheader("🔥 副本：拆除七大封印")
            st.caption("必須解除所有封印，才能進行開工申報。")
            
            # 使用 container 模擬清單
            with st.container(border=True):
                cols = st.columns(3)
                completed_seals = st.session_state.game_state["demo_seals_cleared"]
                
                for i, (sid, data) in enumerate(DEMO_SEALS.items()):
                    is_done = sid in completed_seals
                    icon = "✅" if is_done else "🔒"
                    
                    with cols[i % 3]:
                        st.markdown(f"**{icon} {data['name']}**")
                        if not is_done:
                            if sid == "D01": # 鄰房鑑定特殊邏輯
                                if st.button("鑑定", key=sid):
                                    st.session_state.game_state["demo_seals_cleared"].append(sid)
                                    # 成功鑑定，Ch3 自動開啟護盾
                                    st.session_state.game_state["is_demo_shield_active"] = True
                                    add_log("完成鄰房鑑定 (護盾GET)。")
                                    st.rerun()
                                if st.button("簽切結 (賭博)", key=f"{sid}_risk"):
                                    st.session_state.game_state["demo_seals_cleared"].append(sid)
                                    st.session_state.game_state["risk_level"] += 50
                                    add_log("簽署切結書 (風險+50%)。")
                                    st.rerun()
                            else:
                                if st.button("執行", key=sid):
                                    st.session_state.game_state["demo_seals_cleared"].append(sid)
                                    st.rerun()
            
            # 檢查封印是否全解
            seals_all_clear = len(completed_seals) == 7
        else:
            seals_all_clear = True # 素地直接通過

        # B. 環保局的考驗 (Green Quest)
        st.subheader("🌳 支線：環保局的考驗")
        with st.container(border=True):
            # 任務 G01: 空污費 (必做)
            st.checkbox("G01 空污費申報 (NW1000)", value=True, disabled=True)
            
            # 任務 G02: 逕流廢水 (條件觸發)
            if is_high_pollution:
                g02 = st.checkbox("G02 逕流廢水削減計畫 (NW1100)", key="g02")
                if not g02: st.caption("⚠️ 係數 > 4600，必須執行！")
            else:
                st.markdown("~~G02 逕流廢水削減計畫~~ (規模未達標，免辦)")
                g02 = True
                
            # 任務 G03: B8 廢棄物 (拆併建必做)
            if "拆併建" in config_type:
                # 檢查 D03 是否完成 (B8廢棄物計畫在七大封印裡)
                has_b8_plan = "D03" in st.session_state.game_state["demo_seals_cleared"]
                st.checkbox("G03 營建混合物 B8 (NW2700)", value=has_b8_plan, disabled=True)
                g03 = has_b8_plan
            else:
                st.markdown("~~G03 營建混合物 B8~~ (素地免辦)")
                g03 = True

            green_quest_ok = g02 and g03

    # --- 右側：數位門禁與送件 ---
    with col_system:
        st.subheader("💻 數位憑證閘門")
        
        # 步驟 1: 插卡
        if not st.session_state.game_state["hicos_connected"]:
            st.error("⛔ 未偵測到憑證")
            if st.button("插入：工商憑證卡"):
                with st.spinner("讀取 HiCOS 元件..."):
                    time.sleep(1)
                st.session_state.game_state["hicos_connected"] = True
                st.rerun()
        else:
            st.success("🟢 HiCOS 已連線 (身份驗證通過)")
            
            # 步驟 2: 無紙化上傳 (Time Attack 警告)
            st.markdown("---")
            st.markdown("**無紙化掛件系統**")
            
            # 檢查前置條件
            ready_to_upload = seals_all_clear and green_quest_ok
            
            if not seals_all_clear:
                st.warning("🔒 封印未解：請先完成左側「拆除副本」。")
            elif not green_quest_ok:
                st.warning("🔒 環保卡關：請完成左側「環保任務」。")
            else:
                st.info("⏱️ Time Attack 警告：\n線上送出後，必須在 **24小時** 內送達紙本，否則退件！")
                
                if st.button("進入虛擬桌面 (轉檔與上傳)", type="primary"):
                    st.session_state.game_state["doing_paperless"] = True
                    st.rerun()

            # 步驟 3: 最終狀態
            if st.session_state.game_state["commencement_done"]:
                st.success("🎉 **開工申報完成！**")
                st.caption("進入 24hr 紙本倒數計時...")

# ==========================================
# 無紙化小遊戲 (更新支援 NW 編碼)
# ==========================================
def render_paperless_minigame():
    st.title("💻 台北市無紙化上傳系統")
    st.info("任務：將原始檔轉為 PDF，並依照規定命名 (NWxxxx)。")
    
    if st.button("🔙 放棄並返回"):
        st.session_state.game_state["doing_paperless"] = False
        st.rerun()

    c_ws, c_list = st.columns([2, 1])
    with c_ws:
        st.subheader("🛠️ 轉檔工作區")
        with st.container(border=True):
            col_a, col_b, col_c = st.columns([2, 2, 1])
            
            raws = st.session_state.game_state["paperless_raw_files"]
            sel_raw = col_a.selectbox("選擇原始檔", raws) if raws else None
            sel_code = col_b.selectbox("選擇 NW 編碼", ["請選擇..."] + list(NW_CODES.keys()))
            
            if col_c.button("轉檔", disabled=not sel_raw):
                st.session_state.game_state["paperless_raw_files"].remove(sel_raw)
                # 模擬轉檔命名
                new_name = f"{sel_code}.pdf"
                st.session_state.game_state["paperless_processed_files"].append(new_name)
                st.toast(f"已轉檔：{new_name}")
                st.rerun()
        
        st.write("#### 待上傳清單")
        processed = st.session_state.game_state["paperless_processed_files"]
        st.multiselect("確認檔案", processed, default=processed, disabled=True)
        
        if st.button("🚀 確認送出 (啟動計時)", type="primary", use_container_width=True):
            # 簡易檢查：必須要有開工申報書 (NW0100)
            if any("NW0100" in f for f in processed):
                st.session_state.game_state["commencement_done"] = True
                st.session_state.game_state["doing_paperless"] = False
                st.balloons()
                add_log("線上掛號成功！紙本計時開始。")
                st.rerun()
            else:
                st.error("退件：缺少 NW0100 開工申報書！")

    with c_list:
        st.markdown("📜 **編碼對照表**")
        data = [{"代碼":k, "名稱":v["name"]} for k,v in NW_CODES.items()]
        st.dataframe(data, hide_index=True, use_container_width=True)

# ==========================================
# 其他章節 (保持邏輯連貫)
# ==========================================
def render_chapter_2():
    st.header("📜 第二章：施工計畫")
    if not st.session_state.game_state["commencement_done"]:
        st.warning("🔒 鎖定中：請先完成第一章。")
        return
    # (此處程式碼與之前相同，省略以節省篇幅，請保留原有的 Ch2 邏輯)
    st.info("功能與之前版本相同：收集六大寶石...")
    if st.button("✨ 核定計畫 (快速通道)", key="ch2_pass"):
        st.session_state.game_state["plan_approved"] = True
        st.rerun()

def render_chapter_3():
    st.header("🚜 第三章：拆除整備")
    if not st.session_state.game_state["plan_approved"]:
        st.warning("🔒 鎖定中：請先完成第二章。")
        return
    
    config_type = st.session_state.game_state["config"]["type"]
    if "素地" in config_type:
        st.success("素地免拆，直接通過。")
        st.session_state.game_state["demo_phase_passed"] = True
        return

    st.info("拆併建模式：執行物理拆除。")
    # 檢查 Ch1 是否有鑑定
    has_shield = st.session_state.game_state["is_demo_shield_active"]
    risk = st.session_state.game_state["risk_level"]
    
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"🛡️ 護盾狀態：{'✅ 開啟' if has_shield else '❌ 無 (高風險)'}")
        st.write(f"🔥 風險值：{risk}%")
    
    with col2:
        if st.button("執行拆除"):
            # 簡單判定：如果有風險值，機率觸發鄰損
            if risk > 0 and random.randint(1, 100) < risk:
                st.error("💥 發生鄰損！因為您當初簽切結書跳過鑑定...")
                add_log("鄰損發生！工程暫停。")
            else:
                st.success("拆除完成！(運氣不錯)")
                st.session_state.game_state["demo_phase_passed"] = True
                st.session_state.game_state["b5_closed"] = True # 簡化流程

def render_chapter_4():
    st.header("🧱 第四章：導溝勘驗")
    if not st.session_state.game_state["demo_phase_passed"]:
        st.warning("🔒 請先完成第三章。")
        return
    if st.button("申報勘驗 (快速通道)"): 
        st.session_state.game_state["guide_wall_inspected"] = True
        st.rerun()

def render_chapter_5():
    st.header("🏯 終章：放樣勘驗")
    if not st.session_state.game_state["guide_wall_inspected"]:
        st.warning("🔒 請先完成第四章。")
        return
    st.success("BOSS 戰區域...")
    if st.button("通關", type="primary"):
        st.balloons()

def add_log(msg):
    st.session_state.game_state["logs"].append(f"{time.strftime('%H:%M')} - {msg}")

if __name__ == "__main__":
    main()