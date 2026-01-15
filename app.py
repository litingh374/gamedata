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
        
        # --- Ch1: 開工申報 ---
        "hicos_connected": False,     # 工商憑證
        "project_area": 500,          # 面積
        "project_duration": 10,       # 工期
        "demo_seals_cleared": [],     # 已解封印
        "risk_level": 0,              # 風險值
        "doing_paperless": False,     # 小遊戲狀態
        "commencement_done": False,   # 開工完成
        
        # 無紙化檔案
        "paperless_raw_files": [
            "開工申報書.docx", "空污費收據.jpg", "拆除施工計畫.pdf",
            "鄰房鑑定報告.pdf", "逕流廢水核備函.jpg", "自拍照.jpg"
        ],
        "paperless_processed_files": [],

        # --- Ch2: 施工計畫 ---
        "collected_gems": [],
        "plan_approved": False,
        
        # --- Ch3: 拆除整備 ---
        "is_demo_shield_active": False, # 護盾(鑑定)
        "demo_progress": 0,             # 拆除進度
        "b5_closed": False,             # B5結案狀態
        "demo_phase_passed": False,     # Ch3 通關狀態
        
        # --- Ch4: 導溝勘驗 ---
        "guide_wall_progress": 0,
        "guide_wall_inspected": False,
        
        # --- Ch5: BOSS ---
        "boss_hp": 100,
        "logs": []
    }

def main():
    st.set_page_config(page_title="跑照大作戰：台北市完全體", layout="wide", page_icon="🏗️")
    
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
            
            # 素地預設拆除相關 Pass
            if "素地" in p_type:
                st.session_state.game_state["demo_phase_passed"] = True
                st.session_state.game_state["b5_closed"] = True
                st.session_state.game_state["is_demo_shield_active"] = True
            
            st.session_state.game_state["stage"] = "MainGame"
            st.rerun()

