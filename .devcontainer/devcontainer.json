import streamlit as st
import os
import json
import shutil
from datetime import datetime

# --- 1. 初始化資料設定 ---
st.set_page_config(page_title="DSE NC", layout="wide")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_DATA_DIR = os.path.join(BASE_DIR, "subjects")
os.makedirs(MAIN_DATA_DIR, exist_ok=True)

# --- 2. 輔助函數 ---
def get_subjects():
    return sorted([d for d in os.listdir(MAIN_DATA_DIR) if os.path.isdir(os.path.join(MAIN_DATA_DIR, d))])

# 修改這裡：加入 filename 參數，預設為 "data.json"
def load_data(sub_path, filename="data.json"):
    f = os.path.join(sub_path, filename)
    return json.load(open(f, 'r', encoding='utf-8')) if os.path.exists(f) else []

# 修改這裡：加入 filename 參數，預設為 "data.json"
def save_data(sub_path, data, filename="data.json"):
    with open(os.path.join(sub_path, filename), 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_reasons(sub_dir):
    # 這裡的邏輯必須是讀取該 sub_dir 底下的檔案
    path = os.path.join(sub_dir, "reasons.json")
    if os.path.exists(path):
        return load_data(sub_dir, "reasons.json")
    return [] # 如果找不到檔案就回傳空列表
# --- 2. 確保在篩選器之前，已經取得 sub_dir 和 all_reasons ---
sub_dir = st.session_state.get('sub_dir', 'default_folder')
all_reasons = get_reasons(sub_dir)        
@st.fragment
@st.fragment
def render_label_editor(sub_dir):
    st.subheader("編輯錯誤原因標籤")
    # 這裡確保讀取的是 reasons.json
    reasons = get_reasons(sub_dir)
    
    with st.expander("➕ 新增標籤"):
        new = st.text_input("輸入新標籤名稱", key="new_label_entry")
        if st.button("確認新增"):
            if not new.strip(): st.error("不能為空")
            elif new.strip() in reasons: st.warning("已存在")
            else:
                reasons.append(new.strip())
                # --- 修正處：改用 save_data ---
                save_data(sub_dir, reasons, "reasons.json") 
                st.rerun()
                
    st.write("---")
    selected = st.multiselect("選取要編輯的標籤", options=reasons, key="editor_multiselect")
    if selected:
        new_names = {label: st.text_input(f"(內容清空即是刪除)編輯 '{label}'", value=label, key=f"input_{label}") for label in selected}
        if st.button("儲存修改"):
            final_list = []
            for label in reasons:
                if label in selected:
                    new_val = new_names[label].strip()
                    if new_val: final_list.append(new_val)
                else: final_list.append(label)
            # --- 修正處：改用 save_data ---
            save_data(sub_dir, final_list, "reasons.json")
            st.success("標籤已更新！")
            st.rerun()

# --- 4. 主程式邏輯 ---
if 'page' not in st.session_state: st.session_state.page = "LIST"
if 'current_subject' not in st.session_state: 
    subs = get_subjects()
    st.session_state.current_subject = subs[0] if subs else "Default"

with st.sidebar:
    st.header("科目管理")
    n = st.text_input("新增科目")
    if st.button("新增") and n:
        os.makedirs(os.path.join(MAIN_DATA_DIR, n), exist_ok=True); st.rerun()
        
    subs = get_subjects()
    if subs:
        # 使用 on_change 來確保在切換的「當下」就清除舊的篩選器狀態
        def change_subject():
            st.session_state.labels = []  # 強制清空標籤篩選
            st.session_state.levels = None # 強制清空難度篩選
            
        st.radio(
            "切換科目", 
            subs, 
            index=subs.index(st.session_state.current_subject),
            on_change=change_subject, 
            key="current_subject"
        )
sub_dir = os.path.join(MAIN_DATA_DIR, st.session_state.current_subject)
os.makedirs(sub_dir, exist_ok=True)
all_entries = load_data(sub_dir)

# --- LIST 頁面 ---
if st.session_state.page == "LIST":
    # --- 關鍵修正：確保這裡重新載入了該科目的標籤 ---

    all_reasons = get_reasons(sub_dir) 
    
    st.header(f"📁 {st.session_state.current_subject} 題目列表")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        # 現在這裡的 options 應該就會有值了
        filter_labels = st.multiselect("標籤", options=all_reasons, key="labels")    
    with col_f2:
        # 1. 初始化變數：無論使用者有沒有選，這裡都給一個初始值 None
        filter_levels = st.selectbox(
            "難度", 
            options=["未評級", "1", "2", "3", "4", "5", "5++"], 
            index=None, 
            placeholder="請選擇難度...", 
            key="levels"
        )
    if st.button("➕ 新增錯題"):
        st.session_state.page = "WRITE"
        st.rerun()

    # 2. 篩選邏輯：確保變數在這裡可以被安全使用
    display_entries = all_entries.copy()
    
    if filter_labels:
        display_entries = [
            item for item in display_entries 
            if all(label in item.get('reasons', []) for label in filter_labels)
        ]
        
    # 這裡檢查 filter_levels 是否有值 (即是否被選取)
    if filter_levels:
        display_entries = [
            item for item in display_entries 
            if str(item.get('level', '未評級')).strip() == str(filter_levels).strip()
        ]
    
    # --- 之後的顯示邏輯 ---    # === 顯示邏輯 (這裡的縮排是最關鍵的) ===
# ... 前面的篩選邏輯 ...
    
    if not display_entries:
        st.info("目前沒有符合篩選條件的題目。")
    else:
        # 1. 為了讓版面整齊，我們改用 grid 佈局或是控制容器生成
        # 這裡的 cols 是每三個為一組
        cols = st.columns(3)
        
        for i, item in enumerate(display_entries):
                    with cols[i % 3]:
                        with st.container(border=True): 
                            # 1. 優先定義變數，確保變數已存在
                            display_title = item.get('title', '無標題')
                            
                            # 2. 再進行字串切割 (現在 display_title 已經有值了，不會報錯)
                            display_short_title = display_title[:14] + "..." if len(display_title) > 10 else display_title
                            
                            score = item.get('correct', 0) - item.get('wrong', 0)
                            item_level = item.get('level', '未評級')
                            level_badge = f" (Lv.{item_level})" if item_level != '未評級' else ""
                            
                            # 3. 使用剛剛定義好的變數名稱
                            st.markdown(f"**題目: {display_short_title}**{level_badge}")
                            # ... 剩下的程式碼 ...         
                            st.write(f"📊 分數: {score} (✅ {item.get('correct', 0)} / ❌ {item.get('wrong', 0)})")
                        
                            c1, c2, c3, c4 = st.columns([0.2, 0.2, 0.35, 0.2])
                            with c1:
                                if st.button("✅", key=f"tick_{item['id']}"):
                                    item['correct'] = item.get('correct', 0) + 1
                                    save_data(sub_dir, all_entries)
                                    st.rerun()
                            with c2:
                                if st.button("❌", key=f"cross_{item['id']}"):
                                    item['wrong'] = item.get('wrong', 0) + 1
                                    save_data(sub_dir, all_entries)
                                    st.rerun()
                            with c3:
                                if st.button("👁️", key=f"view_{item['id']}"):
                                    st.session_state.viewing_id = item['id']
                                    st.session_state.page = "VIEW"
                                    st.rerun()
                            with c4:
                                with st.popover("🗑️", help="刪除"):
                                    if st.button("確認刪除", key=f"del_{item['id']}"):
                                        all_entries.remove(item)
                                        save_data(sub_dir, all_entries)
                                        st.rerun()
elif st.session_state.page == "WRITE":
    if st.button("⬅️ 返回", key="btn_write_back"): st.session_state.page = "LIST"; st.rerun()

    st.header("錄入新錯題")
    t = st.text_input("名稱")
    
    # 修正這裡：新題目沒有 entry，所以預設值給空列表 []
    new_r = st.multiselect("錯誤原因", get_reasons(sub_dir), default=[], key="write_reasons_multiselect")
    
    with st.popover("✏️ 管理標籤"): render_label_editor(sub_dir)    # --- 新增：上傳圖片與即時預覽 ---
    f = st.file_uploader("上傳圖片", type=["png", "jpg"])
    if f is not None:
        st.image(f, caption="圖片預覽", use_container_width=True)

    if st.button("儲存"):
        p = None    
        if f:
            # 確保圖片存儲路徑
            p = os.path.join(sub_dir, f"{datetime.now().strftime('%Y%m%d%H%M%S')}.png")
            with open(p, "wb") as out: 
                out.write(f.getbuffer())
        
        new_entry = {
            "id": str(datetime.now()), 
            "title": t, 
            "reasons": new_r, 
            "img": p
        }
        all_entries.append(new_entry)
        save_data(sub_dir, all_entries)
        st.session_state.page = "LIST"
        st.rerun()
elif st.session_state.page == "VIEW":
    if st.button("⬅️ 返回"): 
        st.session_state.page = "LIST"
        st.rerun()

    idx = next((i for i, x in enumerate(all_entries) if x['id'] == st.session_state.viewing_id), None)
    if idx is not None:
        entry = all_entries[idx]
        
        # --- 1. 標題與重命名 (切成三欄：標題、Level、重命名) ---
        col1, col2, col3 = st.columns([0.5, 0.25, 0.25])
        
        with col1: 
            st.header(f"檢視: {entry['title']}")
            
        with col2:
            # 建立 Level 下拉選單
            level_options = ["未評級", "1", "2", "3", "4", "5", "5++"]
            current_level = entry.get('level', "未評級")
            
            # 使用 selectbox 讓使用者即時更改難度
# 找到這一段：
# 這是你原本的程式 (第 216-220 行)
            new_level = st.selectbox(
            "設定難度",
            level_options,
            index=level_options.index(current_level)
            )

            # --- 在這裡插入下面這段程式碼 ---
            if new_level != current_level:
                entry['level'] = new_level        # 更新這個題目的資料
                save_data(sub_dir, all_entries)   # 立即存檔！
                st.rerun()                        # 重新載入頁面確保狀態一致
# --------------------------------        with col3:
            # 這裡放你原本的 "✏️ 重命名" popover 邏輯
            with st.popover("✏️ 重命名"):
                new_title = st.text_input("輸入新名稱", value=entry['title'])
                if st.button("確認修改"):
                    # ... (保留你原本的重命名程式碼) ...                    
                    if new_title.strip():
                        custom_names = load_data(sub_dir, "custom_names.json")
                        if not isinstance(custom_names, dict): custom_names = {}
                        custom_names[entry['id']] = new_title.strip()
                        save_data(sub_dir, custom_names, "custom_names.json")
                        all_entries[idx]['title'] = new_title.strip()
                        save_data(sub_dir, all_entries, "data.json")
                        st.success("已重命名！"); 
                        st.rerun()
                    else: 
                        st.error("不能為空")

        # --- 2. 圖片管理 ---
        st.divider()
        st.subheader("🖼️ 錯題image")
        img_path = entry.get('img')
        if img_path and os.path.exists(img_path):
            st.image(img_path, caption="原始圖片", use_container_width=True)
        else:
            # 這裡幫你除錯：印出程式到底去哪個路徑找檔案
            st.warning(f"找不到圖片，檔案路徑: {img_path}")
            st.info("目前無圖片或檔案路徑已損壞")

        u = st.file_uploader("更換錯題image", type=["png", "jpg"], key="img_uploader_view")
        if u is not None:
            st.image(u, caption="圖片預覽", use_container_width=True)
            if st.button("確認更換"):
                if entry.get('img') and os.path.exists(entry['img']): os.remove(entry['img'])
                p = os.path.join(sub_dir, f"{datetime.now().strftime('%Y%m%d%H%M%S')}.png")
                with open(p, "wb") as out: out.write(u.getbuffer())
                all_entries[idx]['img'] = p
                save_data(sub_dir, all_entries); st.success("已更新"); st.rerun()

        # --- 3. 標籤與檢討 ---
        st.divider()
        st.subheader("📝 錯誤檢討與改進")
        
        # 使用唯一 key 解決 DuplicateElementID
        new_r = st.multiselect("錯誤原因", get_reasons(sub_dir), default=entry.get('reasons', []), key="view_multiselect")
        with st.expander("✏️ 管理標籤"): render_label_editor(sub_dir)
        if new_r != entry.get('reasons', []):
            all_entries[idx]['reasons'] = new_r
            save_data(sub_dir, all_entries); st.success("已更新標籤"); st.rerun()
            
        def save_analysis():
            all_entries[idx]['analysis'] = st.session_state.analysis_input
            save_data(sub_dir, all_entries, "data.json")

        st.text_area("如何避免再犯？", value=entry.get('analysis', ""), key="analysis_input", height=150, on_change=save_analysis)

        
            
        # --- 4. 底部返回按鈕 ---
        st.divider()
        if st.button("⬅️ 返回", key="btn_bottom"): 
            st.session_state.page = "LIST"; st.rerun()
