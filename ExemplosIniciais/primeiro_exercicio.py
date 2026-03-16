import numpy as np
import matplotlib.pyplot as plt

# 1. Matriz de Vértices (Geometria)
# Triângulo com pontos (0,0), (2,0) e (1,2). 
# Repetimos o primeiro ponto na última coluna para fechar a linha do desenho.
# Usamos coordenadas homogêneas: a última linha inteira é preenchida com 1.
vertices_originais = np.array([
    [0, 2, 1, 0],  # Coordenadas X
    [0, 0, 2, 0],  # Coordenadas Y
    [1, 1, 1, 1]   # Coordenada Homogênea (M)
])

# 2. Matriz de Translação
# Vamos mover o triângulo +4 no eixo X e +3 no eixo Y
tx = 4
ty = 3
matriz_translacao = np.array([
    [1, 0, tx],
    [0, 1, ty],
    [0, 0, 1]
])

# 3. Aplicando a Transformação Matemática
# Multiplicamos a matriz de translação 3x3 pela matriz de vértices 3x4
vertices_transformados = np.dot(matriz_translacao, vertices_originais)

# 4. Renderizando na Tela
plt.figure(figsize=(8, 6))

# Plota o triângulo original (em azul)
plt.plot(vertices_originais[0, :], vertices_originais[1, :], 'b-o', label='Original')

# Plota o triângulo transformado (em vermelho)
plt.plot(vertices_transformados[0, :], vertices_transformados[1, :], 'r-o', label='Transladado')

# Configurações do gráfico
plt.axhline(0, color='black', linewidth=1)
plt.axvline(0, color='black', linewidth=1)
plt.grid(True, linestyle='--', alpha=0.7)
plt.xlim(-1, 8)
plt.ylim(-1, 8)
plt.legend()
plt.title('Computação Gráfica: Transformação 2D - Translação')

plt.show()