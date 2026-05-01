"""
==============================================================================
Banguela 3D — Visualização Interativa
Computação Gráfica - UFF  |  Aluno: Igor Ribeiro

Arraste com o mouse para rotacionar.  Scroll para zoom.
Pontos laranjas = articulações físicas do dragão.

Execute: python banguela_3d_visual.py
==============================================================================
"""
import sys, io
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.patches import Patch
import matplotlib.lines as mlines

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# =============================================================================
# HELPERS — geradores de faces para cada tipo de poliedro
# =============================================================================

def box_faces(x0, x1, y0, y1, z0, z1):
    """Paralelepípedo: 8 vértices, 12 arestas, 6 faces  →  V-E+F = 2"""
    v = np.array([
        [x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0],   # z0
        [x0,y0,z1],[x1,y0,z1],[x1,y1,z1],[x0,y1,z1],   # z1
    ])
    return [v[[0,3,2,1]], v[[4,5,6,7]],
            v[[0,1,5,4]], v[[3,7,6,2]],
            v[[0,4,7,3]], v[[1,2,6,5]]]

def hex_prism_faces(x0, x1, R):
    """Prisma hexagonal: 12v, 18a, 8f  →  V-E+F = 2"""
    angs  = np.radians(np.arange(6) * 60)
    front = np.array([[x1, R*np.cos(a), R*np.sin(a)] for a in angs])
    back  = np.array([[x0, R*np.cos(a), R*np.sin(a)] for a in angs])
    faces = [front, back[::-1]]
    for i in range(6):
        j = (i+1) % 6
        faces.append(np.array([front[i], front[j], back[j], back[i]]))
    return faces

def pyramid4_faces(bx, tx, y0, y1, z0, z1):
    """Pirâmide quadrada: 5v, 8a, 5f  →  V-E+F = 2"""
    B = np.array([[bx,y0,z0],[bx,y0,z1],[bx,y1,z1],[bx,y1,z0]])
    T = np.array([tx, (y0+y1)/2, (z0+z1)/2])
    faces = [B[[0,3,2,1]]]
    for i in range(4):
        faces.append(np.array([B[i], B[(i+1)%4], T]))
    return faces

def tri_prism_faces(va, vb, vc, axis, delta):
    """Prisma triangular: 6v, 9a, 5f  →  V-E+F = 2"""
    va, vb, vc = (np.array(x, dtype=float) for x in (va, vb, vc))
    d = np.zeros(3); d['xyz'.index(axis)] = delta
    wa, wb, wc = va+d, vb+d, vc+d
    return [
        np.array([va, vc, vb]),
        np.array([wa, wb, wc]),
        np.array([va, vb, wb, wa]),
        np.array([vb, vc, wc, wb]),
        np.array([vc, va, wa, wc]),
    ]

# =============================================================================
# PARTES DO DRAGÃO
# cada entrada: (faces, cor_face, cor_borda, alpha, nome)
# =============================================================================

PARTES = [
    # ── Parte principal ─────────────────────────────────────────────────────
    (hex_prism_faces(-1.5, 1.5, 0.8),
     '#1e2428', '#3a4a55', 0.97, 'Corpo (prisma hexagonal)'),

    # ── Pescoço / Cabeça ────────────────────────────────────────────────────
    (box_faces(1.5, 2.3, -0.20, 0.60, -0.35, 0.35),
     '#1c2226', '#3a4a55', 0.97, 'Pescoço'),
    (box_faces(2.3, 3.5, -0.30, 0.70, -0.55, 0.55),
     '#181e22', '#3a4a55', 0.97, 'Cabeça'),

    # ── Cauda + nadadeiras ───────────────────────────────────────────────────
    (pyramid4_faces(-1.5, -3.5, -0.40, 0.40, -0.50, 0.50),
     '#1e2428', '#3a4a55', 0.97, 'Cauda (pirâmide)'),
    (tri_prism_faces((-3.5,0,.05),  (-3.0,.55,.65), (-3.8,0,.70),  'y', .05),
     '#263035', '#4a5a65', 0.95, 'Nadadeira dir'),
    (tri_prism_faces((-3.5,0,-.05), (-3.0,.55,-.65),(-3.8,0,-.70), 'y', .05),
     '#263035', '#4a5a65', 0.95, 'Nadadeira esq'),

    # ── Asas ────────────────────────────────────────────────────────────────
    (box_faces(-0.15, 0.15, 0.80, 1.80, 0.30, 0.70),
     '#1c2226', '#3a4a55', 0.97, 'Braço asa dir'),
    (tri_prism_faces((0,1.80,.50),(0,2.60,2.20),(.50,.80,1.80), 'x', .08),
     '#2a3540', '#4a5a65', 0.65, 'Membrana asa dir'),
    (box_faces(-0.15, 0.15, 0.80, 1.80, -0.70, -0.30),
     '#1c2226', '#3a4a55', 0.97, 'Braço asa esq'),
    (tri_prism_faces((0,1.80,-.50),(0,2.60,-2.20),(.50,.80,-1.80),'x', .08),
     '#2a3540', '#4a5a65', 0.65, 'Membrana asa esq'),

    # ── Pernas ──────────────────────────────────────────────────────────────
    (box_faces( 0.80, 1.20, -1.90, -0.80,  0.30,  0.70),
     '#1a2024', '#3a4a55', 0.97, 'Perna DD'),
    (box_faces( 0.80, 1.20, -1.90, -0.80, -0.70, -0.30),
     '#1a2024', '#3a4a55', 0.97, 'Perna DE'),
    (box_faces(-1.20,-0.80, -1.90, -0.80,  0.30,  0.70),
     '#1a2024', '#3a4a55', 0.97, 'Perna TD'),
    (box_faces(-1.20,-0.80, -1.90, -0.80, -0.70, -0.30),
     '#1a2024', '#3a4a55', 0.97, 'Perna TE'),
]

