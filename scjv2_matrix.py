import numpy as np
import pandas as pd
import hmac
import hashlib
from itertools import groupby
from tqdm import tqdm
from datetime import datetime
import os

# Nome do arquivo que guarda a contagem
counter_file = "file_counter.txt"

# Função para carregar o contador de arquivo
def load_file_counter():
    if os.path.exists(counter_file):
        with open(counter_file, 'r') as f:
            return int(f.read().strip())
    return 1  # Se o arquivo não existir, começa com 1

# Função para salvar o contador de arquivo
def save_file_counter(counter):
    with open(counter_file, 'w') as f:
        f.write(str(counter))

# Função para resetar o contador manualmente
def reset_file_counter():
    save_file_counter(1)
    print("Contador de arquivos resetado para 1.")

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

# Função principal para criar o histórico de multiplicadores com barra de progresso
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

# Função para contar todas as sequências de multiplicadores abaixo de um alvo
def countConsecutiveCrashes(multipliers, target):
    mask = multipliers < target
    sequences = [(sum(1 for _ in group)) for val, group in groupby(mask) if val]
    
    count_dict = {}
    for seq in sequences:
        count_dict[seq] = count_dict.get(seq, 0) + 1

    max_sequence = max(sequences, default=0)
    max_occurrences = count_dict.get(max_sequence, 0)
    
    position_max = None
    for i, length in enumerate(sequences):
        if length == max_sequence:
            position_max = i
            break

    return count_dict, max_sequence, max_occurrences, position_max

# Função para salvar as informações em um arquivo .txt
def save_report_to_file(target, histlength, count_dict, max_sequence, max_occurrences, position_max, multipliers):
    # Carrega o contador atual
    file_counter = load_file_counter()

    # Formatação de data: dd-mm-aa
    current_date = datetime.now().strftime("%d-%m-%y")

    # Nome do arquivo com o contador antes da data
    filename = f"[{file_counter}] {current_date}.txt"
    
    # Incrementa o contador e salva
    file_counter += 1
    save_file_counter(file_counter)

    total_sequences = sum(count_dict.values())
    total_multipliers = len(multipliers)

    with open(filename, 'w') as f:
        f.write(f"Relatório de Análise de Multiplicadores\n")
        f.write(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Multiplicador alvo: {target}x\n")
        f.write(f"Total de multiplicadores analisados: {histlength}\n\n")

        f.write(f"Maior sequência de perdas consecutivas abaixo de {target}x: {max_sequence} (apareceu {max_occurrences} vezes)\n")
        if position_max is not None:
            f.write(f"Momento da maior perda: Jogo número {position_max + 1}, multiplicador: {multipliers[position_max]:.2f}x\n\n")

        f.write(f"Outras sequências de perdas:\n")
        for seq_length, count in sorted(count_dict.items()):
            percentage = (count / total_sequences) * 100
            f.write(f"- Sequência de {seq_length} perdas: {count} vezes ({percentage:.2f}% do total)\n")

    print(f"Relatório salvo em {filename}")

# CONFIGURAÇÕES INICIAIS
seed = '0000000000000000001b34dc6a1e86083f95500b096231436e9b25cbdd0075c4'
histlength = 1_000_000  # Quantidade de multiplicadores
target = 2  # Multiplicador alvo

# Instrução de como resetar o contador:
# Basta apagar o file_counter que ele reseta. 

# GERAÇÃO DO HISTÓRICO
print(f"Gerando histórico com {histlength} multiplicadores usando a seed {seed}.")
df = createCrashHistoryParallel(seed, histlength)

# CÁLCULO DAS SEQUÊNCIAS DE PERDAS
multipliers = df['Multiplier'].to_numpy()
count_dict, max_sequence, max_occurrences, position_max = countConsecutiveCrashes(multipliers, target)

# EXIBIÇÃO DOS RESULTADOS
print(f"Maior sequência consecutiva de multiplicadores abaixo de {target}x: {max_sequence} (apareceu {max_occurrences} vezes)")
if position_max is not None:
    print(f"Momento da maior perda: Jogo número {position_max + 1}, multiplicador: {multipliers[position_max]:.2f}x")

print(f"Outras sequências de perdas:")
for seq_length, count in sorted(count_dict.items()):
    percentage = (count / sum(count_dict.values())) * 100
    print(f"- Sequência de {seq_length} perdas: {count} vezes ({percentage:.2f}% do total)")

# SALVA O RELATÓRIO EM ARQUIVO TXT
save_report_to_file(target, histlength, count_dict, max_sequence, max_occurrences, position_max, multipliers)
