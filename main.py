import random
import heapq

class PontodeColeta:
    def __init__(self, id, lixo=0):
        self.id = id
        self.lixo = lixo
        self.animais = self.gerar_animais()
        self.vizinhos = {} # arestas para deslocamento no grafo(bairro)

    def gerar_animais(self):
        # Cada ponto de coleta vai ter a probabilidade de ter rato,gato ou cachorro
        animais = {"rato": 0, "gato": 0, "cachorro": 0}  # inicializa um dicionario vazio de animais 
        if random.random() <= 0.5:
            animais["rato"] += 1
        if random.random() <= 0.25:
            animais["gato"] += 1
        if random.random() <= 0.1:
            animais["cachorro"] += 1
        return animais

    def quantidade_animais(self):
        # Retorna a quantidade de animais no ponto
        return self.animais["rato"] + self.animais["gato"] + self.animais["cachorro"]

    def adicionar_vizinho(self, vizinho, custo):
        self.vizinhos[vizinho] = custo # Adiciona vizinho e o custo(tempo para deslocar(peso das arestas do grafo))

    def __str__(self):
        return f"ponto: {self.id} - lixo : {self.lixo}m³, animais : {self.animais}"

class CentroZoonozes:
    def __init__(self, bairro, centro):
        self.bairro = bairro
        self.centro = centro
        self.carrocinhas = 3

    def enviar_carrocinha(self, ponto_inicial):
        if self.carrocinhas <= 0:
            print("Nenhuma carrocinha disponível no momento.")
            return
        
        print(f"Carrocinha enviada para o ponto {ponto_inicial}.")
        self.carrocinhas -= 1
        capacidade = 5
        caminho = list(self.bairro.pontos.keys())  # Simulação de percurso
        tempo_total = 0
        
        # Use Dijkstra to find the shortest path back to the center
        distancias, predecessores = self.bairro.dijkstra(ponto_inicial, self.centro)
        tempo_total = distancias[self.centro]
        
        for ponto_id in caminho:
            ponto = self.bairro.pontos[ponto_id]
            animais_no_ponto = sum(ponto.animais.values())
            
            if animais_no_ponto > 0:
                if capacidade > 0:
                    coletados = min(animais_no_ponto, capacidade)
                    capacidade -= coletados
                    
                    for animal, quantidade in ponto.animais.items():
                        if coletados <= 0:
                            break
                        if quantidade > 0:
                            removidos = min(quantidade, coletados)
                            ponto.animais[animal] -= removidos
                            coletados -= removidos
                    
                    print(f"Carrocinha coletou animais no ponto {ponto_id}. Capacidade restante: {capacidade}")
                
                if capacidade <= 0:
                    print("Carrocinha cheia! Retornando ao centro de zoonoses.")
                    self.carrocinhas += 1
                    return tempo_total
        
        print("Carrocinha completou o percurso.")
        self.carrocinhas += 1
        return tempo_total


