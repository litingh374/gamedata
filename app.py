# 在 gamedata.py 中可以新增這些資料
# CONSTRUCTION_METHODS = {
#     "bottom_up": {"name": "順打工法", "cost": 0, "speed": 1.0, "risk": "low"},
#     "top_down": {"name": "逆打工法", "cost": 5000000, "speed": 1.3, "risk": "high"}
# }

# 在 app.py 的 render_chapter_2 中新增

def render_chapter_2():
    st.header("📜 第二章：施工計畫 (戰略部署)")
    
    # 1. 工法選擇 (Methodology)
    st.subheader("1. 決定施工戰略")
    method = st.radio("選擇開挖工法", 
        ["順打工法 (標準)", "逆打工法 (高風險/高報酬)"], 
        help="逆打工法可縮短工期，但需額外購買鋼柱道具，且結構體階段容易漏水。"
    )
    
    # 儲存選擇
    if "逆打" in method:
        st.session_state.game_state["construction_method"] = "top_down"
        st.info("💡 已啟用逆打模式：工期縮短，但 Ch7 難度提升。")
    else:
        st.session_state.game_state["construction_method"] = "bottom_up"

    st.markdown("---")

    # 2. 人員配置 (Team Setup)
    st.subheader("2. 組建黃金陣容")
    col_p1, col_p2, col_p3 = st.columns(3)
    
    with col_p1:
        st.markdown("👷 **工地主任**")
        # 檢查背包是否有證照
        has_cert = "NW3500" in st.session_state.game_state.get("paperless_processed_files", []) or \
                   any("工地主任" in f for f in st.session_state.game_state["paperless_raw_files"])
        
        director = st.selectbox("指派人選", ["請選擇...", "資深主任 (老王)", "菜鳥主任 (阿明)"])
        if director == "資深主任 (老王)":
            st.caption("費用高，免疫「承辦刁難」。")
        elif director == "菜鳥主任 (阿明)":
            st.caption("費用低，放樣時可能忘帶章。")
            
    with col_p2:
        st.markdown("🏗️ **專任工程人員**")
        pe = st.selectbox("指派技師", ["請選擇...", "主任技師", "兼職技師"])
    
    with col_p3:
        st.markdown("⛑️ **勞安人員**")
        safety = st.selectbox("指派勞安", ["請選擇...", "專職勞安", "無 (違法)"])
        if safety == "無 (違法)":
            st.error("⚠️ 風險警告：發生意外將直接停工！")

    st.markdown("---")

    # 3. 原有的寶石收集 (保持不變)
    st.subheader("3. 收集計畫書素材 (六大寶石)")
    # ... (保留原本的寶石收集代碼) ...
    
    # 綜合判斷按鈕
    if st.button("✨ 送出施工計畫書 (合成)"):
        # 檢查邏輯
        if director == "請選擇..." or pe == "請選擇...":
            st.error("退件：未配置關鍵人員！施工計畫書不完整。")
        elif safety == "無 (違法)":
            st.error("退件：勞檢處駁回！未配置勞安人員。")
        else:
            # 成功邏輯
            st.session_state.game_state["plan_approved"] = True
            st.balloons()
            st.success("✅ 施工計畫核定！取得「開工許可」。")
            # 根據選擇設定遊戲參數
            if director == "菜鳥主任 (阿明)":
                st.session_state.game_state["risk_level"] += 10
            if "逆打" in method:
                st.session_state.game_state["total_weeks"] -= 10 # 工期縮短
                st.session_state.game_state["budget_used"] += 5000000 # 成本增加
            st.rerun()