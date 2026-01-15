import streamlit as st
import time
import random
import os
from gamedata import GEMS, SETTING_OUT_STEPS

# ==========================================
# 0. 核心狀態管理 (State Management)
# ==========================================
if 'game_state' not in st.session_state:
    st.session_state.game_state = {
        "current_chapter": "Chapter_2_MasterPlan", # 起始章節
        
        # --- Chapter 2: 施工計畫 ---
        "architect_plan_ready": False, # 結構圖說 (建築師)
        "ping_count": 0,               # 催圖次數
        "collected_gems": [],          # 已收集的寶石
        "master_plan_approved": False, # 施工計畫核定
        
        # --- Chapter 3: 拆除與導溝 ---
        "demolition_permit": False,    # 拆除執照 (Buff)
        "demolition_progress": 0,      # 拆除進度
        "site_cleared": False,         # 基地整理完畢
        "office_tasks": [],            # 跑照人員的任務 (B5, 斜坡道, 水電)
        
        # --- Chapter 4: 放樣 BOSS ---
        "boss_hp": 100,
        "current_step_index": 0,       # 目前打到第幾關
        "is_game_cleared": False
    }

def main():
    st.set_page_config(page_title="跑照大作戰：三界協同版", layout="wide", page_icon="🏗️")
    
    # 渲染三界狀態欄 (固定在頂部)
    render_three_realms_header()
    
    # 章節路由
    chapter = st.session_state.game_state["current_chapter"]
    
    if chapter == "Chapter_2_MasterPlan":
        render_chapter_2()
    elif chapter == "Chapter_3_DoubleHelix":
        render_chapter_3()
    elif chapter == "Chapter_4_SettingOut":
        render_chapter_4()
    elif chapter == "Ending":
        render_ending()

# ==========================================
# UI 元件：三界協同系統 (The Three Realms)
# ==========================================
def render_three_realms_header():
    """顯示遊戲上方的三層狀態欄"""
    st.markdown("### 🏛️ 三界協同狀態 (Synergy System)")
    c1, c2, c3 = st.columns(3)
    
    # 上層：橘色神界 (建築師)
    with c1:
        st.warning("🧙‍♂️ **上層：建築師 (NPC)**")
        if st.session_state.game_state["architect_plan_ready"]:
            st.markdown("狀態：🟢 **心情愉悅** (圖說已出)")
        else:
            st.markdown("狀態：🔴 **閉關修煉中** (請勿打擾)")
            
    # 中層：黃色人界 (跑照人員)
    with c2:
        st.info("🏃 **中層：跑照人員 (Player)**")
        gems = len(st.session_state.game_state["collected_gems"])
        st.markdown(f"任務道具：🎒 已收集 {gems}/6 寶石")

    # 下層：綠色地界 (工地現場)
    with c3:
        st.success("👷 **下層：工地現場 (Constructor)**")
        if st.session_state.game_state["demolition_permit"]:
            st.markdown("Buff：🛡️ **拆除執照生效中**")
        else:
            st.markdown("Buff：❌ **無許可證** (小心罰單怪獸)")
    
    st.markdown("---")

