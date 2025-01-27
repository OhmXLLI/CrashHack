import numpy as np
import pandas as pd
import hmac
import hashlib
from tqdm import tqdm
import matplotlib.pyplot as plt
from bokeh.plotting import figure, show, output_file
from bokeh.models import HoverTool, Range1d, ColumnDataSource
from bokeh.layouts import column

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

    for batch_start in tqdm(range(0, histlength, batch_size), desc="Gerando Histórico", unit="batch"):
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
def calcular_rsi(percentuais, janela=30):  # Janela ajustada para 30
    diffs = np.diff(percentuais)
    ganhos = np.where(diffs > 0, diffs, 0)
    perdas = np.where(diffs < 0, -diffs, 0)

    media_ganhos = pd.Series(ganhos).rolling(janela).mean()
    media_perdas = pd.Series(perdas).rolling(janela).mean()

    rs = media_ganhos / media_perdas
    rsi = 100 - (100 / (1 + rs))
    rsi = rsi.fillna(50).to_numpy()  # Preencher os valores iniciais com 50 (neutro)

    return np.concatenate(([50], rsi))  # Adicionar o primeiro valor neutro

# Função para análise detalhada com sincronismo e ajuste de gráficos
def analisar_comportamento_detalhado(df, target, intervalo=1, limite_estabilizacao=5000, janela_media=300, multiplicador_desvio=1.5, salvar_relatorio=True):
    total_jogos = len(df)
    ganhos_acumulados = 0
    relatorio_detalhado = []

    for i, multiplier in enumerate(df['Multiplier']):
        if multiplier >= target:
            ganhos_acumulados += 1

        percentual_atual = (ganhos_acumulados / (i + 1)) * 100
        relatorio_detalhado.append((i + 1, multiplier, percentual_atual))

    # Converter dados para análise de oscilação
    jogos, multiplicadores, percentuais = zip(*relatorio_detalhado)

    # Calcular média móvel, desvio padrão e RSI
    media_movel, desvio_padrao = calcular_media_movel(percentuais, janela=janela_media, multiplicador_desvio=multiplicador_desvio)
    rsi = calcular_rsi(percentuais)

    # Definir zonas com base na média móvel e desvios
    zonas = []
    for i, pct in enumerate(percentuais):
        if i < limite_estabilizacao or np.isnan(media_movel[i]):
            zonas.append("---")  # Sem análise antes da estabilização ou sem média
        elif pct < media_movel[i] - desvio_padrao[i]:
            zonas.append("ZDB")  # Zona de Baixa
        elif pct > media_movel[i] + desvio_padrao[i]:
            zonas.append("ZDA")  # Zona de Alta
        else:
            zonas.append("ZDE")  # Zona de Equilíbrio

    # Salvar relatório detalhado em arquivo com as zonas e RSI
    if salvar_relatorio:
        with open("relatorio_detalhado_multiplicadores.txt", "w") as file:
            file.write(f"{'Jogo':<10}{'Multiplicador':<15}{'Percentual (%)':<15}{'Zona':<10}{'RSI':<10}\n")
            file.write("=" * 60 + "\n")
            for jogo, mult, pct, zona, rsi_val in zip(jogos, multiplicadores, percentuais, zonas, rsi):
                file.write(f"{jogo:<10}{mult:<15.2f}{pct:<15.2f}{zona:<10}{rsi_val:<10.2f}\n")
        print("\nRelatório detalhado salvo em 'relatorio_detalhado_multiplicadores.txt'.")

    # Gerar gráficos interativos com Bokeh
    output_file("grafico_interativo_multiplicadores_com_rsi.html")

    # Gráfico de percentuais com médias móveis e zonas
    source1 = ColumnDataSource(data=dict(jogos=jogos, percentuais=percentuais, media_movel=media_movel, desvio_inferior=media_movel - desvio_padrao, desvio_superior=media_movel + desvio_padrao))
    source2 = ColumnDataSource(data=dict(jogos=jogos, rsi=rsi))

    p1 = figure(title="Comportamento Detalhado com Média Móvel e Zonas", x_axis_label="Número de Jogos", y_axis_label="Percentual (%)", width=1400, height=500, tools="pan,wheel_zoom,box_zoom,reset,save")
    p1.line('jogos', 'percentuais', source=source1, legend_label=f"Percentual de ganhos (>= {target}x)", line_color="blue", alpha=0.5)
    p1.line('jogos', 'media_movel', source=source1, legend_label="Média Móvel", line_color="orange", line_width=2)
    p1.varea(x='jogos', y1='desvio_inferior', y2='desvio_superior', source=source1, fill_color="orange", fill_alpha=0.2, legend_label="Desvio Padrão")
    p1.line('jogos', [49.5] * len(jogos), legend_label="Percentual teórico (49,5%)", line_dash="dashed", line_color="red")
    p1.legend.title = "Legenda"
    p1.legend.label_text_font_size = "10pt"
    p1.legend.location = "top_left"
    p1.legend.click_policy = "hide"
    p1.grid.grid_line_alpha = 0.3

    # Gráfico de RSI
    p2 = figure(title="RSI (Índice de Força Relativa)", x_axis_label="Número de Jogos", y_axis_label="RSI", width=1400, height=300, tools="pan,wheel_zoom,box_zoom,reset,save")
    p2.line('jogos', 'rsi', source=source2, line_color="green", legend_label="RSI", line_width=1.5)
    p2.y_range = Range1d(0, 100)
    p2.line(jogos, [65] * len(jogos), line_dash="dashed", line_color="red", legend_label="Zona de Sobrecompra (65)")
    p2.line(jogos, [35] * len(jogos), line_dash="dashed", line_color="blue", legend_label="Zona de Sobrevenda (35)")
    p2.legend.title = "RSI"
    p2.legend.label_text_font_size = "10pt"
    p2.legend.location = "top_left"
    p2.legend.click_policy = "hide"
    p2.grid.grid_line_alpha = 0.3

    hover_tool_p1 = HoverTool(tooltips=[("Jogo", "@jogos"), ("Percentual", "@percentuais{0.2f}%"), ("Média Móvel", "@media_movel{0.2f}"), ("Desvio Superior", "@desvio_superior{0.2f}"), ("Desvio Inferior", "@desvio_inferior{0.2f}")])
    hover_tool_p2 = HoverTool(tooltips=[("Jogo", "@jogos"), ("RSI", "@rsi{0.2f}")])

    p1.add_tools(hover_tool_p1)
    p2.add_tools(hover_tool_p2)

    layout_final = column(p1, p2)
    show(layout_final)

# CONFIGURAÇÕES INICIAIS
seed = '0000000000000000001b34dc6a1e86083f95500b096231436e9b25cbdd0075c4'
histlength = 5_000  # Quantidade de multiplicadores
target = 2  # Multiplicador alvo

# GERAÇÃO DO HISTÓRICO
df = createCrashHistoryParallel(seed, histlength)

# Análise detalhada com as mudanças
analisar_comportamento_detalhado(df, target)
