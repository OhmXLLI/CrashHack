from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_cors import CORS
import hashlib
import hmac
import pandas as pd
import threading
import time

# Inicialização do Flask e SocketIO
app = Flask(__name__)
CORS(app, origins=["http://127.0.0.1:5500"])  # Permitir conexões apenas do frontend
socketio = SocketIO(app, cors_allowed_origins=["http://127.0.0.1:5500"])

# Variáveis globais e parâmetros configuráveis
frontend_connected = False
is_paused = False
speed = 1.0
target = 2.0
janela_media = 300
multiplicador_desvio = 1.5
janela_rsi = 30
limite_estabilizacao = 5000  # Quantidade de jogos para estabilização inicial

# Histórico de dados para navegação
historico_dados = []

# Funções para cálculo de multiplicadores
def createCrashMulti(hash):
    result = int(hash[:8], 16)
    return (4294967296 / (result + 1)) * 0.99

def get_next_seed(seed):
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()

def compute_hmac(seed, message):
    return hmac.new(seed.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).hexdigest()

def createCrashHistoryParallel(crashseed, histlength, batch_size=100_000):
    crashList = []
    message = '0000000000000000001b34dc6a1e86083f95500b096231436e9b25cbdd0075c4'

    for batch_start in range(0, histlength, batch_size):
        batch_end = min(batch_start + batch_size, histlength)
        batch_length = batch_end - batch_start

        seeds = [crashseed]
        for _ in range(batch_length - 1):
            seeds.append(get_next_seed(seeds[-1]))

        results = [createCrashMulti(compute_hmac(seed, message)) for seed in seeds]
        crashList.extend(results)
        crashseed = get_next_seed(seeds[-1])

    return pd.DataFrame({'Multiplier': crashList})

# Funções de cálculo estatístico
def calcular_media_movel(percentuais, janela, multiplicador_desvio):
    media_movel = pd.Series(percentuais).rolling(janela).mean().to_numpy()
    desvio_padrao = pd.Series(percentuais).rolling(janela).std().to_numpy()
    return media_movel, multiplicador_desvio * desvio_padrao

def calcular_rsi(percentuais, janela):
    diffs = pd.Series(percentuais).diff().to_numpy()
    ganhos = [x if x > 0 else 0 for x in diffs]
    perdas = [-x if x < 0 else 0 for x in diffs]
    media_ganhos = pd.Series(ganhos).rolling(janela).mean().to_numpy()
    media_perdas = pd.Series(perdas).rolling(janela).mean().to_numpy()

    rs = media_ganhos / media_perdas
    rsi = 100 - (100 / (1 + rs))
    rsi = pd.Series(rsi).fillna(50).to_numpy()
    return rsi

def calcular_maior_perda_consecutiva(percentuais, janela):
    perdas_consecutivas = 0
    maior_perda = 0
    for i in range(-janela, 0):
        if i < -len(percentuais):
            break
        if percentuais[i] < percentuais[i - 1]:  # Indica uma perda
            perdas_consecutivas += 1
        else:
            maior_perda = max(maior_perda, perdas_consecutivas)
            perdas_consecutivas = 0
    maior_perda = max(maior_perda, perdas_consecutivas)
    return maior_perda

def calcular_maior_ganho_consecutivo(percentuais, janela):
    ganhos_consecutivos = 0
    maior_ganho = 0
    for i in range(-janela, 0):
        if i < -len(percentuais):
            break
        if percentuais[i] > percentuais[i - 1]:  # Indica um ganho
            ganhos_consecutivos += 1
        else:
            maior_ganho = max(maior_ganho, ganhos_consecutivos)
            ganhos_consecutivos = 0
    maior_ganho = max(maior_ganho, ganhos_consecutivos)
    return maior_ganho

# Evento de conexão e desconexão
@socketio.on('connect')
def handle_connect():
    global frontend_connected
    frontend_connected = True
    print("Frontend conectado.")
    socketio.emit('status', {'message': 'Conexão estabelecida com o backend.'})

