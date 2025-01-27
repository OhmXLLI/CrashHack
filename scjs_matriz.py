import numpy as np
import pandas as pd
import hmac
import hashlib
from itertools import groupby
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

# Função para calcular o multiplicador a partir do hash
def createCrashMulti(hash):
    result = int(hash[:8], 16)
    finalResult = (4294967296 / (result + 1)) * 0.99
    return finalResult

def get_next_seed(seed):
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()

def compute_hmac(seed, message):
    return hmac.new(bytes(seed, 'utf-8'), message.encode('utf-8'), hashlib.sha256).hexdigest()

def createCrashHistoryParallel(crashseed, histlength, batch_size=100_000):
    crashList = []
    message = '000000000000000000066448f2f56069750fc40c718322766b6bdf63fdcf45b8'

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

def countConsecutiveCrashes(multipliers, target):
    mask = multipliers < target
    max_consecutive = max((sum(1 for _ in group) for val, group in groupby(mask) if val), default=0)
    return max_consecutive

def run_game(seed, histlength, targets, game_num):
    df = createCrashHistoryParallel(seed, histlength)
    results = []
    for target in targets:
        max_crash_streak = countConsecutiveCrashes(df['Multiplier'].to_numpy(), target)
        results.append(f"Jogo {game_num}, Alvo {target}x: Maior sequência abaixo: {max_crash_streak}")
    return results

# CONFIGURAÇÕES
num_jogos = 2  # Quantidade de jogos simultâneos
seed = '0000000000000000001b34dc6a1e86083f95500b096231436e9b25cbdd0075c4'
histlength = 1_000_000  # Quantidade de multiplicadores por jogo
targets = [1.5, 2]  # Múltiplos multiplicadores alvos

# EXECUTANDO JOGOS COM MÚLTIPLOS MULTIPLICADORES
with ThreadPoolExecutor(max_workers=num_jogos) as executor:
    futures = list(tqdm(executor.map(lambda i: run_game(seed, histlength, targets, i), range(1, num_jogos + 1)),
                        total=num_jogos, desc="Executando Jogos", unit="jogo"))

# Exibir os resultados
for game_results in futures:
    for result in game_results:
        print(result)