# ==========================================
# 主遊戲介面
# ==========================================
def render_main_game():
    cfg = st.session_state.game_state["config"]
    
    # 無紙化小遊戲路由
    if st.session_state.game_state["doing_paperless"]:
        render_paperless_minigame()
        return

    st.title(f"🏗️ 專案執行中：{cfg['type']}")
    
    # 風險提示
    risk = st.session_state.game_state["risk_level"]
    if risk > 0:
        st.warning(f"⚠️ 當前專案風險值：{risk}% (Ch3 拆除時可能觸發鄰損)")

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
# Chapter 1: 開工申報 (含封印與數位門禁)
# ==========================================
def render_chapter_1():
    st.header("📂 第一章：開工申報")
    
    # 參數設定
    with st.expander("🛠️ 專案參數設定 (影響環保任務)", expanded=True):
        c1, c2, c3 = st.columns(3)
        area = c1.number_input("基地面積 (m²)", value=500, step=100)
        dur = c2.number_input("預計工期 (月)", value=10, step=1)
        threshold = area * dur
        is_high_pollution = threshold > 4600
        c3.metric("污染係數", f"{threshold}", delta="高污染" if is_high_pollution else "一般", delta_color="inverse")
        st.session_state.game_state["project_area"] = area
        st.session_state.game_state["project_duration"] = dur

    col_quest, col_system = st.columns([3, 2])
    
    # --- 左側：任務 ---
    with col_quest:
        config_type = st.session_state.game_state["config"]["type"]
        
        # A. 拆除副本
        if "拆併建" in config_type:
            st.subheader("🔥 副本：拆除七大封印")
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
                                    st.session_state.game_state["is_demo_shield_active"] = True
                                    add_log("完成鄰房鑑定 (護盾開啟)。")
                                    st.rerun()
                                if st.button("簽切結(博)", key=f"{sid}_risk"):
                                    st.session_state.game_state["demo_seals_cleared"].append(sid)
                                    st.session_state.game_state["risk_level"] += 50
                                    add_log("簽署切結書 (風險+50%)。")
                                    st.rerun()
                            else:
                                if st.button("執行", key=sid):
                                    st.session_state.game_state["demo_seals_cleared"].append(sid)
                                    st.rerun()
            seals_all_clear = len(completed_seals) == 7
        else:
            seals_all_clear = True

        # B. 環保局任務
        st.subheader("🌳 支線：環保局的考驗")
        with st.container(border=True):
            st.checkbox("G01 空污費申報 (NW1000)", value=True, disabled=True)
            
            if is_high_pollution:
                g02 = st.checkbox("G02 逕流廢水削減計畫 (NW1100)", key="g02")
                if not g02: st.caption("⚠️ 係數 > 4600，必須執行！")
            else:
                st.markdown("~~G02 逕流廢水削減計畫~~ (免辦)")
                g02 = True
                
            if "拆併建" in config_type:
                has_b8_plan = "D03" in st.session_state.game_state["demo_seals_cleared"]
                st.checkbox("G03 營建混合物 B8 (NW2700)", value=has_b8_plan, disabled=True)
                g03 = has_b8_plan
            else:
                st.markdown("~~G03 營建混合物 B8~~ (免辦)")
                g03 = True
            
            green_quest_ok = g02 and g03

    # --- 右側：數位門禁 ---
    with col_system:
        st.subheader("💻 數位憑證閘門")
        
        if not st.session_state.game_state["hicos_connected"]:
            st.error("⛔ 未偵測到憑證")
            if st.button("插入：工商憑證卡"):
                with st.spinner("讀取 HiCOS..."): time.sleep(1)
                st.session_state.game_state["hicos_connected"] = True
                st.rerun()
        else:
            st.success("🟢 HiCOS 已連線")
            st.markdown("---")
            st.markdown("**無紙化掛件系統**")
            
            ready_to_upload = seals_all_clear and green_quest_ok
            
            if not seals_all_clear:
                st.warning("🔒 請先解除「拆除封印」。")
            elif not green_quest_ok:
                st.warning("🔒 請完成「環保任務」。")
            else:
                st.info("⏱️ Time Attack：線上送出後，24H內送紙本。")
                if st.button("進入虛擬桌面 (上傳)", type="primary"):
                    st.session_state.game_state["doing_paperless"] = True
                    st.rerun()

            if st.session_state.game_state["commencement_done"]:
                st.success("🎉 **開工申報完成！**")

# ==========================================
# 無紙化小遊戲
# ==========================================
def render_paperless_minigame():
    st.title("💻 台北市無紙化上傳系統")
    if st.button("🔙 放棄"):
        st.session_state.game_state["doing_paperless"] = False
        st.rerun()

    c_ws, c_list = st.columns([2, 1])
    with c_ws:
        st.subheader("🛠️ 轉檔工作區")
        with st.container(border=True):
            col_a, col_b, col_c = st.columns([2, 2, 1])
            raws = st.session_state.game_state["paperless_raw_files"]
            sel_raw = col_a.selectbox("原始檔", raws) if raws else None
            sel_code = col_b.selectbox("NW 編碼", ["請選擇..."] + list(NW_CODES.keys()))
            if col_c.button("轉檔", disabled=not sel_raw):
                st.session_state.game_state["paperless_raw_files"].remove(sel_raw)
                new_name = f"{sel_code}.pdf"
                st.session_state.game_state["paperless_processed_files"].append(new_name)
                st.rerun()
        
        st.write("#### 待上傳")
        processed = st.session_state.game_state["paperless_processed_files"]
        st.multiselect("確認", processed, default=processed, disabled=True)
        
        if st.button("🚀 送出電子簽章", type="primary", use_container_width=True):
            if any("NW0100" in f for f in processed):
                st.session_state.game_state["commencement_done"] = True
                st.session_state.game_state["doing_paperless"] = False
                st.balloons()
                add_log("線上掛號成功。")
                st.rerun()
            else:
                st.error("退件：缺少 NW0100 開工申報書！")

    with c_list:
        st.markdown("📜 **編碼表**")
        data = [{"代碼":k, "名稱":v["name"]} for k,v in NW_CODES.items()]
        st.dataframe(data, hide_index=True)

