
* * * * *

# CrashHack: Explorando o Limbo da Aleatoriedade
==============================================

> "A sorte favorece os preparados. Mas será que ela consegue vencer as estatísticas?"

* * * * *

## 📜 Introdução
-------------

Bem-vindo ao **CrashHack**, um projeto que explora a justiça (ou falta dela) nos multiplicadores do jogo **Crash** e **Limbo**.\
Aqui você encontrará ferramentas para analisar probabilidades, visualizar métricas avançadas, e, quem sabe, criar\
uma estratégia para ganhar (sem ser consumido pela ganância, claro).

**Objetivo:**\
Analisar e testar estatísticas de multiplicadores, entendendo padrões e simulando cenários, com foco no aprendizado técnico.

* * * * *

## 📑 Tabela de Conteúdos
----------------------

1. [Minha Jornada no CrashHack](#minha-jornada-no-crashhack)
2. [Bônus e Ferramentas Interativas](#bônus-e-ferramentas-interativas)
3. [Scripts Disponíveis](#scripts-disponíveis)
4. [Como Rodar o Projeto](#como-rodar-o-projeto)
5. [Desafio para Desenvolvedores](#desafio-para-desenvolvedores)
6. [Licença](#licença)


* * * * *

## 🧭 Minha Jornada no CrashHack
-----------------------------

> "Ganhar é uma coisa. Manter é outra."

Tudo começou no dia **24/01/2025**, com uma ideia: testar se era possível dobrar um capital inicial com base nas estatísticas\
do jogo. Entre análises e brincadeiras, nasceu o **catalogador no console**, que gerenciava entradas e perdas consecutivas.

**Resumo da Experiência:**

-   Comecei com **R$16 em Litecoin** e, após dois dias, cheguei a **R$34**.
-   A estratégia baseava-se na **estatística de perdas consecutivas**, ajustando as apostas com segurança.

**Estatísticas Relevantes:**\
(Testadas em uma cadeia de 60 milhões de jogos)

-   Sequência de 5 perdas consecutivas: **0,88%**
-   Sequência de 10 perdas consecutivas: **0,00%**

**Conclusão:**

-   A ganância é sua pior inimiga.
-   Aposte com responsabilidade, e lembre-se: **o cassino sempre tem vantagem**.

**Minha Dica:**\
Use este projeto como aprendizado, ou para arrancar pequenos ganhos. Mas não alimente seu vício (ou sua ganância).

* * * * *

## 🛠 Bônus e Ferramentas Interativas
----------------------------------

### 1\. Backend e Frontend Interativos

O projeto inclui um sistema robusto de análise com:

-   **Backend:** `ctsv2.py`, baseado em Flask, para cálculos avançados como **RSI**, **média móvel**, e comunicação em tempo real.
-   **Frontend:** `index.html` e `display.html` para visualização interativa de gráficos.

**Exemplo:**\
Você pode visualizar o comportamento dos multiplicadores em tempo real e interagir com controles para ajustar alvos, pausar ou acelerar a análise.

* * * * *

### 2\. Monitores Inteligentes

-   **`l.js` e `laV2.js`:** Scripts em JavaScript que monitoram e registram multiplicadores, analisando sequências de perdas e gerenciando blocos de análise.

* * * * *

📜 Scripts Disponíveis
----------------------

### Análise e Simulação

-   **`scj_matriz.py`:** Geração de multiplicadores e histórico.
-   **`scjs_matriz.py`:** Simulações paralelas para análise avançada.
-   **`scjv2_matriz.py`:** Relatórios detalhados com sequência de perdas.

### Visualização Avançada

-   **`scjv4_matriz.py`:** Gráficos estáticos e interativos para explorar padrões.
-   **`scjv8_matriz.py`:** Monitoramento em tempo real com GUI em **Tkinter**.

### Frontend/Backend

-   **`ctsv2.py`:** Backend Flask com comunicação WebSocket.
-   **`index.html` e `display.html`:** Interface moderna com gráficos interativos.

* * * * *

## 🛠 Como Rodar o Projeto
-----------------------

### Requisitos

-   **Python 3.9+**
-   Bibliotecas:

    ```
    pip install flask flask-socketio pandas numpy matplotlib

    ```

### Passos

1.  Clone este repositório:

    ```
    git clone https://github.com/OhmXLLI/CrashHack.git

    ```

2.  Entre na pasta e inicie o backend:

    ```
    cd CrashHack
    python ctsv2.py

    ```

3.  Abra o frontend (`index.html`) e o (`display.html`) em seu navegador para acessar os gráficos interativos.

* * * * *

## 🎯 Desafio para Desenvolvedores
-------------------------------

Será que você consegue usar essas ferramentas para desenvolver estratégias consistentes?\
Aqui está o desafio:

1.  Teste os scripts com diferentes seeds e alvos.
2.  Explore métricas como **RSI** para identificar padrões vencedores.
3.  Se possível, **crie um método** que maximize os ganhos no Crash.

**Nota:** Eu tentei e falhei, mas quem sabe você consiga?

* * * * *

## 📄 Licença
----------

Este projeto está sob a licença MIT. Para mais informações, consulte o arquivo LICENSE.

* * * * *

## 📂 **Adendo: Não Pule os Manuais!**  

> **🚀 IMPORTANTE:** Na pasta deste projeto, você encontrará **manuais detalhados** que explicam como utilizar cada script.  
> Eles são essenciais para aproveitar ao máximo as ferramentas disponíveis e compreender as análises.  

📘 **O que você encontrará nos manuais?**
- Explicações passo a passo de **como rodar os scripts**.
- Descrição detalhada de **cada funcionalidade e parâmetro**.
- Exemplos práticos para personalizar as ferramentas ao seu cenário.

💡 **Dica:**  
Antes de executar qualquer script, **dê uma olhada nos manuais**. Eles foram criados para facilitar sua vida e garantir que você extraia o melhor do projeto.  

<div align="center">
  <h3>📥 Não deixe de conferir!</h3>
  <img src="https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExcjI5aXJyZXEzMmtjbjhlMmJqb3VqOW11bjRpdnI5dW0yYWlsanZpayZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3o6MbbwX2g2GA4MUus/giphy.gif" alt="Leia os manuais!" width="300px">
</div>
