class MultiplicadorMonitor {
    constructor(target = 1.5, perdasConsecutivas = 3) {
        this.target = target;
        this.perdasConsecutivas = perdasConsecutivas;
        this.perdasAtuais = 0;
        this.botaoParar = null;
        
        // Sistema de blocos
        this.blocoAtual = 1;
        this.maxBlocos = 10;
        this.multiplicadoresBloco = [];
        this.historicoMaiorPerdasPorBloco = [];
        
        this.maiorSequenciaPerdas = 0;
        this.maiorSequenciaPerdasBloco = 0;
        this.registroPerdas = [];
        this.sequenciaAtual = 0;
        this.expandirMultiplicadores = false;
        this.expandirRegistros = false;
    }

    init() {
        console.clear();
        console.log('🟢 Monitor de multiplicadores iniciado.');
        console.log(`Target: ${this.target} | Perdas Monitoradas: ${this.perdasConsecutivas}`);
        console.log('----------------------------------------');
        this.observarMultiplicadores();
        this.observarBotao();
    }

    mostrarStatus() {
        console.clear();
        console.log('📊 MONITOR DE TRADING - STATUS');
        console.log('----------------------------------------');
        console.log(`🎯 Target: ${this.target} | Perdas Monitoradas: ${this.perdasConsecutivas}`);
        console.log(`📈 Bloco ${this.blocoAtual}/${this.maxBlocos}: ${this.multiplicadoresBloco.length}/300`);
        console.log(`⚠️ Perdas Consecutivas Atuais: ${this.perdasAtuais}`);
        console.log(`📉 Maior Sequência de Perdas (Total): ${this.maiorSequenciaPerdas}`);
        console.log(`📊 Maior Sequência de Perdas (Bloco): ${this.maiorSequenciaPerdasBloco}`);
        
        if (this.historicoMaiorPerdasPorBloco.length > 0) {
            console.log('\n📊 Histórico de Maiores Perdas por Bloco:');
            this.historicoMaiorPerdasPorBloco.forEach(hist => {
                console.log(`Bloco ${hist.bloco}: ${hist.maiorSequencia} perdas`);
            });
        }
        
        console.log('----------------------------------------');
        
        console.log('📝 Registro de Perdas Monitoradas:');
        if (this.registroPerdas.length === 0) {
            console.log('Nenhum registro ainda...');
        } else {
            if (this.expandirRegistros) {
                this.registroPerdas.forEach(registro => {
                    console.log(`Bloco ${registro.bloco} - Perda ${registro.perdas}x ${this.formatarData(registro.timestamp)}`);
                });
            } else {
                console.log('[▼] ... (digite monitor.toggleRegistros() para expandir)');
            }
        }
        
        console.log('----------------------------------------');
        
        console.log('📋 Multiplicadores Capturados:');
        if (this.expandirMultiplicadores) {
            console.log(this.multiplicadoresBloco);
        } else {
            console.log('[▼] ... (digite monitor.toggleMultiplicadores() para expandir)');
        }
    }

    toggleMultiplicadores() {
        this.expandirMultiplicadores = !this.expandirMultiplicadores;
        this.mostrarStatus();
    }

    toggleRegistros() {
        this.expandirRegistros = !this.expandirRegistros;
        this.mostrarStatus();
    }

    formatarData(timestamp) {
        return new Date(timestamp).toLocaleTimeString('pt-BR');
    }

    processarMultiplicador(valor) {
        if (isNaN(valor) || valor < 1) return;

        this.multiplicadoresBloco.push(valor);
        
        // Verifica se completou um bloco
        if (this.multiplicadoresBloco.length >= 300) {
            this.historicoMaiorPerdasPorBloco.push({
                bloco: this.blocoAtual,
                maiorSequencia: this.maiorSequenciaPerdasBloco
            });
            
            // Se atingiu o máximo de blocos, reseta tudo
            if (this.blocoAtual >= this.maxBlocos) {
                console.log('🔄 Resetando monitor após 10 blocos completos...');
                this.resetarMonitor();
            } else {
                // Avança para o próximo bloco
                this.blocoAtual++;
                this.multiplicadoresBloco = [valor];
                this.maiorSequenciaPerdasBloco = 0;
            }
        }

        if (valor < this.target) {
            this.perdasAtuais++;
            this.sequenciaAtual++;
            
            if (this.sequenciaAtual > this.maiorSequenciaPerdasBloco) {
                this.maiorSequenciaPerdasBloco = this.sequenciaAtual;
            }
            
            if (this.sequenciaAtual > this.maiorSequenciaPerdas) {
                this.maiorSequenciaPerdas = this.sequenciaAtual;
            }

            if (this.perdasAtuais >= this.perdasConsecutivas) {
                console.error(`❌ Sequência de ${this.perdasAtuais} perdas detectada!`);
                this.pararApostas();
            }
        } else {
            if (this.sequenciaAtual >= this.perdasConsecutivas) {
                this.registroPerdas.push({
                    perdas: this.sequenciaAtual,
                    timestamp: new Date(),
                    bloco: this.blocoAtual
                });
            }
            this.perdasAtuais = 0;
            this.sequenciaAtual = 0;
        }

        this.mostrarStatus();
    }

    resetarMonitor() {
        this.blocoAtual = 1;
        this.multiplicadoresBloco = [];
        this.historicoMaiorPerdasPorBloco = [];
        this.maiorSequenciaPerdasBloco = 0;
        this.registroPerdas = [];
    }

    observarMultiplicadores() {
        const containerResultados = document.querySelector('.OriginalGameRecentResult_originalGameResultsWrapper__aCNPr');

        if (!containerResultados) {
            console.warn('❌ Contêiner de resultados não encontrado!');
            setTimeout(() => this.observarMultiplicadores(), 1000);
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

    observarBotao() {
        const buscarBotao = () => {
            const botaoParar = Array.from(document.querySelectorAll('button')).find(button => {
                return button.innerText.includes("Parar Aposta Automática") || 
                       button.innerText.includes("Iniciar aposta automática");
            });

            if (botaoParar) {
                this.botaoParar = botaoParar;
                return true;
            }
            return false;
        };

        if (!buscarBotao()) {
            setTimeout(() => this.observarBotao(), 1000);
        }
    }

    pararApostas() {
        if (!this.botaoParar) {
            console.error('❌ Botão de aposta não disponível!');
            return;
        }

        const eventoClique = new MouseEvent('click', {
            bubbles: true,
            cancelable: true,
            view: window
        });

        this.botaoParar.dispatchEvent(eventoClique);

        setTimeout(() => {
            if (this.botaoParar.innerText.includes("Iniciar aposta automática")) {
                console.log('✅ Aposta automática parada com sucesso.');
            } else {
                console.warn('❌ Falha ao parar apostas, tentando novamente...');
                this.pararApostas();
            }
        }, 1000);
    }
}

// Inicializa o monitor
const monitor = new MultiplicadorMonitor(1.5, 3);
monitor.init();

console.log('Para expandir os registros, digite: monitor.toggleRegistros()');
console.log('Para expandir os multiplicadores, digite: monitor.toggleMultiplicadores()');