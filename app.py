import streamlit as st
import time
import random
from gamedata import REGIONS, PROJECT_TYPES, THRESHOLDS, DEMO_SEALS, GEMS, SETTING_OUT_STEPS, NW_CODES

# ==========================================
# 0. 核心狀態管理
# ==========================================
if 'game_state' not in st.session_state:
    st.session_state.game_state = {
        "stage": "Launcher",
        "config": {},
        
        # --- 專案數值資料 (新) ---
        "project_data": {
            "area": 0, "area_unknown": False,
            "duration": 0, "duration_unknown": False,
            "cost": 0, "cost_unknown": False,
            "floor_area": 0, "floor_area_unknown": False,
        },

        # --- Ch1: 開工申報 ---
        "hicos_connected": False,
        "demo_seals_cleared": [],
        "risk_level": 0,
        "doing_paperless": False,
        "commencement_done": False,
        
        # 無紙化檔案
        "paperless_raw_files": [
            "開工申報書.docx", "空污費收據.jpg", "拆除施工計畫.pdf",
            "鄰房鑑定報告.pdf", "逕流廢水核備函.jpg", "自拍照.jpg"
        ],
        "paperless_processed_files": [],

        # --- Ch2~5 狀態 ---
        "collected_gems": [],
        "plan_approved": False,
        "is_demo_shield_active": False,
        "demo_progress": 0,
        "b5_closed": False,
        "demo_phase_passed": False,
        "guide_wall_progress": 0,
        "guide_wall_inspected": False,
        "boss_hp": 100,
        "logs": []
    }

def main():
    st.set_page_config(page_title="跑照大作戰：資訊迷霧版", layout="wide", page_icon="🏗️")
    
    if st.session_state.game_state["stage"] == "Launcher":
        render_launcher()
    else:
        render_main_game()

# ==========================================
# 遊戲大廳 (全新設計：工程情報表)
# ==========================================
def render_launcher():
    st.title("🏗️ 專案啟動：工程情報輸入")
    
    # --- 1. 快速樣板 (Presets) ---
    st.subheader("🏁 快速開始 (選擇樣板)")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        if st.button("🟢 新手村 (小型透天)", use_container_width=True):
            set_preset("small")
    with col_p2:
        if st.button("🔴 挑戰模式 (大型建案)", use_container_width=True):
            set_preset("large")

    st.markdown("---")

    # --- 2. 自定義輸入 (Custom Input) ---
    st.subheader("📝 自定義專案參數")
    
    with st.container(border=True):
        # 區域與類型
        c1, c2 = st.columns(2)
        region = c1.radio("伺服器 (Server)", REGIONS)
        p_type = c2.radio("劇本 (Scenario)", PROJECT_TYPES)
        
        st.markdown("#### 📐 工程規模數值")
        
        # 基地面積
        cc1, cc2 = st.columns([3, 1])
        area_unk = cc2.checkbox("不清楚面積", key="chk_area")
        area = cc1.number_input("基地面積 (m²)", value=100, disabled=area_unk)
        
        # 預計工期
        cc3, cc4 = st.columns([3, 1])
        dur_unk = cc4.checkbox("不清楚工期", key="chk_dur")
        dur = cc3.number_input("預計工期 (月)", value=6, disabled=dur_unk)
        
        # 工程造價
        cc5, cc6 = st.columns([3, 1])
        cost_unk = cc6.checkbox("不清楚造價", key="chk_cost")
        cost = cc5.number_input("工程造價 (元)", value=3000000, step=100000, disabled=cost_unk)

        # 總樓地板面積
        cc7, cc8 = st.columns([3, 1])
        floor_unk = cc8.checkbox("不清楚樓地板", key="chk_floor")
        floor_area = cc7.number_input("總樓地板面積 (m²)", value=300, disabled=floor_unk)

        # --- 即時回饋 (Live Feedback) ---
        st.markdown("#### 📊 系統預判 (Live Check)")
        
        # 判斷 1: 逕流廢水
        if not area_unk and not dur_unk:
            factor = area * dur
            if factor >= THRESHOLDS["POLLUTION_FACTOR"]:
                st.error(f"⚠️ 係數 {factor} (≥4600)：將觸發【逕流廢水削減計畫】副本！")
            else:
                st.success(f"✅ 係數 {factor}：免辦逕流廢水。")
        else:
            st.info("❔ 資料不足：無法判斷環保係數。")

        # 判斷 2: B8 列管
        b8_trigger = False
        if (not area_unk and area >= THRESHOLDS["B8_AREA"]) or (not cost_unk and cost >= THRESHOLDS["B8_COST"]):
            b8_trigger = True
            st.warning("⚠️ 規模達標：將觸發【營建混合物 B8】列管。")
        elif area_unk or cost_unk:
            st.info("❔ 資料不足：無法判斷廢棄物列管。")
        else:
            st.success("✅ 規模小型：免除 B8 列管。")

        # 判斷 3: 交維計畫
        if not floor_unk and floor_area >= THRESHOLDS["TRAFFIC_AREA"]:
            st.error("⛔ 超大型案件：將觸發【交通維持計畫】魔王關！")

    # --- 啟動按鈕 ---
    if st.button("🚀 確認並生成專案", type="primary", use_container_width=True):
        # 儲存設定
        st.session_state.game_state["config"] = {"region": region, "type": p_type, "is_mrt": False}
        st.session_state.game_state["project_data"] = {
            "area": area, "area_unknown": area_unk,
            "duration": dur, "duration_unknown": dur_unk,
            "cost": cost, "cost_unknown": cost_unk,
            "floor_area": floor_area, "floor_area_unknown": floor_unk
        }
        
        # 素地預設拆除通過
        if "素地" in p_type:
            st.session_state.game_state["demo_phase_passed"] = True
            st.session_state.game_state["b5_closed"] = True
            st.session_state.game_state["is_demo_shield_active"] = True
        
        st.session_state.game_state["stage"] = "MainGame"
        st.rerun()

