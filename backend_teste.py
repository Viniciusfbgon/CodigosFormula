from flask import Flask, jsonify, render_template
import sqlite3
import requests
import threading
import time

app = Flask(_name_)


ESP_URL = "http://172.20.10.13/dados"

# =====================================
# BANCO SQLITE
# =====================================
conn = sqlite3.connect(
    'dados.db',
    check_same_thread=False
)

cursor = conn.cursor()

# =====================================
# TABELA
# =====================================
cursor.execute('''
CREATE TABLE IF NOT EXISTS dados_teste (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    tensao REAL,

    corrente REAL,

    potencia REAL,

    pwm INTEGER
)
''')

conn.commit()

# =====================================
# FUNÇÃO QUE LÊ O ESP32
# =====================================
def ler_esp():

    while True:

        try:

            # Faz requisição GET no ESP32
            resposta = requests.get(ESP_URL)

            # Converte JSON
            dados = resposta.json()

            # Extrai valores
            tensao = dados["tensao"]

            corrente = dados["corrente"]

            potencia = dados["potencia"]

            pwm = dados["pwm"]

            # Salva no banco
            cursor.execute(
                """
                INSERT INTO dados_teste
                (tensao, corrente, potencia, pwm)

                VALUES (?, ?, ?, ?)
                """,

                (
                    tensao,
                    corrente,
                    potencia,
                    pwm
                )
            )

            conn.commit()

            print("Dados salvos!")

        except Exception as erro:

            print("Erro:", erro)

        # Espera 2 segundos
        time.sleep(2)

# =====================================
# DASHBOARD
# =====================================
@app.route('/')
def dashboard():

    return render_template("index.html")

# =====================================
# ENVIA DADOS PARA O FRONTEND
# =====================================
@app.route('/dados')
def enviar_dados_dashboard():

    cursor.execute(
        """
        SELECT *
        FROM dados_teste
        ORDER BY id DESC
        LIMIT 20
        """
    )

    linhas = cursor.fetchall()

    lista = []

    for l in reversed(linhas):

        lista.append({

            "tensao": l[1],

            "corrente": l[2],

            "potencia": l[3],

            "pwm": l[4]
        })

    return jsonify(lista)

# =====================================
# TABELA HTML
# =====================================
@app.route('/tabela')
def tabela():

    cursor.execute(
        """
        SELECT *
        FROM dados_teste
        ORDER BY id DESC
        LIMIT 20
        """
    )

    dados = cursor.fetchall()

    return render_template(
        "tabela.html",
        dados=dados
    )

# =====================================
# THREAD PARA LER ESP32
# =====================================
threading.Thread(
    target=ler_esp,
    daemon=True
).start()

# =====================================
# RODA SERVIDOR
# =====================================
app.run(debug=True)