# ==========================================
# Chapter 2: 施工計畫的試煉 (The Master Plan)
# ==========================================
def render_chapter_2():
    st.title("📜 第二章：施工計畫的試煉")
    st.markdown("目標：取得建築師圖說，並收集六大寶石，合成【施工計畫核定本】。")

    col_architect, col_gems = st.columns([1, 2])

    # --- 任務 1: 結構外審 (Architect Dependency) ---
    with col_architect:
        with st.container(border=True):
            st.subheader("🧙‍♂️ 建築師塔")
            if st.session_state.game_state["architect_plan_ready"]:
                st.success("✨ 道具取得：\n核備結構圖說")
                st.image("https://placeholder.co/300x200?text=Approved+Plan", caption="關鍵道具")
            else:
                st.error("🔒 任務鎖定：等待結構外審")
                st.caption("建築師 NPC 正在施法中...")
                
                # Ping 機制
                if st.button("🔔 Ping (催圖)", type="primary"):
                    st.session_state.game_state["ping_count"] += 1
                    chance = random.randint(1, 10)
                    # 隨著催圖次數增加，成功率提升，但也可能激怒建築師
                    if chance > 7 or st.session_state.game_state["ping_count"] > 3:
                        st.session_state.game_state["architect_plan_ready"] = True
                        st.toast("🎉 建築師終於把圖丟出來了！", icon="📜")
                        st.rerun()
                    else:
                        st.toast(f"建築師：別催了！還在畫！(已催 {st.session_state.game_state['ping_count']} 次)", icon="💢")

    # --- 任務 2: 六大寶石收集 ---
    with col_gems:
        with st.container(border=True):
            st.subheader("💎 六大寶石收集 (The 6 Elements)")
            
            # 檢查是否解鎖
            if not st.session_state.game_state["architect_plan_ready"]:
                st.warning("⚠️ 請先取得【結構圖說】以解鎖施工計畫製作。")
            else:
                cols = st.columns(3)
                collected = st.session_state.game_state["collected_gems"]
                
                for i, (key, data) in enumerate(GEMS.items()):
                    with cols[i % 3]:
                        is_collected = key in collected
                        icon = "✅" if is_collected else "💎"
                        btn_type = "secondary" if is_collected else "primary"
                        
                        st.markdown(f"**{data['name']}**")
                        st.caption(data['desc'])
                        
                        if st.button(f"{icon} 獲取", key=key, type=btn_type, disabled=is_collected):
                            # Mini-game 模擬 (例如公會說明會)
                            if key == "GEM_GUILD":
                                st.toast("📢 舉辦鄰里說明會...安撫成功！", icon="🤝")
                            elif key == "GEM_TRAFFIC":
                                st.toast("🚚 規劃卡車路線...交通局核准！", icon="🚦")
                            
                            st.session_state.game_state["collected_gems"].append(key)
                            st.rerun()
                
                # 合成按鈕
                st.markdown("---")
                if len(collected) == 6:
                    if st.button("✨ 合成：施工計畫核定本 (前往下一章)", type="primary", use_container_width=True):
                        st.session_state.game_state["master_plan_approved"] = True
                        st.balloons()
                        time.sleep(2)
                        st.session_state.game_state["current_chapter"] = "Chapter_3_DoubleHelix"
                        st.rerun()

# ==========================================
# Chapter 3: 拆除與導溝的雙重奏 (Parallel Processing)
# ==========================================
def render_chapter_3():
    st.title("🚜 第三章：拆除與導溝的雙重奏")
    st.markdown("目標：辦理 B5 結案與水電，同時指揮工地進行拆除。")

    c_office, c_site = st.columns(2)

    # --- 黃色線：辦公室任務 ---
    with c_office:
        st.info("🏃 **辦公室 (Office Ops)**")
        
        # 任務清單
        tasks = {
            "B5_CLOSE": "建管處：拆除土方 B5 結案",
            "SLOPE_PERMIT": "新工處：車行斜坡道許可",
            "TEMP_POWER": "台電：施工用臨時水電"
        }
        
        for t_code, t_name in tasks.items():
            checked = t_code in st.session_state.game_state["office_tasks"]
            if st.checkbox(t_name, value=checked, key=t_code):
                if not checked:
                    st.session_state.game_state["office_tasks"].append(t_code)
                    st.toast(f"已完成：{t_name}")
        
        # 給予工地 Buff
        st.markdown("---")
        if not st.session_state.game_state["demolition_permit"]:
            if st.button("🛡️ 發送 Buff：給予拆除許可證"):
                st.session_state.game_state["demolition_permit"] = True
                st.success("已將許可證快遞給工地主任！")
                st.rerun()
        else:
            st.write("✅ 已發送拆除許可")

    # --- 綠色線：工地現場 ---
    with c_site:
        st.success("👷 **工地現場 (Site Ops)**")
        
        # 檢查 Buff
        has_buff = st.session_state.game_state["demolition_permit"]
        
        st.write(f"當前拆除進度：{st.session_state.game_state['demolition_progress']}%")
        prog_bar = st.progress(st.session_state.game_state["demolition_progress"] / 100)

        if st.button("🚜 執行：拆除作業 (物理攻擊)"):
            if not has_buff:
                st.error("👾 遭遇罰單怪獸！")
                st.toast("環保局開罰：沒有許可證就動工！扣除信譽值！", icon="💸")
            else:
                new_prog = min(100, st.session_state.game_state["demolition_progress"] + 25)
                st.session_state.game_state["demolition_progress"] = new_prog
                if new_prog == 100:
                    st.session_state.game_state["site_cleared"] = True
                    st.toast("拆除完畢！基地已整平。", icon="🏗️")
                st.rerun()

    # --- BOSS 戰觸發：導溝勘驗 ---
    st.markdown("---")
    # 條件：辦公室 3 任務全解 + 工地拆除 100%
    office_ready = len(st.session_state.game_state["office_tasks"]) == 3
    site_ready = st.session_state.game_state["site_cleared"]
    
    if office_ready and site_ready:
        st.success("🌟 雙線任務完成！導溝勘驗準備就緒。")
        if st.button("⚔️ 挑戰 BOSS：放樣勘驗 (進入最終章)", type="primary", use_container_width=True):
            st.session_state.game_state["current_chapter"] = "Chapter_4_SettingOut"
            st.rerun()
    else:
        st.caption(f"解鎖進度：辦公室 ({len(st.session_state.game_state['office_tasks'])}/3) | 工地 ({'完成' if site_ready else '進行中'})")

