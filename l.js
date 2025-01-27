class MultiplicadorMonitor {
    constructor(target = 1.5, perdasConsecutivas = 3) {
        this.target = target;
        this.perdasConsecutivas = perdasConsecutivas;
        this.perdasAtuais = 0;
        this.botaoParar = null;
    }

    init() {
        console.log('🟢 Monitor de multiplicadores iniciado.');
        this.observarMultiplicadores();
        this.observarBotao();
    }

    observarBotao() {
        const buscarBotao = () => {
            // Seleciona o botão de "Parar Aposta Automática"
            const botaoParar = Array.from(document.querySelectorAll('button')).find(button => {
                return button.innerText.includes("Parar Aposta Automática") || 
                       button.innerText.includes("Iniciar aposta automática");
            });

            if (botaoParar) {
                console.log('✅ Botão de aposta encontrado.');
                this.botaoParar = botaoParar;
                return true;
            } else {
                console.warn('❌ Botão de aposta não encontrado!');
                return false;
            }
        };

        if (!buscarBotao()) {
            // Tenta buscar novamente após 1 segundo
            setTimeout(() => {
                this.observarBotao();
            }, 1000);
        }
    }

    observarMultiplicadores() {
        const containerResultados = document.querySelector('.OriginalGameRecentResult_originalGameResultsWrapper__aCNPr');

        if (!containerResultados) {
            console.warn('❌ Contêiner de resultados do jogo não encontrado!');
            return;
        }

        const observer = new MutationObserver(mutations => {
            mutations.forEach(mutation => {
                if (mutation.addedNodes && mutation.addedNodes.length > 0) {
                    mutation.addedNodes.forEach(node => {
                        if (node.nodeType === Node.ELEMENT_NODE) {
                            const valor = parseFloat(node.textContent.trim());
                            this.processarMultiplicador(valor);
                        }
                    });
                }
            });
        });

        observer.observe(containerResultados, { childList: true });
    }

    processarMultiplicador(valor) {
        if (isNaN(valor) || valor < 1) {
            console.warn(`⚠️ Valor inválido ignorado: ${valor}`);
            return;
        }

        console.log(`🎲 Multiplicador capturado: ${valor}`);

        // Verifica se é uma perda
        if (valor < this.target) {
            this.perdasAtuais++;
            console.warn(`⚠️ Perda registrada! Total de perdas consecutivas: ${this.perdasAtuais}`);

            if (this.perdasAtuais >= this.perdasConsecutivas) {
                console.error('❌ Limite de perdas consecutivas atingido! Parando apostas...');
                this.pararApostas();
            }
        } else {
            // Zera o contador de perdas em caso de ganho
            this.perdasAtuais = 0;
        }
    }

    pararApostas() {
        if (!this.botaoParar) {
            console.error('❌ Botão de aposta não está disponível para parar!');
            return;
        }

        console.log('🛑 Tentando parar as apostas...');
        
        // Simula um clique real no botão
        const eventoClique = new MouseEvent('click', {
            bubbles: true,
            cancelable: true,
            view: window,
        });

        this.botaoParar.dispatchEvent(eventoClique);
        console.log('✅ Evento de clique disparado no botão.');

        // Valida se o botão foi realmente clicado
        setTimeout(() => {
            if (this.botaoParar.innerText.includes("Iniciar aposta automática")) {
                console.log('✅ Aposta automática parada com sucesso.');
            } else {
                console.warn('❌ Falha ao parar apostas, tentando novamente...');
                this.pararApostas(); // Tenta novamente
            }
        }, 1000); // Aguarda 1 segundo para validar o clique
    }
}

// Inicializa o monitor
const monitor = new MultiplicadorMonitor(1.5, 3); // Target: 1.5, Perdas consecutivas: 3
monitor.init();