def set_preset(mode):
    """設定快速樣板"""
    if mode == "small":
        st.session_state.game_state["config"] = {"region": "台北市 (Taipei)", "type": "素地新建 (Empty Land)", "is_mrt": False}
        st.session_state.game_state["project_data"] = {
            "area": 100, "area_unknown": False,
            "duration": 6, "duration_unknown": False,
            "cost": 3000000, "cost_unknown": False,
            "floor_area": 300, "floor_area_unknown": False
        }
        # 素地設定
        st.session_state.game_state["demo_phase_passed"] = True
        st.session_state.game_state["b5_closed"] = True
        st.session_state.game_state["is_demo_shield_active"] = True
        
    elif mode == "large":
        st.session_state.game_state["config"] = {"region": "台北市 (Taipei)", "type": "拆併建照 (Demolition & Build)", "is_mrt": True}
        st.session_state.game_state["project_data"] = {
            "area": 3000, "area_unknown": False,
            "duration": 24, "duration_unknown": False,
            "cost": 200000000, "cost_unknown": False,
            "floor_area": 15000, "floor_area_unknown": False
        }
    
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
# Chapter 1: 開工申報 (含迷霧機制)
# ==========================================
def render_chapter_1():
    st.header("📂 第一章：開工申報")
    
    p_data = st.session_state.game_state["project_data"]
    
    col_quest, col_system = st.columns([3, 2])
    
    # --- 左側：任務列表 ---
    with col_quest:
        config_type = st.session_state.game_state["config"]["type"]
        
        # A. 拆除副本 (維持不變)
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
                            if sid == "D01": 
                                if st.button("鑑定", key=sid):
                                    st.session_state.game_state["demo_seals_cleared"].append(sid)
                                    st.session_state.game_state["is_demo_shield_active"] = True
                                    add_log("完成鄰房鑑定 (護盾開啟)。")
                                    st.rerun()
                                if st.button("簽切結", key=f"{sid}_risk"):
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

        # B. 環保局任務 (加入迷霧機制)
        st.subheader("🌳 支線：環保局的考驗")
        with st.container(border=True):
            st.checkbox("G01 空污費申報 (NW1000)", value=True, disabled=True)
            
            # 判斷 1: 逕流廢水 (依賴 Area, Duration)
            if p_data["area_unknown"] or p_data["duration_unknown"]:
                st.info("🔒 **G02 逕流廢水計畫：資料迷霧中...**")
                if st.button("📞 打電話給建築師 (確認規模)"):
                    # 模擬獲得數據
                    p_data["area"] = random.choice([300, 1000])
                    p_data["duration"] = random.choice([6, 12])
                    p_data["area_unknown"] = False
                    p_data["duration_unknown"] = False
                    st.toast(f"獲得情報：面積 {p_data['area']}, 工期 {p_data['duration']}")
                    st.rerun()
            else:
                # 資料已知，判斷門檻
                factor = p_data["area"] * p_data["duration"]
                if factor >= THRESHOLDS["POLLUTION_FACTOR"]:
                    g02 = st.checkbox(f"G02 逕流廢水 (係數{factor})", key="g02")
                    if not g02: st.caption("⚠️ 必須執行！")
                else:
                    st.markdown(f"~~G02 逕流廢水~~ (係數{factor}未達標)")
                    g02 = True

            # 判斷 2: B8 列管 (依賴 Area, Cost)
            # 這裡簡化邏輯：如果是拆併建，通常都會觸發，但如果是素地，要看規模
            if "拆併建" in config_type:
                # 拆除案必做
                 has_b8_plan = "D03" in st.session_state.game_state["demo_seals_cleared"]
                 st.checkbox("G03 B8廢棄物列管 (拆除觸發)", value=has_b8_plan, disabled=True)
                 g03 = has_b8_plan
            else:
                # 素地看規模
                if p_data["area_unknown"] or p_data["cost_unknown"]:
                     st.info("🔒 **G03 廢棄物列管：資料迷霧中...**")
                     if st.button("📞 詢問老闆 (確認預算)"):
                         p_data["cost"] = random.choice([3000000, 6000000])
                         p_data["cost_unknown"] = False
                         p_data["area_unknown"] = False # 假設一併得知
                         st.toast(f"獲得情報：造價 {p_data['cost']}")
                         st.rerun()
                     g03 = False # 暫時卡住
                else:
                    is_large_scale = (p_data["area"] >= THRESHOLDS["B8_AREA"]) or (p_data["cost"] >= THRESHOLDS["B8_COST"])
                    if is_large_scale:
                        # 這裡沒有實際的 B8 任務按鈕，假設自動列管或需額外動作
                        st.warning("⚠️ 觸發 G03：B8 廢棄物列管 (規模達標)")
                        # 為了遊戲流暢，這裡假設「知情」即算通過，但在真實流程可能需要去填單
                        g03 = True 
                    else:
                        st.markdown("~~G03 B8廢棄物列管~~ (規模未達標)")
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
            
            ready_to_upload = seals_all_clear and green_quest_ok
            
            if not seals_all_clear:
                st.warning("🔒 封印未解")
            elif not green_quest_ok:
                st.warning("🔒 環保任務未完成")
            else:
                if st.button("進入虛擬桌面 (上傳)", type="primary"):
                    st.session_state.game_state["doing_paperless"] = True
                    st.rerun()

            if st.session_state.game_state["commencement_done"]:
                st.success("🎉 **開工申報完成！**")

