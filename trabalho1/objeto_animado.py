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


#testando a reflexao da asa direita para criar o movimento da asa esquerda

asa_esquerda = np.dot(reflexao_y(), asa_direita) # aplicando a reflexao no eixo y para criar a asa esquerda

#configurar  o grafico que vai aparecer o objeto animado
fig, ax = plt.subplots(figsize=(8, 8))

#no eixo x, o limite vai de -6 a 6, e no eixo y, o limite vai de -4 a 4
ax.set_xlim(-6, 6)
ax.set_ylim(-5,5 )
#impedindo que objeto fique esticado
ax.set_aspect('equal')
#plotando o corpo do objeto
ax.grid(True, linestyle='--', alpha=0.5) # adicionando uma grade para facilitar a visualização


# Desenhando as linhas estáticas
ax.plot(corpo[0, :], corpo[1, :], 'k-', linewidth=4, label="Corpo")
ax.plot(asa_direita[0, :], asa_direita[1, :], 'b-', linewidth=2, label="Asa Dir")
ax.plot(asa_esquerda[0, :], asa_esquerda[1, :], 'g-', linewidth=2, label="Asa Esq")

ax.legend() # adicionando legenda para identificar as partes do objeto
ax.set_title('Objeto Animado - Estrutura Inicial') # título do gráfico
plt.show() # exibindo o gráfico