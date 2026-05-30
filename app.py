import streamlit as st
import os
import json
from datetime import datetime

# --- 1. 設定與 CSS ---
st.set_page_config(page_title="DSE NC", layout="wide")

st.markdown("""
    <style>
    /* 1. 僅保留 Sidebar 的設定 */
    [data-testid="stSidebar"] h2 { font-size: 35px !important; }
    [data-testid="stSidebar"] div[role="radiogroup"] label p { 
        font-size: 20px !important; 
    }
    </style>
    """, unsafe_allow_html=True)
# --- 2. 路徑設定 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_DATA_DIR = os.path.join(BASE_DIR, "subjects")
os.makedirs(MAIN_DATA_DIR, exist_ok=True)

# --- 3. 函數定義 ---
def get_subjects():
    return sorted([d for d in os.listdir(MAIN_DATA_DIR) if os.path.isdir(os.path.join(MAIN_DATA_DIR, d))])

def load_data(sub_path, filename="data.json"):
    f = os.path.join(sub_path, filename)
    return json.load(open(f, 'r', encoding='utf-8')) if os.path.exists(f) else []

def save_data(sub_path, data, filename="data.json"):
    with open(os.path.join(sub_path, filename), 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_reasons(sub_path):
    f = os.path.join(sub_path, "reasons.json")
    return json.load(open(f, 'r', encoding='utf-8')) if os.path.exists(f) else ["概念有錯", "睇錯題目", "計錯數"]

def save_reasons(sub_path, reasons):
    with open(os.path.join(sub_path, "reasons.json"), 'w', encoding='utf-8') as f:
        json.dump(reasons, f, indent=4, ensure_ascii=False)

@st.fragment
def render_label_editor(sub_dir):
    st.subheader("編輯錯誤原因標籤")
    reasons = get_reasons(sub_dir)
    # ... (你的標籤編輯邏輯) ...

# --- 4. 狀態初始化 ---
if 'page' not in st.session_state: st.session_state.page = "LIST"
if 'current_subject' not in st.session_state: 
    subs = get_subjects()
    st.session_state.current_subject = subs[0] if subs else "Default"

# --- 5. 唯一一次的 Sidebar 邏輯 ---
with st.sidebar:
    st.header("科目管理")
    n = st.text_input("新增科目")
    if st.button("新增") and n:
        os.makedirs(os.path.join(MAIN_DATA_DIR, n), exist_ok=True); st.rerun()
    with st.popover("🗑️ 刪除此科目"):
        st.warning("刪除後將無法復原，確定要刪除嗎？")
    
        # 防呆機制：必須點選確認才會執行刪除邏輯
        if st.button("確認刪除", type="primary"):
        # 這裡放入你刪除科目的邏輯 (例如：從 session_state 或資料庫移除)
        # del st.session_state.subjects[current_subject] 
            st.success("科目已刪除")
            st.rerun() # 刪除後立即重新整理頁面
    subs = get_subjects()
    if subs:
        selected_sub = st.radio("切換科目", subs, index=subs.index(st.session_state.current_subject))
        if selected_sub != st.session_state.current_subject:
            st.session_state.current_subject = selected_sub
            st.rerun()

# --- 6. 主頁面邏輯 ---
sub_dir = os.path.join(MAIN_DATA_DIR, st.session_state.current_subject)
os.makedirs(sub_dir, exist_ok=True)
all_entries = load_data(sub_dir)

# -----------------------------
# 1. 列表頁面區塊
if st.session_state.page == "LIST":
    st.header(f"📁 {st.session_state.current_subject}")
    if st.button("➕ 錄入新錯題"): 
        st.session_state.page = "WRITE"
        st.rerun()

    st.write("---")
    # 你的列表迴圈
    for i in range(0, len(all_entries), 4):
        row_items = all_entries[i:i+4]
        cols = st.columns(4)
        for j, col in enumerate(cols):
            if j < len(row_items):
                item = row_items[j]
                with col:
                    with st.expander(f"題目: {item['title']}", expanded=False):
                        if st.button("👁️ 檢視詳情", key=f"view_{item['id']}_{i}_{j}"):
                            st.session_state.viewing_id = item['id']
                            st.session_state.page = "VIEW"
                            st.rerun()
                        with st.popover("🗑️ 刪除此錯題"):
                            st.write("確定要刪除這題嗎？")
                            if st.button("確認刪除", key=f"del_{item['id']}", type="primary"):
                                if item.get('img') and os.path.exists(item['img']):
                                    os.remove(item['img'])
                                all_entries.pop(i + j)
                                save_data(sub_dir, all_entries)
                                st.rerun()

# 2. 錄入頁面區塊
elif st.session_state.page == "WRITE":
    st.header("錄入新錯題")
    t = st.text_input("名稱")
    r = st.multiselect("錯誤原因", get_reasons(sub_dir))
    with st.popover("✏️ 管理標籤"): render_label_editor(sub_dir)
    
    f = st.file_uploader("上傳錯題圖片", type=["png", "jpg"])
    if f is not None:
        st.image(f, caption="圖片預覽", use_container_width=True)
    
    if st.button("儲存"):
        p = None
        if f:
            p = os.path.join(sub_dir, f"{datetime.now().strftime('%Y%m%d%H%M%S')}.png")
            with open(p, "wb") as out: 
                out.write(f.getbuffer())
        
        all_entries.append({"id": str(datetime.now()), "title": t, "reasons": r, "img": p})
        save_data(sub_dir, all_entries)
        st.session_state.page = "LIST"
        st.rerun()

    if st.button("⬅️ 返回"):
        st.session_state.page = "LIST"
        st.rerun()

# 3. 檢視頁面區塊
elif st.session_state.page == "VIEW":
    # 這裡放你的檢視邏輯 (跟之前一樣)
    if st.button("⬅️ 返回"):
        st.session_state.page = "LIST"
        st.rerun()
        
    idx = next((i for i, x in enumerate(all_entries) if x['id'] == st.session_state.viewing_id), None)
    if idx is not None:
        entry = all_entries[idx]

        # --- 1. 標題與重命名 ---
        col1, col2 = st.columns([0.8, 0.2])
        with col1: st.header(f"檢視: {entry['title']}")
        with col2:
            with st.popover("✏️ 重命名"):
                new_title = st.text_input("輸入新名稱", value=entry['title'])
                if st.button("確認修改"):
                    if new_title.strip():
                        custom_names = load_data(sub_dir, "custom_names.json")
                        if not isinstance(custom_names, dict): custom_names = {}
                        custom_names[entry['id']] = new_title.strip()
                        save_data(sub_dir, custom_names, "custom_names.json")
                        all_entries[idx]['title'] = new_title.strip()
                        save_data(sub_dir, all_entries, "data.json")
                        st.success("已重命名")
                        st.rerun()
                    else:
                        st.error("不能為空")

        # --- 2. 圖片管理 ---
        st.divider()
        st.subheader("🖼️ 錯題image")
        if entry.get('img') and os.path.exists(entry['img']):
            st.image(entry['img'], caption="原始圖片", use_container_width=True)
        else: st.info("目前無圖片")

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