# ==========================================
# Chapter 2: 施工計畫 (動態難度)
# ==========================================
def render_chapter_2():
    st.header("📜 第二章：施工計畫")
    if not st.session_state.game_state["commencement_done"]:
        st.warning("🔒 鎖定中：請先完成第一章。")
        return
    
    p_data = st.session_state.game_state["project_data"]
    
    col_gems, col_status = st.columns([2, 1])
    collected = st.session_state.game_state["collected_gems"]
    
    with col_gems:
        st.subheader("六大寶石")
        cols = st.columns(3)
        for i, (key, data) in enumerate(GEMS.items()):
            with cols[i % 3]:
                is_got = key in collected
                btn_type = "secondary" if is_got else "primary"
                
                # 特殊邏輯：交通寶石
                gem_name = data['name']
                if key == "GEM_TRAFFIC":
                    if p_data["floor_area_unknown"]:
                        gem_name = "交通寶石 (?)"
                        if st.button("🔍 調查樓地板面積", key="chk_traf"):
                            p_data["floor_area"] = random.choice([5000, 12000])
                            p_data["floor_area_unknown"] = False
                            st.rerun()
                        continue # 暫不顯示獲取按鈕
                    elif p_data["floor_area"] >= THRESHOLDS["TRAFFIC_AREA"]:
                         gem_name = "🔥 交通維持計畫 (魔王)"
                    else:
                         gem_name = "交通維持計畫 (簡易)"

                st.markdown(f"**{gem_name}**")
                if st.button("獲取", key=key, type=btn_type, disabled=is_got):
                    st.session_state.game_state["collected_gems"].append(key)
                    add_log(f"獲得：{gem_name}")
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

# ==========================================
# 無紙化小遊戲 (維持不變)
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
# Chapter 3~5 (邏輯維持不變)
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
            if risk > 0 and random.randint(1, 100) < risk:
                st.error("💥 發生鄰損！因為您之前簽切結書跳過鑑定...")
                add_log("鄰損發生！工程暫停。")
            else:
                st.session_state.game_state["demo_progress"] = 100
                st.success("拆除完成！")
                add_log("拆除作業完成。")

    if st.session_state.game_state["demo_progress"] >= 100:
        st.session_state.game_state["demo_phase_passed"] = True
        st.success("🌟 拆除階段完成！")

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

def render_chapter_5():
    st.header("🏯 終章：放樣勘驗")
    if not st.session_state.game_state["guide_wall_inspected"]:
        st.error("🔒 卡關！請先完成第四章。")
        return
    st.success("🌟 准予掛號！")
    hp = st.session_state.game_state["boss_hp"]
    st.metric("BOSS HP", f"{hp}/100")
    if st.button("⚔️ 發動攻擊"):
        st.session_state.game_state["boss_hp"] = max(0, hp - 20)
        st.rerun()
    if st.session_state.game_state["boss_hp"] == 0:
        st.balloons()
        st.success("🏆 恭喜通關！准予放樣！")

def add_log(msg):
    st.session_state.game_state["logs"].append(f"{time.strftime('%H:%M')} - {msg}")

if __name__ == "__main__":
    main()