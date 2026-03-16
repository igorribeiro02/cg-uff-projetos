import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# 1. FUNÇÕES MATEMÁTICAS (O "Motor" do PDF)
# ==========================================

def translacao(tx, ty):
    """Matriz de Translação 2D [cite: 328-329]"""
    return np.array([
        [1, 0, tx],
        [0, 1, ty],
        [0, 0, 1]
    ])

def escala(sx, sy):
    """Matriz de Escala 2D [cite: 333]"""
    return np.array([
        [sx, 0, 0],
        [0, sy, 0],
        [0, 0, 1]
    ])

def rotacao(angulo_graus):
    """Matriz de Rotação 2D (em torno da origem) [cite: 187, 214]"""
    rad = np.radians(angulo_graus)
    c, s = np.cos(rad), np.sin(rad)
    return np.array([
        [c, -s, 0],
        [s,  c, 0],
        [0,  0, 1]
    ])

def cisalhamento(kx, ky):
    """Matriz de Cisalhamento 2D [cite: 223, 230]"""
    return np.array([
        [1, kx, 0],
        [ky, 1, 0],
        [0, 0, 1]
    ])

def reflexao(eixo):
    """Matriz de Reflexão 2D [cite: 156-163]"""
    if eixo == 'x':
        # Reflexão no eixo X (inverte Y) [cite: 162-163]
        return np.array([[1, 0, 0], [0, -1, 0], [0, 0, 1]])
    elif eixo == 'y':
        # Reflexão no eixo Y (inverte X) 
        return np.array([[-1, 0, 0], [0, 1, 0], [0, 0, 1]])
    return np.identity(3)


# ==========================================
# 2. DEFININDO O OBJETO (BANGUELA SINTÉTICO)
# ==========================================
# Cada coluna é um ponto [x, y, 1]. O último ponto repete o primeiro para fechar o desenho.

# Corpo do Dragão (Um polígono central)
corpo = np.array([
    [0,  1,  1, -1, -1,  0],  # Coordenadas X
    [3,  1, -3, -3,  1,  3],  # Coordenadas Y
    [1,  1,  1,  1,  1,  1]   # Coordenada Homogênea M=1 [cite: 458]
])

# Asa Direita (Conectada ao corpo no ponto X=1, Y=1)
asa_direita = np.array([
    [1,  4,  3,  1,  1],  # Coordenadas X
    [1,  0, -2, -1,  1],  # Coordenadas Y
    [1,  1,  1,  1,  1]   # Coordenada Homogênea M=1 [cite: 458]
])

# ==========================================
# 3. APLICANDO AS TRANSFORMAÇÕES (A MÁGICA)
# ==========================================

# A. Criando a Asa Esquerda automaticamente com Reflexão! 
asa_esquerda = np.dot(reflexao('y'), asa_direita)

# B. Fazendo a Asa Direita "bater" (Composição de Transformações) [cite: 310-313]
# Regra do PDF: Transladar P(1,1) para origem -> Transformar -> Transladar de volta [cite: 312-313]
ponto_articulacao_x = 1
ponto_articulacao_y = 1

# Matriz Composta = Translação_Ida * Escala_Achatar * Translação_Volta
# Multiplicamos de trás para frente (da direita para a esquerda)
matriz_bater_asa = np.dot(translacao(ponto_articulacao_x, ponto_articulacao_y), 
                   np.dot(escala(0.8, 0.2), # Achata a asa no eixo Y e um pouco no X
                          translacao(-ponto_articulacao_x, -ponto_articulacao_y)))

# Aplicando a matriz composta na asa
asa_direita_batendo = np.dot(matriz_bater_asa, asa_direita)


# ==========================================
# 4. RENDERIZANDO NA TELA
# ==========================================
plt.figure(figsize=(8, 8))

# Desenhando o Dragão Original (Cinza/Preto)
plt.plot(corpo[0, :], corpo[1, :], 'k-', linewidth=3, label="Corpo")
plt.plot(asa_direita[0, :], asa_direita[1, :], 'gray', linewidth=2, label="Asa Direita (Repouso)")
plt.plot(asa_esquerda[0, :], asa_esquerda[1, :], 'gray', linewidth=2, label="Asa Esquerda")

# Desenhando a Asa Animada (Vermelho)
plt.plot(asa_direita_batendo[0, :], asa_direita_batendo[1, :], 'r-', linewidth=3, label="Asa Direita (Batendo)")

# Configurações do gráfico
plt.axhline(0, color='black', linewidth=0.5)
plt.axvline(0, color='black', linewidth=0.5)
plt.grid(True, linestyle='--', alpha=0.6)
plt.xlim(-5, 5)
plt.ylim(-4, 4)
plt.legend()
plt.title('Transformações Geométricas - Estrutura do Dragão')

plt.show()