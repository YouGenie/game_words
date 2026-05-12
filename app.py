import streamlit as st
import requests
import time
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")
st.set_page_config(page_title="Игра в слова!", page_icon="🎮")
st.title("🎮 Игра в слова!")

# Показываем счёт
res_score = requests.get(f"{API_URL}/score")
if res_score.status_code == 200:
    score = res_score.json().get('score')
    if score is not None:
        st.subheader(f'Счёт: :green[{score}]')

# Показываем последнее введёное слово
res_last = requests.get(f"{API_URL}/last_word")
if res_last.status_code == 200:
    last = res_last.json().get("word")
    if last:
        st.subheader(f'Последнее слово: :green[{last}]')

# Показываем все слова
response = requests.get(f"{API_URL}/words")
if response.status_code == 200:
    words = response.json().get("words", [])
    with st.expander("Посмотреть слова в игре", expanded=False):
        if words:
            st.info(", ".join(words))
        else:
            st.write("Пока тут пусто.")

# Форма отправки нового слова
with st.form("my_form", clear_on_submit=True):
    new_word = st.text_input("Введите слово")
    submitted = st.form_submit_button("Отправить") 
    if submitted and new_word:
        payload = {"word": new_word, 'player': 'Игрок'}
        res = requests.post(f'{API_URL}/add_word', json=payload)
        if res.status_code == 200:
            st.success(res.json().get('message'))
            time.sleep(2.3)
            st.rerun()

# Удаление всех слов
if st.button("Удалить все слова", type="primary"):
    res = requests.delete(f"{API_URL}/clear_words")
    if res.status_code == 200:
        st.success('Все слова удалены!')
        time.sleep(1)
        st.rerun()

