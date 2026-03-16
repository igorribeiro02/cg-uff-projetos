import numpy as np 

import matplotlib.pyplot as plt

#importanto as bibliotecas para animação
import matplotlib.animation as animation

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

# O corpo é fixo, desenhamos uma vez só
ax.plot(corpo[0, :], corpo[1, :], 'k-', linewidth=4)

# As asas vão mudar, então criamos linhas "vazias" que serão atualizadas
linha_asa_dir, = ax.plot([], [], color='gray', linewidth=3)
linha_asa_esq, = ax.plot([], [], color='gray', linewidth=3)

ax.legend() # adicionando legenda para identificar as partes do objeto
ax.set_title('Objeto Animado - Estrutura Inicial') # título do gráfico

art_x , art_y = 1,-1 # ponto de articulação para a asa direita (o ponto onde a asa vai "bater")

#COnfigurações para a animação
def animar(i):
    # o valor i vai de 0 a 2*pi, o seno faz o valor subir e descer suavemente, criando o efeito de bater de asa
    escala_y = 0.65 + 0.35 * np.sin(i)  # a asa vai achatar no eixo y, criando o efeito de bater, e depois volta ao normal

    #Regras de composição de transformações
    #1. translação para levar o ponto de articulação para a origem (-art_x, -art_y); leva o ombro do objeto para origm
    #2. Escala (1.0, escala_y) para achatar a asa no eixo y, criando o efeito de bater
    #3. translacao (art_x, art_y) para levar a asa de volta para a posição original
    matriz_bater = np.dot(translacao(art_x, art_y), np.dot(escala(1.0, escala_y), translacao(-art_x, -art_y)))

    #aplicando a matriz de transformação na asa direita e depois na asa esquerda
    asa_d_animada = np.dot(matriz_bater, asa_direita)

    #refletindo a asa esquerda para gerar a animação da asa esquerda
    asa_e_animada = np.dot(reflexao_y(), asa_d_animada)

    #atualiza as linhas da tabela 
    linha_asa_dir.set_data(asa_d_animada[0, :], asa_d_animada[1, :])
    linha_asa_esq.set_data(asa_e_animada[0, :], asa_e_animada[1, :])

    return linha_asa_dir, linha_asa_esq

#criando a animação
# frames: criamos 60 passos de 0 até 2*PI (um ciclo trigonométrico completo do seno)
passos_tempo = np.linspace(0, 2 * np.pi, 60) # 60 frames para uma animação suave
ani = animation.FuncAnimation(fig, animar, frames=passos_tempo, blit=True, repeat=True, interval= 15)
plt.show()