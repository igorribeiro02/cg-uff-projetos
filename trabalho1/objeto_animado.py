import numpy as np 

import matplotlib.pyplot as plt

#funções matemáticas

#usando matrizes 3x3 para transformar pontos 2d em coordenadas homogêneas (x, y, 1)

def translacao(tx,ty):
    return np.array([[1,0,tx],[0,1,ty],[0,0,1]]) # estes sao os valores da matriz de translacao

def escala(sx,sy):
    return np.array([[sx,0,0],[0,sy,0],[0,0,1]]) # estes sao os valores da matriz de escala

def reflexao_y(): # reflexao no eixo y (inverte x)
    return np.array([[-1,0,0],[0,1,0],[0,0,1]])
#esta funcao inverte o sinal de X para criar o efeito de reflexao no eixo Y

# geometria (os pontos do objeto)
# o corpo será feito de um polígono central, e as asas serão triângulos anexados a ele
corpo = np.array([
    [0,  1,  1, -1, -1,  0],  # Coordenadas X
    [3,1,-3,-3,1 ,3], # Coordenadas Y
    [1,  1,   1,   1,   1,   1] # Coordenada homogênea (M)
])

#asa direita (a parte que irá se mover e depois irá ser refletida para criar a asa esquerda)
asa_direita = np.array([
    [1,5,4,1,1], # Coordenadas X
    [1,  0, -3, -1,  1],  # Y
    [1,  1,  1,  1,  1] # Coordenada homogênea (M)
])

print("Corpo do Objeto:\n", corpo)
print("Asa Direita:\n", asa_direita)
