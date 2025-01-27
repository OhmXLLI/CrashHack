import numpy as np
import pandas as pd
import hmac
import hashlib
from itertools import groupby
from tqdm import tqdm

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
    message = '000000000000000000066448f2f56069750fc40c718322766b6bdf63fdcf45b8'

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

# Função para contar a maior sequência de multiplicadores abaixo de um alvo
def countConsecutiveCrashes(multipliers, target):
    mask = multipliers < target
    max_consecutive = max((sum(1 for _ in group) for val, group in groupby(mask) if val), default=0)
    return max_consecutive

# CONFIGURAÇÕES INICIAIS
seed = '0000000000000000001b34dc6a1e86083f95500b096231436e9b25cbdd0075c4'
histlength = 100_000  # Quantidade de multiplicadores
target = 1.5  # Multiplicador alvo

# GERAÇÃO DO HISTÓRICO
print(f"Gerando histórico com {histlength} multiplicadores usando a seed {seed}.")
df = createCrashHistoryParallel(seed, histlength)

# CÁLCULO DA MAIOR SEQUÊNCIA ABAIXO DO ALVO
max_crash_streak = countConsecutiveCrashes(df['Multiplier'].to_numpy(), target)
print(f"Maior sequência consecutiva de multiplicadores abaixo de {target}x: {max_crash_streak}")
