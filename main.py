from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from llama_cpp import Llama
from huggingface_hub import hf_hub_download
from typing import cast
import database as db
import os
import re

app = FastAPI()

# Чтобы фронтенд с бэкендом хорошо дружил (обязательная вещь)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

db.init_db()

MODEL_DIR = "models"
MODEL_FILE = "Llama-3.3-8B-Instruct-128K.Q4_K_M.gguf"
MODEL_PATH = os.path.join(MODEL_DIR, MODEL_FILE)

if not os.path.exists(MODEL_PATH):
    print(f"Модель не найдена в '{MODEL_PATH}'. Начинается автоматическое скачивание...")
    hf_hub_download(
        repo_id="mradermacher/Llama-3.3-8B-Instruct-128K-GGUF",
        filename=MODEL_FILE,
        local_dir=MODEL_DIR
    )
    print("Скачивание завершено!")
else:
    print(f"Модель уже существует по адресу: {MODEL_PATH}")

llm = Llama(
    model_path=MODEL_PATH, 
    n_ctx=1024,
    #n_gpu_layers=-1,     # все слои на GPU 
    n_threads=8, 
    verbose=False,
    stream=False
)

# Модель данных для того, что присылает игрок
class WordRequest(BaseModel):
    word: str
    player: str

# --------------------------------------------------------------------

@app.get('/score')
def get_score():
    return {"score": db.get_word_count() // 2}

@app.get('/last_word')
def last_word():
    return {"word": db.get_last_word()}

@app.get('/words')
def get_words():
    return {"words": db.get_all_words()}

def get_ai_word(last_letter: str, used_words: list) -> str:
    prompt = (
        f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n"
        f"Ты играешь в игру в слова на русском языке. Твоя задача - написать ровно ОДНО СУЩЕСТВИТЕЛЬНОЕ "
        f"в единственном числе, которое начинается на букву, указанную пользователем. "
        f"ЗАПРЕЩЕНО писать любые приветствия, комментарии, пояснения, точки и знаки препинания. Необходимо написать только одно слово.<|eot_id|>"
        f"<|start_header_id|>user<|end_header_id|>\n\n"
        f"Напиши только одно слово на букву '{last_letter.upper()}'.\n"
        f"Список уже использованных слов (их использовать НЕЛЬЗЯ): {', '.join(used_words)}.<|eot_id|>"
        f"<|start_header_id|>assistant<|end_header_id|>\n"
    )  
    response = llm(prompt, max_tokens=10, temperature=0.5)
    response_dict = cast(dict, response)
    ai_word = re.sub(r'[^а-яё-]', '', response_dict["choices"][0]["text"].strip().lower())
    return ai_word

@app.post("/add_word")
def add_word(data: WordRequest):
    db.save_word(data.word, data.player)
    word_cleaned = data.word.strip().lower()
    last_letter = word_cleaned[-1]
    if last_letter in ["ь", "ы", "ъ", "ё"] and len(word_cleaned) > 1:
        last_letter = word_cleaned[-2]

    used_words = db.get_all_words()
    ai_word = get_ai_word(last_letter, used_words)
    
    max_attempts = 5
    attempt = 0
    while (ai_word in used_words or not ai_word or len(ai_word) >= 15) and attempt < max_attempts:
        attempt += 1
        retry_prompt = (
            f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n"
            f"Ты играешь в игру в слова на русском языке. Твоя задача - написать ровно ОДНО короткое СУЩЕСТВИТЕЛЬНОЕ "
            f"в единственном числе, которое начинается на букву '{last_letter.upper()}'. "
            f"Оно должно быть строго КОРОЧЕ 15 БУКВ и его НЕ должно быть в списке: {', '.join(used_words)}.<|eot_id|>"
            f"<|start_header_id|>user<|end_header_id|>\n\n"
            f"Напиши другое слово.<|eot_id|>"
            f"<|start_header_id|>assistant<|end_header_id|>\n"
        )
        response = llm(retry_prompt, max_tokens=10, temperature=0.8, stream=False)
        ai_word = re.sub(r'[^а-яё-]', '', response["choices"][0]["text"].strip().lower())  # type: ignore
    db.save_word(ai_word, "AI (Llama)")
    return {
        "status": "success", 
        "message": f"Вы добавили '{data.word}'.  \nИИ ответил: '{ai_word}'"
    }

@app.delete('/clear_words')
def clear_words():
    db.clear_db()
    return {"status": "success", "message": "История слов очищена"}


#  команда для запуска сервера
#  uvicorn main:app --reload