class Bairro:
    def __init__(self):
        self.pontos = {}
        self.aterro = None
        self.zoonoses = None

    def adicionar_ponto(self, ponto: PontodeColeta):
        self.pontos[ponto.id] = ponto
    
    def dijkstra(self, origem, destino=None):
        """
        Implementa o algoritmo de Dijkstra para encontrar o caminho mais curto
        
        Parâmetros:
        - origem: id do ponto de origem
        - destino: id do ponto de destino (opcional, se não fornecido, calcula para todos os pontos)
        
        Retorna:
        - Dicionário de distâncias mínimas
        - Dicionário de predecessores para reconstruir caminhos
        """
        # Verificar se origem existe
        if origem not in self.pontos:
            raise ValueError(f"Ponto de origem {origem} não encontrado no grafo")
        
        # Inicialização
        distancias = {ponto: float('inf') for ponto in self.pontos}
        distancias[origem] = 0
        predecessores = {ponto: None for ponto in self.pontos}
        
        # Fila de prioridade para processamento dos vértices
        pq = [(0, origem)]
        
        while pq:
            dist_atual, ponto_atual = heapq.heappop(pq)
            
            # Se já encontramos um caminho mais longo, pula
            if dist_atual > distancias[ponto_atual]:
                continue
            
            # Se um destino específico foi encontrado, podemos parar
            if destino is not None and ponto_atual == destino:
                break
            
            # Verifica vizinhos
            for vizinho, custo in self.pontos[ponto_atual].vizinhos.items():
                distancia = dist_atual + custo
                
                # Se encontramos um caminho mais curto
                if distancia < distancias[vizinho]:
                    distancias[vizinho] = distancia
                    predecessores[vizinho] = ponto_atual
                    heapq.heappush(pq, (distancia, vizinho))
        
        return distancias, predecessores
    
    def caminho_minimo(self, origem, destino):
        """
        Recupera o caminho mínimo entre dois pontos
        
        Retorna uma lista de pontos no caminho mais curto
        """
        distancias, predecessores = self.dijkstra(origem, destino)
        
        # Verifica se há um caminho
        if distancias[destino] == float('inf'):
            return None
        
        # Reconstrói o caminho
        caminho = []
        ponto_atual = destino
        while ponto_atual is not None:
            caminho.append(ponto_atual)
            ponto_atual = predecessores[ponto_atual]
        
        # Inverte o caminho para ir da origem ao destino
        return list(reversed(caminho))

    def movimentar_animais(self):
        novos_animais = {ponto_id: [0, 0, 0] for ponto_id in self.pontos} # dicionario com pontos e animais

        for ponto_id, ponto in self.pontos.items():
            ratos, gatos, cachorros = ponto.animais
            vizinhos = list(ponto.vizinhos.keys())
            
            if not vizinhos:
                continue  # Se não há vizinhos, os animais não podem se mover

            # Regras para ratos
            if gatos > 0:
                for _ in range(ratos - 1):  # Apenas 1 rato fica no ponto
                    destino = random.choice(vizinhos)
                    novos_animais[destino][0] += 1
                ratos = 1 if ratos > 0 else 0
            
            # Regras para gatos
            if cachorros > 0:
                for _ in range(gatos):
                    destino = random.choice(vizinhos)
                    novos_animais[destino][1] += 1
                gatos = 0
            
            # Regras para todos os animais
            if ratos > 0 and gatos > 0 and cachorros > 0:
                for _ in range(ratos):
                    destino = random.choice(vizinhos)
                    novos_animais[destino][0] += 1
                for _ in range(gatos):
                    destino = random.choice(vizinhos)
                    novos_animais[destino][1] += 1
                ratos, gatos = 0, 0  # Cachorros permanecem

            # Regras para pontos sem lixo
            if ponto.lixo == 0:
                for _ in range(ratos):
                    destino = random.choice(vizinhos)
                    novos_animais[destino][0] += 1
                for _ in range(gatos):
                    destino = random.choice(vizinhos)
                    novos_animais[destino][1] += 1
                for _ in range(cachorros):
                    destino = random.choice(vizinhos)
                    novos_animais[destino][2] += 1
                ratos, gatos, cachorros = 0, 0, 0

            # Atualiza os animais restantes no ponto
            novos_animais[ponto_id][0] += ratos
            novos_animais[ponto_id][1] += gatos
            novos_animais[ponto_id][2] += cachorros

        # Atualiza os pontos com os novos estados dos animais
        for ponto_id, animais in novos_animais.items():
            self.pontos[ponto_id].animais = animais

class Carrodolixo:
    def __init__(self, carro, capacidade):
        self.carro = carro
        self.capacidade = capacidade 
        self.lixo_recolhido = 0
        self.funcionarios = random.randint(3, 5)
        self.compactacoes = 0  # Contador de compactações
        
    def coletar_lixo(self, ponto: PontodeColeta, centro: CentroZoonozes):
        tempo_coleta = ponto.lixo // self.funcionarios
        
        if ponto.quantidade_animais() > 0:
            print(f" Ponto {ponto.id}: Animais detectados!")
            print(f" Animais no ponto: {ponto.animais}")  # Exibe os animais detectados
            centro.enviar_carrocinha(ponto.id)

        if ponto.quantidade_animais() == 1:
            print(f"Lixo espalhou no ponto {ponto.id}! Tempo de coleta dobrado!")
            tempo_coleta *= 2
        
        self.lixo_recolhido += ponto.lixo
        ponto.lixo = 0
        return tempo_coleta
      
    def compactar_lixo(self):
        # compacta o lixo a 33,33% de seu volume total, até o máximo de 3 vezes.
        if self.lixo_recolhido >= self.capacidade and self.compactacoes < 3:
            self.lixo_recolhido = self.lixo_recolhido // 3  # Compacta o lixo a 1/3 do volume
            self.compactacoes += 1
            print(f"Lixo compactado. Compactações restantes: {3 - self.compactacoes}. Lixo atual: {self.lixo_recolhido}/{self.capacidade}")
            return True
        return False
    
    def descarregar_lixo(self):
        # Desacarrega o lixo no aterro e reinicia o caminhão.
        print(f"Descarregando lixo de {self.lixo_recolhido}/{self.capacidade} para o aterro")
        self.lixo_recolhido = 0
        self.compactacoes = 0  # resetando as compactações

    def mover_e_coletar(self, bairro: Bairro):
        tempo_total = 0
        caminho = list(bairro.pontos.keys())  # Simulação de um percurso simples pelo bairro

        for ponto_id in caminho:
            ponto = bairro.pontos[ponto_id]
            
            # Coleta de lixo no ponto
            print(f"Carro {self.carro} coletando no ponto {ponto_id}...")
            tempo_coleta = self.coletar_lixo(ponto, bairro.zoonoses)
            tempo_total += tempo_coleta
            
            # Compactação ou descarregamento
            if self.lixo_recolhido >= self.capacidade:
                if not self.compactar_lixo():
                    # Use Dijkstra to find shortest path to aterro
                    caminho_aterro = bairro.caminho_minimo(ponto_id, bairro.aterro)
                    if caminho_aterro:
                        # Use the last leg of the path to calculate time
                        tempo_deslocamento = bairro.pontos[caminho_aterro[-2]].vizinhos[caminho_aterro[-1]]
                        print(f"Carro {self.carro} indo ao aterro para descarregar.")
                        tempo_total += tempo_deslocamento
                    self.descarregar_lixo()
            
            print(f"Tempo total até agora: {tempo_total} minutos")
        
        return tempo_total

    def __str__(self):
        return f"Carro {self.carro} - Capacidade: {self.capacidade}m³, lixo recolhido: {self.lixo_recolhido}m³"
    

