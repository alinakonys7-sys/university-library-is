import os
import requests
import streamlit as st

BASE_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")
st.set_page_config(page_title="Университет кітапханасы", page_icon="📚", layout="wide")
st.title("📚 Университеттің электрондық кітапханасы")
st.sidebar.header("Жоба туралы")
st.sidebar.write("FastAPI + SQLite + Streamlit. Лабораториялық жұмыстар №1–7")

def api(method, path, **kwargs):
    try:
        response = requests.request(method, f"{BASE_URL}{path}", timeout=10, **kwargs)
        if response.status_code >= 400:
            try:
                detail = response.json().get("detail", response.text)
            except ValueError:
                detail = response.text
            st.error(f"Сервер қатесі {response.status_code}: {detail}")
            return None
        return response.json() if response.content else True
    except requests.RequestException as exc:
        st.error(f"Серверге қосылу мүмкін емес: {exc}")
        return None

categories = api("GET", "/categories")
authors = api("GET", "/authors")
if categories is None or authors is None:
    st.stop()
category_names = {c["id"]: c["name"] for c in categories}
author_names = {a["id"]: a["full_name"] for a in authors}

st.subheader("Кітаптар каталогы")
col1, col2, col3 = st.columns(3)
with col1:
    search = st.text_input("Кітап атауы бойынша іздеу", placeholder="Python")
with col2:
    selected_category = st.selectbox("Категория", [None] + list(category_names), format_func=lambda x: "Барлығы" if x is None else category_names[x])
with col3:
    min_year = st.number_input("Шыққан жылы (бастап)", min_value=1450, max_value=2100, value=1450)
params = {"search": search, "min_year": int(min_year)}
if selected_category is not None:
    params["category_id"] = selected_category
books = api("GET", "/books", params=params)
if books is not None:
    rows = [{"ID": b["id"], "Кітап": b["title"], "Жылы": b["publication_year"], "Дана": b["copies"], "Категория": category_names.get(b["category_id"], "—"), "Автор": author_names.get(b["author_id"], "—")} for b in books]
    st.dataframe(rows, use_container_width=True, hide_index=True)
    st.caption(f"Табылған кітаптар саны: {len(rows)}")

st.subheader("Жаңа кітап қосу")
with st.form("add_book", clear_on_submit=True):
    title = st.text_input("Кітап атауы")
    year = st.number_input("Шыққан жылы", min_value=1450, max_value=2100, value=2024)
    copies = st.number_input("Дана саны", min_value=0, value=1)
    cat = st.selectbox("Категория", list(category_names), format_func=lambda x: category_names[x])
    author = st.selectbox("Автор", list(author_names), format_func=lambda x: author_names[x])
    add = st.form_submit_button("Кітапты сақтау", type="primary")
if add:
    if not title.strip():
        st.warning("Кітап атауын енгізіңіз")
    elif api("POST", "/books", json={"title": title.strip(), "publication_year": int(year), "copies": int(copies), "category_id": cat, "author_id": author}) is not None:
        st.success("Кітап қосылды")
        st.rerun()

st.subheader("Кітапты өзгерту")
with st.form("edit_book"):
    edit_id = st.number_input("Өзгертілетін кітап ID", min_value=1, step=1, key="edit_id")
    new_copies = st.number_input("Жаңа дана саны", min_value=0, step=1)
    edit = st.form_submit_button("Дана санын өзгерту")
if edit and api("PATCH", f"/books/{int(edit_id)}", json={"copies": int(new_copies)}) is not None:
    st.success("Мәлімет жаңартылды")
    st.rerun()

st.subheader("Кітапты жою")
with st.form("delete_book"):
    delete_id = st.number_input("Жойылатын кітап ID", min_value=1, step=1)
    confirm = st.checkbox("Осы кітапты біржола жоюды растаймын")
    delete = st.form_submit_button("Кітапты жою")
if delete:
    if not confirm:
        st.warning("Алдымен жоюды растаңыз")
    elif api("DELETE", f"/books/{int(delete_id)}") is not None:
        st.success("Кітап жойылды")
        st.rerun()
