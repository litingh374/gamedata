import streamlit as st
import time
from gamedata import REGIONS, PROJECT_TYPES, TRIALS, GEMS, SETTING_OUT_STEPS, NW_CODES

# ==========================================
# 0. 核心狀態管理
# ==========================================
if 'game_state' not in st.session_state:
    st.session_state.game_state = {
        "stage": "Launcher",
        "config": {},
        
        # Ch1: 開工
        "completed_trials": [],
        "commencement_done": False,
        
        # Ch2: 施工計畫
        "collected_gems": [],
        "plan_approved": False,
        
        # Ch3: 拆除 (條件式)
        "is_demo_shield_active": False,
        "demo_progress": 0,
        "b5_closed": False,
        "demo_phase_passed": False, # 拆除階段是否通過(或跳過)
        
        # Ch4: 導溝 (新增)
        "guide_wall_progress": 0,
        "guide_wall_inspected": False,
        
        # Ch5: 放樣 BOSS
        "boss_hp": 100,
        "logs": []
    }

def main():
    st.set_page_config(page_title="跑照大作戰：導溝完全版", layout="wide", page_icon="🏗️")
    
    if st.session_state.game_state["stage"] == "Launcher":
        render_launcher()
    else:
        render_main_game()

# ==========================================
# 遊戲大廳
# ==========================================
def render_launcher():
    st.title("🏗️ 跑照大作戰：建立新專案")
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            region = st.radio("基地位置", REGIONS)
            is_mrt = st.checkbox("捷運沿線管制")
        with col2:
            p_type = st.radio("開發類型", PROJECT_TYPES)
            if "拆併建" in p_type:
                st.error("⚠️ 拆併建模式：將開啟 Ch3 拆除章節與 B5 陷阱！")
            else:
                st.success("✅ 素地新建：Ch3 拆除章節將自動跳過。")
        
        if st.button("🚀 生成專案", type="primary", use_container_width=True):
            st.session_state.game_state["config"] = {"region": region, "type": p_type, "is_mrt": is_mrt}
            
            # 如果是素地，預設拆除階段為通過，且無 B5 問題
            if "素地" in p_type:
                st.session_state.game_state["demo_phase_passed"] = True
                st.session_state.game_state["b5_closed"] = True # 素地視為無 B5 問題
            
            st.session_state.game_state["stage"] = "MainGame"
            st.rerun()

# ==========================================
# 主遊戲介面 (五章節)
# ==========================================
def render_main_game():
    cfg = st.session_state.game_state["config"]
    st.title(f"🏗️ 專案執行中：{cfg['type']}")
    
    # 五大分頁
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

# --- Ch1: 開工申報 ---
def render_chapter_1():
    st.header("📂 第一章：開工申報")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("七大試煉")
        completed = st.session_state.game_state["completed_trials"]
        for tid, data in TRIALS.items():
            is_done = tid in completed
            icon = "✅" if is_done else "🔲"
            if st.button(f"{icon} {data['name']}", key=tid, disabled=is_done):
                if tid == "T04":
                    with st.spinner("無紙化上傳中..."): time.sleep(0.5)
                st.session_state.game_state["completed_trials"].append(tid)
                st.rerun()
    with col2:
        st.subheader("狀態")
        if len(completed) == 7:
            st.success("文件齊全！")
            if st.button("🚀 申報開工", type="primary"):
                st.session_state.game_state["commencement_done"] = True
                st.balloons()
                add_log("開工申報完成。")
        else:
            st.info(f"進度：{len(completed)}/7")

# --- Ch2: 施工計畫 ---
def render_chapter_2():
    st.header("📜 第二章：施工計畫")
    if not st.session_state.game_state["commencement_done"]:
        st.warning("🔒 請先完成第一章。")
        return
    
    col1, col2 = st.columns([2, 1])
    collected = st.session_state.game_state["collected_gems"]
    with col1:
        st.subheader("六大寶石")
        cols = st.columns(3)
        for i, (key, data) in enumerate(GEMS.items()):
            with cols[i % 3]:
                is_got = key in collected
                btn_type = "secondary" if is_got else "primary"
                if st.button(f"獲取\n{data['name']}", key=key, type=btn_type, disabled=is_got):
                    st.session_state.game_state["collected_gems"].append(key)
                    add_log(f"獲得：{data['name']}")
                    st.rerun()
    with col2:
        st.subheader("狀態")
        if len(collected) == 6:
            if st.button("✨ 核定計畫", type="primary"):
                st.session_state.game_state["plan_approved"] = True
                st.success("計畫核定！")
                add_log("施工計畫核定。")
        else:
            st.write(f"收集：{len(collected)}/6")