# ==========================================
# Chapter 2: 施工計畫 (功能回歸)
# ==========================================
def render_chapter_2():
    st.header("📜 第二章：施工計畫")
    if not st.session_state.game_state["commencement_done"]:
        st.warning("🔒 鎖定中：請先完成第一章。")
        return
    
    col_gems, col_status = st.columns([2, 1])
    collected = st.session_state.game_state["collected_gems"]
    
    with col_gems:
        st.subheader("六大寶石收集")
        cols = st.columns(3)
        for i, (key, data) in enumerate(GEMS.items()):
            with cols[i % 3]:
                is_got = key in collected
                btn_type = "secondary" if is_got else "primary"
                st.markdown(f"**{data['name']}**")
                if st.button("獲取", key=key, type=btn_type, disabled=is_got):
                    st.session_state.game_state["collected_gems"].append(key)
                    add_log(f"獲得：{data['name']}")
                    st.rerun()
                    
    with col_status:
        st.subheader("審查進度")
        if len(collected) == 6:
            if st.button("✨ 核定計畫", type="primary"):
                st.session_state.game_state["plan_approved"] = True
                st.balloons()
                add_log("施工計畫核定。")
        else:
            st.write(f"收集：{len(collected)}/6")
            
    if st.session_state.game_state["plan_approved"]:
        st.success("✅ 施工計畫已核定")

# ==========================================
# Chapter 3: 拆除整備 (功能回歸)
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
    
    # 讀取 Ch1 的決定 (是否有簽切結書)
    has_shield = st.session_state.game_state["is_demo_shield_active"]
    risk = st.session_state.game_state["risk_level"]
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("辦公室作業")
        st.write(f"🛡️ 護盾狀態：{'✅ 開啟' if has_shield else '❌ 無 (風險!)'}")
        
        # B5 結案
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
            # 風險判定邏輯
            if risk > 0 and random.randint(1, 100) < risk:
                st.error("💥 發生鄰損！因為您之前簽切結書跳過鑑定...")
                add_log("鄰損發生！工程暫停。")
            else:
                st.session_state.game_state["demo_progress"] = 100
                st.success("拆除完成！(運氣不錯)")
                add_log("拆除作業完成。")

    if st.session_state.game_state["demo_progress"] >= 100:
        st.session_state.game_state["demo_phase_passed"] = True
        st.success("🌟 拆除階段完成！")

# ==========================================
# Chapter 4: 導溝勘驗 (功能回歸)
# ==========================================
def render_chapter_4():
    st.header("🧱 第四章：導溝勘驗")
    
    # 雙重檢查
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
                # B5 陷阱檢查
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
# Chapter 5: BOSS 戰 (功能回歸)
# ==========================================
def render_chapter_5():
    st.header("🏯 終章：放樣勘驗")
    if not st.session_state.game_state["guide_wall_inspected"]:
        st.error("🔒 卡關！請先完成第四章。")
        return

    st.success("🌟 條件符合，准予掛號！")
    hp = st.session_state.game_state["boss_hp"]
    st.metric("BOSS HP", f"{hp}/100")
    
    if st.button("⚔️ 發動攻擊 (審查)"):
        st.session_state.game_state["boss_hp"] = max(0, hp - 20)
        st.rerun()
        
    if st.session_state.game_state["boss_hp"] == 0:
        st.balloons()
        st.success("🏆 恭喜通關！准予放樣！建築物正式長出來啦！")

def add_log(msg):
    st.session_state.game_state["logs"].append(f"{time.strftime('%H:%M')} - {msg}")

if __name__ == "__main__":
    main()