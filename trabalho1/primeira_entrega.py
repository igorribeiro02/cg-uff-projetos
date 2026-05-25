import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# 1. FUNÇÕES MATEMÁTICAS (Kit de Ferramentas)
# ==========================================
def reflexao_y():
    """Matriz de Reflexão 2D no eixo Y (inverte X) [cite: 156-157]"""
    return np.array([[-1, 0, 0], [0, 1, 0], [0, 0, 1]])

# ==========================================
# 2. DEFININDO O OBJETO E A TOPOLOGIA
# ==========================================
# O último ponto repete o primeiro para fechar a figura.
# A última linha de cada matriz é a Coordenada Homogênea M=1[cite: 799, 935].

corpo = np.array([
    [0,  1,  1, -1, -1,  0],  # Coordenadas X
    [3,  1, -3, -3,  1,  3],  # Coordenadas Y
    [1,  1,  1,  1,  1,  1]   # Coordenada Homogênea M
])

asa_direita = np.array([
    [1,  4,  3,  1,  1],  # Coordenadas X
    [1,  0, -2, -1,  1],  # Coordenadas Y
    [1,  1,  1,  1,  1]   # Coordenada Homogênea M
])

# Criando a Asa Esquerda automaticamente usando a transformação linear de Reflexão [cite: 633-635]
asa_esquerda = np.dot(reflexao_y(), asa_direita)

# ==========================================
# 3. RENDERIZANDO NA TELA COM PONTOS VISÍVEIS
# ==========================================
plt.figure(figsize=(10, 8))

# O parâmetro 'o' desenha as "bolinhas" nos vértices da nossa estrutura de dados
plt.plot(corpo[0, :], corpo[1, :], 'k-o', linewidth=3, markersize=8, label="Corpo")
plt.plot(asa_direita[0, :], asa_direita[1, :], 'b-o', linewidth=2, markersize=6, label="Asa Direita")
plt.plot(asa_esquerda[0, :], asa_esquerda[1, :], 'g-o', linewidth=2, markersize=6, label="Asa Esquerda")

# Função auxiliar para escrever as coordenadas (X, Y) do lado de cada ponto
def anotar_pontos(matriz, cor):
    # O loop vai até a penúltima coluna para não repetir o texto do último ponto (que fecha o polígono)
    for i in range(matriz.shape[1] - 1): 
        x, y = matriz[0, i], matriz[1, i]
        plt.text(x + 0.2, y + 0.1, f'({int(x)}, {int(y)})', color=cor, fontsize=10, fontweight='bold')

# Escrevendo os pontos na tela
anotar_pontos(corpo, 'black')
anotar_pontos(asa_direita, 'blue')
anotar_pontos(asa_esquerda, 'green')

# Configurações visuais do gráfico
plt.axhline(0, color='black', linewidth=1)
plt.axvline(0, color='black', linewidth=1)
plt.grid(True, linestyle='--', alpha=0.6)
plt.xlim(-6, 6)
plt.ylim(-5, 5)
plt.legend()
plt.title('Trabalho 1 - Estrutura de Dados do Objeto 2D (Geometria e Topologia)')
plt.gca().set_aspect('equal') # Impede que o gráfico fique distorcido

plt.show()