# --- Ch3: 拆除整備 (條件式) ---
def render_chapter_3():
    st.header("🚜 第三章：拆除整備")
    
    # 前置檢查
    if not st.session_state.game_state["plan_approved"]:
        st.warning("🔒 請先完成第二章施工計畫。")
        return

    config_type = st.session_state.game_state["config"]["type"]
    
    # 判斷是否為素地
    if "素地" in config_type:
        st.success("✅ **素地新建模式**")
        st.info("本案無需拆除，系統自動判定本章節通過。")
        st.markdown("您可以直接前往第四章「導溝勘驗」。")
        # 確保狀態正確
        st.session_state.game_state["demo_phase_passed"] = True
        st.session_state.game_state["b5_closed"] = True 
        return

    # 拆併建邏輯
    st.error("⚠️ **拆併建模式：必須執行拆除！**")
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("辦公室作業")
        if st.button("1. 鄰房鑑定 (護盾)"):
            st.session_state.game_state["is_demo_shield_active"] = True
            st.success("護盾 ON")
        
        if st.button("2. B5 廢棄物結案"):
            st.session_state.game_state["b5_closed"] = True
            st.success("B5 已結案")
            add_log("B5 結案完成。")
            
        if st.session_state.game_state["b5_closed"]:
            st.info("✅ B5 結案狀態：OK")
        else:
            st.warning("❌ B5 結案狀態：未結案 (將影響後續)")

    with c2:
        st.subheader("現場作業")
        if st.button("執行拆除"):
            if not st.session_state.game_state["is_demo_shield_active"]:
                st.error("💥 未鑑定即拆除！發生鄰損！")
                add_log("發生鄰損事件。")
            else:
                st.session_state.game_state["demo_progress"] = 100
                st.success("拆除完成！")
                add_log("拆除作業完成。")

    # 通關判定
    if st.session_state.game_state["demo_progress"] >= 100:
        st.session_state.game_state["demo_phase_passed"] = True
        st.success("🌟 拆除階段完成！請前往導溝勘驗。")

# --- Ch4: 導溝勘驗 (新增獨立章節) ---
def render_chapter_4():
    st.header("🧱 第四章：導溝勘驗")
    
    # 前置檢查：必須通過 Ch3 (無論是跳過還是做完)
    if not st.session_state.game_state["demo_phase_passed"]:
        st.warning("🔒 請先完成第三章拆除整備。")
        return

    col_gw1, col_gw2 = st.columns(2)
    
    with col_gw1:
        st.subheader("現場施作：導溝")
        gw_prog = st.session_state.game_state["guide_wall_progress"]
        st.progress(gw_prog / 100, text=f"施作進度: {gw_prog}%")
        
        if gw_prog < 100:
            if st.button("挖溝 & 綁紮 & 澆置"):
                st.session_state.game_state["guide_wall_progress"] += 50
                st.rerun()
        else:
            st.success("✅ 導溝施作完畢")

    with col_gw2:
        st.subheader("行政查驗：申報勘驗")
        
        if gw_prog >= 100:
            if st.button("📞 申報導溝勘驗", type="primary"):
                # 這裡檢查 B5 陷阱！
                # 如果是拆併建，且 B5 沒結案，就算現場做好了也會被退件
                config_type = st.session_state.game_state["config"]["type"]
                b5_ok = st.session_state.game_state["b5_closed"]
                
                if "拆併建" in config_type and not b5_ok:
                    st.error("🚫 **退件！**")
                    st.markdown("建管處：系統查無 **B5 拆除廢棄物結案** 紀錄。")
                    st.caption("雖然導溝做好了，但行政程序未完成，無法勘驗。請回第三章補辦結案。")
                else:
                    st.session_state.game_state["guide_wall_inspected"] = True
                    st.balloons()
                    st.success("🎉 勘驗合格！准予進行放樣。")
                    add_log("導溝勘驗通過。")
        else:
            st.info("請先完成現場施作。")

# --- Ch5: 放樣 BOSS ---
def render_chapter_5():
    st.header("🏯 終章：放樣勘驗 (BOSS)")
    
    # 前置檢查
    if not st.session_state.game_state["guide_wall_inspected"]:
        st.error("🔒 卡關！請先完成第四章「導溝勘驗」。")
        return

    st.success("🌟 條件符合，准予掛號！")
    hp = st.session_state.game_state["boss_hp"]
    st.metric("放樣審查 BOSS", f"HP: {hp}/100")
    
    if st.button("⚔️ 發動攻擊"):
        st.session_state.game_state["boss_hp"] = max(0, hp - 20)
        st.rerun()
        
    if st.session_state.game_state["boss_hp"] == 0:
        st.balloons()
        st.success("🏆 恭喜通關！准予放樣！建築物正式長出來啦！")

def add_log(msg):
    st.session_state.game_state["logs"].append(f"{time.strftime('%H:%M')} - {msg}")

if __name__ == "__main__":
    main()