# ==========================================
# Chapter 4: 放樣勘驗大審查 (The Setting Out)
# ==========================================
def render_chapter_4():
    st.title("🏯 最終章：放樣勘驗大審查")
    st.markdown("這是實質興建前的大魔王。必須依序擊破五個階段。")

    # BOSS HP Bar
    current_step_idx = st.session_state.game_state["current_step_index"]
    
    # 計算剩餘 HP (視覺效果)
    total_hp = 100
    current_damage = 0
    for i in range(current_step_idx):
        current_damage += SETTING_OUT_STEPS[i]['hp']
    remaining_hp = max(0, total_hp - current_damage)
    
    st.metric("BOSS 血量 (審查刁難度)", f"{remaining_hp} / 100")
    st.progress(remaining_hp / 100)

    # 戰鬥區域
    col_battle, col_visual = st.columns([1, 1])

    with col_battle:
        if current_step_idx < len(SETTING_OUT_STEPS):
            step = SETTING_OUT_STEPS[current_step_idx]
            
            with st.container(border=True):
                st.subheader(f"🛡️ 第 {current_step_idx + 1} 關：{step['name']}")
                st.write(step['desc'])
                st.write(f"造成傷害：{step['hp']} 點")
                
                # 特殊事件：現場會勘
                if step['id'] == "S3":
                    st.warning("⚠️ 警告：建築師 NPC 與公務員 NPC 同時進場！")
                    st.image("https://placeholder.co/400x200?text=Site+Inspection", caption="工地模擬圖")
                
                if st.button("⚔️ 發動攻擊 (執行)", type="primary"):
                    with st.spinner("技能施放中..."):
                        time.sleep(1)
                    
                    st.session_state.game_state["current_step_index"] += 1
                    st.toast(f"擊破 {step['name']}！BOSS 受傷！", icon="💥")
                    st.rerun()
        else:
            # 通關
            st.session_state.game_state["current_chapter"] = "Ending"
            st.rerun()

    with col_visual:
        # 顯示通關紀錄
        st.write("### 📜 戰鬥紀錄")
        for i, step in enumerate(SETTING_OUT_STEPS):
            if i < current_step_idx:
                st.write(f"✅ {step['name']} [擊破]")
            elif i == current_step_idx:
                st.write(f"⚔️ **{step['name']} [戰鬥中]**")
            else:
                st.write(f"🔒 {step['name']} [未解鎖]")

# ==========================================
# Ending: 結局
# ==========================================
def render_ending():
    st.balloons()
    st.title("🏆 Game Clear！准予放樣")
    st.success("恭喜！你成功協調了神界、人界與地界，完成了不可能的任務。")
    st.image("https://placeholder.co/600x400?text=Construction+Starts+NOW", caption="怪手正式進場")
    st.markdown("### 你的成就：")
    st.markdown("- 獲得稱號：**傳說的跑照大師**")
    st.markdown("- 建築物開始一層層長出來...")
    
    if st.button("🔄 重新開始新案子"):
        st.session_state.clear()
        st.rerun()

if __name__ == "__main__":
    main()