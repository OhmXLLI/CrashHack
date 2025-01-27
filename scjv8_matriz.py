import numpy as np
import pandas as pd
import hmac
import hashlib
import time
import threading
import tkinter as tk
from tkinter import ttk

# Função para calcular o multiplicador a partir do hash
def createCrashMulti(hash):
    result = int(hash[:8], 16)
    finalResult = (4294967296 / (result + 1)) * 0.99
    return finalResult

# Função para calcular o próximo seed a partir do seed atual
def get_next_seed(seed):
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()

# Função para calcular o hash HMAC-SHA256
def compute_hmac(seed, message):
    return hmac.new(bytes(seed, 'utf-8'), message.encode('utf-8'), hashlib.sha256).hexdigest()

# Função principal para criar o histórico de multiplicadores
def createCrashHistoryParallel(crashseed, histlength, batch_size=100_000):
    crashList = []  # Lista para armazenar os multiplicadores
    message = '0000000000000000001b34dc6a1e86083f95500b096231436e9b25cbdd0075c4'

    for batch_start in range(0, histlength, batch_size):
        batch_end = min(batch_start + batch_size, histlength)
        batch_length = batch_end - batch_start

        seeds = [crashseed]
        for _ in range(batch_length - 1):
            seeds.append(get_next_seed(seeds[-1]))  # Calcula os seeds em sequência

        results = [createCrashMulti(compute_hmac(seed, message)) for seed in seeds]

        crashList.extend(results)
        crashseed = get_next_seed(seeds[-1])  # Atualiza o seed para o próximo batch

    return pd.DataFrame({'Multiplier': crashList})

# Função para calcular a média móvel e desvios padrão com ajuste de sensibilidade
def calcular_media_movel(percentuais, janela=300, multiplicador_desvio=1.5):
    media_movel = pd.Series(percentuais).rolling(janela).mean().to_numpy()
    desvio_padrao = pd.Series(percentuais).rolling(janela).std().to_numpy()
    return media_movel, multiplicador_desvio * desvio_padrao

# Função para calcular o RSI (Relative Strength Index)
def calcular_rsi(percentuais, janela=30):
    diffs = np.diff(percentuais)
    ganhos = np.where(diffs > 0, diffs, 0)
    perdas = np.where(diffs < 0, -diffs, 0)

    media_ganhos = pd.Series(ganhos).rolling(janela).mean()
    media_perdas = pd.Series(perdas).rolling(janela).mean()

    rs = media_ganhos / media_perdas
    rsi = 100 - (100 / (1 + rs))
    rsi = rsi.fillna(50).to_numpy()  # Preencher os valores iniciais com 50 (neutro)

    return np.concatenate(([50], rsi))  # Adicionar o primeiro valor neutro

