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

def get_reasons(sub_path):
    f = os.path.join(sub_path, "reasons.json")
    return json.load(open(f, 'r', encoding='utf-8')) if os.path.exists(f) else ["概念有錯", "睇錯題目", "計錯數"]

def save_reasons(sub_path, reasons):
    with open(os.path.join(sub_path, "reasons.json"), 'w', encoding='utf-8') as f:
        json.dump(reasons, f, indent=4, ensure_ascii=False)
# --- 3. 新版標籤編輯函數 (只定義一次) ---
@st.fragment
def render_label_editor(sub_dir):
    st.subheader("編輯錯誤原因標籤")
    reasons = get_reasons(sub_dir)
    with st.expander("➕ 新增標籤"):
        new = st.text_input("輸入新標籤名稱", key="new_label_entry")
        if st.button("確認新增"):
            if not new.strip(): st.error("不能為空")
            elif new.strip() in reasons: st.warning("已存在")
            else:
                reasons.append(new.strip()); save_reasons(sub_dir, reasons); st.rerun()
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
            save_reasons(sub_dir, final_list); st.success("標籤已更新！"); st.rerun()

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
        st.session_state.current_subject = st.radio("切換科目", subs, index=subs.index(st.session_state.current_subject))

sub_dir = os.path.join(MAIN_DATA_DIR, st.session_state.current_subject)
os.makedirs(sub_dir, exist_ok=True)
all_entries = load_data(sub_dir)
# 讀取你的「長期名稱記憶庫」
custom_names = load_data(sub_dir, "custom_names.json")
for item in all_entries:
    if item['id'] in custom_names:
        item['title'] = custom_names[item['id']] # 把新名字貼上去
# -----------------------------

if st.session_state.page == "LIST":
    st.header(f"📁 {st.session_state.current_subject} 題目列表")
    
    if st.button("+ 錄入新錯題"):
        st.session_state.page = "WRITE"
        st.rerun()
        
    all_reasons = get_reasons(sub_dir)
    filter_labels = st.multiselect("🔍 篩選錯題 (標籤)", options=all_reasons)

    if filter_labels:
        # 使用列表推導式進行嚴格的 AND 篩選
        display_entries = [
            item for item in all_entries 
            if all(label in item.get('reasons', []) for label in filter_labels)
        ]
    else:
        display_entries = all_entries

    st.write("---")
    
    # 使用 3 欄進行排列
    cols = st.columns(4)
    
    for i, item in enumerate(display_entries):
        with cols[i % 4]:
            # 不使用 height=150，改用 border=True，這在任何版本都能運作
            with st.container(border=True):
                display_title = item['title'] if len(item['title']) < 12 else item['title'][:10] + "..."
                st.markdown(f"**題目: {display_title}**")
            
                c1, c2 = st.columns([0.8, 0.2])
                with c1:
                    if st.button("查看", key=f"view_{item['id']}"):
                        st.session_state.viewing_id = item['id']
                        st.session_state.page = "VIEW"
                        st.rerun()
                with c2:
                # 呢度用 popover，入面放刪除按鈕
                    with st.popover("🗑️"):
                        st.write("確定要刪除這道題目嗎？")
                    # 當 user 喺 popover 入面按「確認刪除」時先執行刪除
                        if st.button("確認刪除", key=f"del_{item['id']}"):
                            if item.get('img') and os.path.exists(item['img']):
                                os.remove(item['img'])
                            if item in all_entries:
                                all_entries.remove(item)
                            save_data(sub_dir, all_entries)
                            st.rerun()
elif st.session_state.page == "WRITE":
    if st.button("⬅️ 返回", key="btn_write_back"): st.session_state.page = "LIST"; st.rerun()
    
    st.header("錄入新錯題")
    t = st.text_input("名稱")
    r = st.multiselect("錯誤原因", get_reasons(sub_dir))
    with st.popover("✏️ 管理標籤"): render_label_editor(sub_dir)
    
    # --- 新增：上傳圖片與即時預覽 ---
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
        
        # 儲存資料
        all_entries.append({"id": str(datetime.now()), "title": t, "reasons": r, "img": p})
        save_data(sub_dir, all_entries)
        st.session_state.page = "LIST"
        st.rerun()

elif st.session_state.page == "VIEW":
    if st.button("⬅️ 返回"): st.session_state.page = "LIST"; st.rerun()
    
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
                        st.success("已重命名！"); st.rerun()
                    else: st.error("不能為空")

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