# método para ler o arquivo (nao possui classe)
def ler_arquivo(caminho_arquivo):
    bairro = Bairro()
    
    with open(caminho_arquivo, "r") as arquivo:
        linhas = arquivo.readlines()
    
    num_pontos = int(linhas[1].strip())
    
    # Ler os vizinhos
    idx = 4
    while linhas[idx].strip():
        linha = linhas[idx].strip().split(":")
        ponto_id = int(linha[0])
        if ponto_id not in bairro.pontos:
            bairro.adicionar_ponto(PontodeColeta(id=ponto_id))
    
        if linha[1].strip():
            for vizinho in linha[1].split(","):
                viz_id, custo = map(int, vizinho.strip().split())
                if viz_id not in bairro.pontos:
                    bairro.adicionar_ponto(PontodeColeta(id=viz_id))
                bairro.pontos[ponto_id].adicionar_vizinho(viz_id, custo)
        idx += 1
    
    # Quantidade de lixo
    idx += 2
    quantidades_lixo = list(map(int, linhas[idx].strip().split()))
    for i, lixo in enumerate(quantidades_lixo, start=1):
        bairro.pontos[i].lixo = lixo
    
    # Localização do aterro sanitário e centro de zoonoses
    idx += 3
    aterro, zoonoses = map(int, linhas[idx].strip().split())
    bairro.aterro = aterro
    bairro.zoonoses = zoonoses
    
    return bairro

def calcular_caminhoes_e_funcionarios(bairro, capacidade_caminhao, max_tempo=480):
    num_caminhoes = 1
    while True:
        caminhoes = [Carrodolixo(i, capacidade_caminhao) for i in range(num_caminhoes)]
        tempo_total = 0

        for carro in caminhoes:
            tempo_total += carro.mover_e_coletar(bairro)
        
        if tempo_total <= max_tempo:
            funcionarios = sum(carro.funcionarios for carro in caminhoes)
            return num_caminhoes, funcionarios
        
        num_caminhoes += 1


if __name__ == '__main__':
    # Caminho do arquivo
    arquivo = "grafo.txt"
    
    # Carregar os dados do bairro
    bairro = ler_arquivo(arquivo)

    centro_zoonoses = CentroZoonozes(bairro, bairro.zoonoses)
    bairro.zoonoses = centro_zoonoses 
    
    # Exemplo: Imprimir informações de cada ponto
    for ponto_id, ponto in bairro.pontos.items():
        print(f"Ponto {ponto_id}:")
        print(f"  Vizinhos: {ponto.vizinhos}")
        print(f"  Lixo: {ponto.lixo}")
        print(f"  Animais: {ponto.animais}")

    # Exibir aterro sanitário e centro de zoonoses
    print(f"Aterro Sanitário: {bairro.aterro}")
    print(f"Centro de Zoonoses: {bairro.zoonoses.centro}")
    #bairro.zoonoses.enviar_carrocinha(ponto_inicial=5)
    
    capacidade_caminhao = 10  # Capacidade em metros cúbicos
    num_caminhoes, num_funcionarios = calcular_caminhoes_e_funcionarios(bairro, capacidade_caminhao)
    print("\n------------------------------\n")
    print(f"Número mínimo de caminhões: {num_caminhoes}")
    print(f"Número total de funcionários: {num_funcionarios}")