# Função de monitoramento com interface Tkinter
def monitorar_dados_com_interface(df, target, limite_estabilizacao=5000, janela_media=300, multiplicador_desvio=1.5):
    def atualizar_interface():
        nonlocal pausado, velocidade
        # Iniciar com os primeiros 5000 jogos para simular uma estabilização prévia
        ganhos_acumulados = len(df.iloc[:limite_estabilizacao][df['Multiplier'] >= target])
        percentuais = [(ganhos_acumulados / (i + 1)) * 100 for i in range(limite_estabilizacao)]

        media_movel, desvio_padrao = calcular_media_movel(percentuais, janela=janela_media, multiplicador_desvio=multiplicador_desvio)
        rsi = calcular_rsi(percentuais)

        for i, row in df.iloc[limite_estabilizacao:].iterrows():
            if pausado:
                time.sleep(0.1)
                continue

            multiplier = row['Multiplier']
            if multiplier >= target:
                ganhos_acumulados += 1

            percentual_atual = (ganhos_acumulados / (i + 1)) * 100
            percentuais.append(percentual_atual)

            zona = "---"
            if len(percentuais) >= janela_media:
                media_movel, desvio_padrao = calcular_media_movel(percentuais, janela=janela_media, multiplicador_desvio=multiplicador_desvio)
                rsi = calcular_rsi(percentuais)

                if percentual_atual < media_movel[-1] - desvio_padrao[-1]:
                    zona = "ZDB"  # Zona de Baixa
                elif percentual_atual > media_movel[-1] + desvio_padrao[-1]:
                    zona = "ZDA"  # Zona de Alta
                else:
                    zona = "ZDE"  # Zona de Equilíbrio

            label_jogo.config(text=f"{i + 1}", font=("Helvetica", 20))
            label_multiplicador.config(text=f"{multiplier:.2f}", font=("Helvetica", 20))
            label_percentual.config(text=f"{percentual_atual:.2f}%", font=("Helvetica", 20))
            label_media_movel.config(text=f"{media_movel[-1]:.2f}" if len(media_movel) > 0 else "---", font=("Helvetica", 20))
            label_zona.config(text=zona, font=("Helvetica", 20))
            label_rsi.config(text=f"{rsi[-1]:.2f}" if len(rsi) > 0 else "50.00", font=("Helvetica", 20))

            time.sleep(velocidade)

    def pausar_continuar():
        nonlocal pausado
        pausado = not pausado

    def acelerar():
        nonlocal velocidade
        velocidade = max(0.05, velocidade / 2)

    def desacelerar():
        nonlocal velocidade
        velocidade = min(2.0, velocidade * 2)

    # Inicialização de variáveis
    pausado = False
    velocidade = 0.5

    # Configuração da interface
    root = tk.Tk()
    root.title("Monitoramento de Multiplicadores")

    frame = ttk.Frame(root, padding="10")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    ttk.Label(frame, text="Jogo:", font=("Helvetica", 20)).grid(row=0, column=0, sticky=tk.W)
    label_jogo = ttk.Label(frame, text="---", font=("Helvetica", 20))
    label_jogo.grid(row=0, column=1, sticky=tk.W)

    ttk.Label(frame, text="Multiplicador:", font=("Helvetica", 20)).grid(row=1, column=0, sticky=tk.W)
    label_multiplicador = ttk.Label(frame, text="---", font=("Helvetica", 20))
    label_multiplicador.grid(row=1, column=1, sticky=tk.W)

    ttk.Label(frame, text="Percentual:", font=("Helvetica", 20)).grid(row=2, column=0, sticky=tk.W)
    label_percentual = ttk.Label(frame, text="---", font=("Helvetica", 20))
    label_percentual.grid(row=2, column=1, sticky=tk.W)

    ttk.Label(frame, text="Média Móvel:", font=("Helvetica", 20)).grid(row=3, column=0, sticky=tk.W)
    label_media_movel = ttk.Label(frame, text="---", font=("Helvetica", 20))
    label_media_movel.grid(row=3, column=1, sticky=tk.W)

    ttk.Label(frame, text="Zona:", font=("Helvetica", 20)).grid(row=4, column=0, sticky=tk.W)
    label_zona = ttk.Label(frame, text="---", font=("Helvetica", 20))
    label_zona.grid(row=4, column=1, sticky=tk.W)

    ttk.Label(frame, text="RSI:", font=("Helvetica", 20)).grid(row=5, column=0, sticky=tk.W)
    label_rsi = ttk.Label(frame, text="---", font=("Helvetica", 20))
    label_rsi.grid(row=5, column=1, sticky=tk.W)

    ttk.Button(frame, text="Pausar/Continuar", command=pausar_continuar).grid(row=6, column=0)
    ttk.Button(frame, text="Acelerar", command=acelerar).grid(row=6, column=1)
    ttk.Button(frame, text="Desacelerar", command=desacelerar).grid(row=6, column=2)
    ttk.Button(frame, text="Sair", command=root.destroy).grid(row=7, column=1)

    threading.Thread(target=atualizar_interface, daemon=True).start()
    root.mainloop()

# CONFIGURAÇÕES INICIAIS
seed = '0000000000000000001b34dc6a1e86083f95500b096231436e9b25cbdd0075c4'
histlength = 10_000  # Quantidade de multiplicadores
target = 2  # Multiplicador alvo

# GERAÇÃO DO HISTÓRICO
df = createCrashHistoryParallel(seed, histlength)

# Iniciar interface de monitoramento em tempo real
monitorar_dados_com_interface(df, target)