@socketio.on('disconnect')
def handle_disconnect():
    global frontend_connected
    frontend_connected = False
    print("Frontend desconectado.")
    socketio.emit('status', {'message': 'Conexão perdida com o backend.'})

# Controle de comandos recebidos do frontend
@socketio.on('command')
def handle_command(data):
    global is_paused, speed, target
    command = data.get('command')

    if command == 'pause':
        is_paused = True
        socketio.emit('status', {'message': 'Sistema pausado.'})
    elif command == 'resume':
        is_paused = False
        socketio.emit('status', {'message': 'Sistema retomado.'})
    elif command == 'accelerate':
        speed = min(speed * 1.5, 5.0)
        socketio.emit('status', {'message': f'Velocidade aumentada para {speed:.1f}x.'})
    elif command == 'decelerate':
        speed = max(speed / 1.5, 0.1)
        socketio.emit('status', {'message': f'Velocidade reduzida para {speed:.1f}x.'})
    elif command == 'update_target':
        target = float(data.get('value', target))
        socketio.emit('status', {'message': f'Target atualizado para {target:.2f}x.'})

# Simulador de dados
def simulador_dados():
    global is_paused, speed, target

    # Gerar histórico inicial
    seed = "0000000000000000001b34dc6a1e86083f95500b096231436e9b25cbdd0075c4"
    df = createCrashHistoryParallel(seed, limite_estabilizacao)
    percentuais = []
    ganhos_acumulados = 0

    for i, multiplier in enumerate(df['Multiplier']):
        if multiplier >= target:
            ganhos_acumulados += 1
        percentual_atual = (ganhos_acumulados / (i + 1)) * 100
        percentuais.append(percentual_atual)

    media_movel, desvio_padrao = calcular_media_movel(percentuais, janela_media, multiplicador_desvio)
    rsi = calcular_rsi(percentuais, janela_rsi)

    # Loop para simulação em tempo real
    while True:
        if not frontend_connected:
            time.sleep(1)
            continue

        while is_paused:
            time.sleep(0.1)

        multiplier = df['Multiplier'][len(percentuais) % len(df)]
        ganhos_acumulados += 1 if multiplier >= target else 0
        percentual_atual = (ganhos_acumulados / len(percentuais)) * 100
        percentuais.append(percentual_atual)

        media_movel, desvio_padrao = calcular_media_movel(percentuais, janela_media, multiplicador_desvio)
        rsi = calcular_rsi(percentuais, janela_rsi)

        zona = "---"
        if percentual_atual < media_movel[-1] - desvio_padrao[-1]:
            zona = "ZDB"
        elif percentual_atual > media_movel[-1] + desvio_padrao[-1]:
            zona = "ZDA"
        else:
            zona = "ZDE"

        maior_perda = calcular_maior_perda_consecutiva(percentuais, janela_media)
        maior_ganho = calcular_maior_ganho_consecutivo(percentuais, janela_media)

        dado_atual = {
            'jogo': len(percentuais),
            'multiplicador': round(multiplier, 2),
            'percentual': round(percentual_atual, 2),
            'media_movel': round(media_movel[-1], 2) if len(media_movel) > 0 else "---",
            'zona': zona,
            'rsi': round(rsi[-1], 2) if len(rsi) > 0 else 50.00,
            'maior_perda': maior_perda,
            'maior_ganho': maior_ganho,
            'time': int(time.time() * 1000),
        }

        historico_dados.append(dado_atual)

        socketio.emit('atualizacao', dado_atual)
        time.sleep(1 / speed)

# Rota principal
@app.route('/')
def index():
    return render_template('index.html')

# Iniciar o simulador em uma thread separada
threading.Thread(target=simulador_dados, daemon=True).start()

# Rodar o servidor
if __name__ == '__main__':
    socketio.run(app, debug=True)