# =============================================================================
# ARTICULAÇÕES (posição 3D + rótulo)
# =============================================================================

ARTICULACOES = [
    ( 1.5,  0.3,  0.0, 'Pescoço\n(esférico 3DOF)'),
    ( 2.3,  0.3,  0.0, 'Cabeça\n(charneira 1DOF)'),
    (-1.5,  0.0,  0.0, 'Cauda\n(composto 2DOF)'),
    (-3.5,  0.0,  0.0, 'Nadadeira\n(charneira 1DOF)'),
    ( 0.5,  0.8,  0.5, 'Ombro Dir\n(esférico 3DOF)'),
    ( 0.0,  1.8,  0.5, 'Cotovelo Dir\n(charneira 1DOF)'),
    ( 0.5,  0.8, -0.5, 'Ombro Esq\n(esférico 3DOF)'),
    ( 0.0,  1.8, -0.5, 'Cotovelo Esq\n(charneira 1DOF)'),
    ( 1.0, -0.8,  0.5, 'Quadril DD\n(esférico 3DOF)'),
    ( 1.0, -0.8, -0.5, 'Quadril DE\n(esférico 3DOF)'),
    (-1.0, -0.8,  0.5, 'Quadril TD\n(esférico 3DOF)'),
    (-1.0, -0.8, -0.5, 'Quadril TE\n(esférico 3DOF)'),
]

# =============================================================================
# FIGURA
# =============================================================================

fig = plt.figure(figsize=(15, 9), facecolor='#0b0f14')
ax  = fig.add_subplot(111, projection='3d')
ax.set_facecolor('#0b0f14')

# Renderiza cada parte
for faces, fc, ec, alpha, _ in PARTES:
    col = Poly3DCollection(faces, facecolor=fc, edgecolor=ec,
                           linewidth=0.5, alpha=alpha)
    ax.add_collection3d(col)

# Articulações
xs = [a[0] for a in ARTICULACOES]
ys = [a[1] for a in ARTICULACOES]
zs = [a[2] for a in ARTICULACOES]
ax.scatter(xs, ys, zs, color='#FF6B2B', s=90, depthshade=False, zorder=10)

# Linhas de esqueleto (hierarquia de juntas)
ESQUELETO = [
    (-1.5,0,0, -3.5,0,0),    # corpo → cauda
    (1.5,0.3,0, 2.3,0.3,0),  # pescoço
    (2.3,0.3,0, 2.3,0.3,0),  # cabeça
    (0.5,0.8,0.5, 0,1.8,0.5),  # ombro dir → cotovelo dir
    (0.5,0.8,-0.5, 0,1.8,-0.5), # ombro esq → cotovelo esq
    (1,-.8,.5,  1,-1.9,.5),   # quadril DD → pé
    (1,-.8,-.5, 1,-1.9,-.5),
    (-1,-.8,.5,  -1,-1.9,.5),
    (-1,-.8,-.5, -1,-1.9,-.5),
]
for x1,y1,z1,x2,y2,z2 in ESQUELETO:
    ax.plot([x1,x2],[y1,y2],[z1,z2], color='#FF6B2B', lw=0.8, alpha=0.4)

# Limites e eixos
ax.set_xlim(-4.2, 4.2)
ax.set_ylim(-2.8, 3.2)
ax.set_zlim(-2.8, 2.8)

ax.set_xlabel('X  (cauda ←→ cabeça)', color='#6b7f8a', labelpad=8)
ax.set_ylabel('Y  (baixo ←→ cima)',    color='#6b7f8a', labelpad=8)
ax.set_zlabel('Z  (profundidade)',      color='#6b7f8a', labelpad=8)
ax.tick_params(colors='#3a4a55', labelsize=7)

ax.xaxis.pane.fill = False; ax.yaxis.pane.fill = False; ax.zaxis.pane.fill = False
ax.xaxis.pane.set_edgecolor('#1a2530')
ax.yaxis.pane.set_edgecolor('#1a2530')
ax.zaxis.pane.set_edgecolor('#1a2530')
ax.grid(color='#1a2530', linewidth=0.4)

ax.view_init(elev=22, azim=-48)   # vista inicial: 3/4 frontal-superior

ax.set_title(
    'Banguela  —  Objeto 3D  |  Computação Gráfica / UFF\n'
    'Arraste para rotacionar  ·  Scroll para zoom  ·  ● pontos laranjas = articulações',
    color='#c8d8e0', fontsize=11, pad=12
)

# Legenda
legend_els = [
    Patch(fc='#1e2428', ec='#3a4a55', label='Corpo, pescoço, cabeça (prisma hex / box)'),
    Patch(fc='#263035', ec='#4a5a65', label='Cauda (pirâmide) + nadadeiras (prisma tri)'),
    Patch(fc='#2a3540', ec='#4a5a65', label='Membranas das asas (semi-transparente)'),
    Patch(fc='#1a2024', ec='#3a4a55', label='Pernas (4 × paralelepípedo)'),
    mlines.Line2D([],[], marker='o', color='#0b0f14',
                  markerfacecolor='#FF6B2B', markersize=9,
                  label='12 articulações  (esférica / charneira / composta)'),
]
ax.legend(handles=legend_els, loc='upper left',
          facecolor='#111820', edgecolor='#2a3a45',
          labelcolor='#c8d8e0', fontsize=8.5)

plt.tight_layout()
plt.show()
