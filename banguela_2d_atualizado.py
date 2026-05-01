"""
==============================================================================
Banguela 2D — Vista Lateral Animada  (VERSÃO ATUALIZADA)
Computação Gráfica - UFF  |  Aluno: Igor Ribeiro

DIFERENÇAS em relação à versão original:
  ✓ Vista lateral (perfil) — não mais de cima
  ✓ Corpo correto: cabeça, pescoço, torso, cauda, pernas, asas
  ✓ Olho verde característico do Banguela
  ✓ Animação usa ROTAÇÃO em torno do joint (matriz correta)
    → antes: escala no eixo Y (incorreto fisicamente)
    → agora: R = T(joint) · Rθ · T(-joint)  (correto)
  ✓ Articulações exibidas com tipo e DOF

Execute: python banguela_2d_atualizado.py
==============================================================================
"""
import sys, io
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as anim
from matplotlib.patches import Polygon, Circle, FancyArrowPatch
from matplotlib.patches import Patch as LPatch
import matplotlib.lines as mlines

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# =============================================================================
# TRANSFORMAÇÕES 2D EM COORDENADAS HOMOGÊNEAS (matriciais — corretas)
# =============================================================================

def T(tx, ty):
    """Matriz de translação 3×3 homogênea"""
    return np.array([[1, 0, tx],
                     [0, 1, ty],
                     [0, 0,  1]], dtype=float)

def R(theta):
    """Matriz de rotação 3×3 homogênea"""
    c, s = np.cos(theta), np.sin(theta)
    return np.array([[ c, -s, 0],
                     [ s,  c, 0],
                     [ 0,  0, 1]], dtype=float)

def rodar_em_torno(pts, cx, cy, theta):
    """
    Rotaciona os pontos em torno de (cx, cy) por theta radianos.
    Composição correta:  M = T(cx,cy) · R(θ) · T(-cx,-cy)
    """
    M     = T(cx, cy) @ R(theta) @ T(-cx, -cy)
    pts_h = np.hstack([pts, np.ones((len(pts), 1))])
    return (M @ pts_h.T).T[:, :2]

# =============================================================================
# GEOMETRIA BASE — pose de repouso, vista lateral (plano XY)
# Dragão olha para a direita (+X). Y = cima. Unidades em metros.
# =============================================================================

# ── Corpo (torso) ─────────────────────────────────────────────────────────────
corpo_pts = np.array([
    [ 1.50,  0.30], [ 1.30,  0.78], [ 0.50,  0.85],
    [-0.50,  0.82], [-1.20,  0.65], [-1.50,  0.20],
    [-1.50, -0.35], [-1.20, -0.76], [ 0.00, -0.80],
    [ 1.20, -0.68], [ 1.50, -0.30],
])

# ── Pescoço ──────────────────────────────────────────────────────────────────
pescoco_pts = np.array([
    [1.50,  0.30], [2.30,  0.50],
    [2.30, -0.10], [1.50, -0.30],
])

# ── Cabeça (Banguela — larga e achatada) ─────────────────────────────────────
cabeca_pts = np.array([
    [2.30,  0.50], [2.60,  0.70], [3.10,  0.68], [3.40,  0.52],
    [3.50,  0.15], [3.50, -0.05], [3.20, -0.28], [2.80, -0.30],
    [2.30, -0.10],
])

# ── Perna dianteira (direita, visível de perfil) ──────────────────────────────
perna_f_pts = np.array([
    [0.85, -0.74], [0.85, -1.78], [1.18, -1.78], [1.18, -0.74],
])
pe_f_pts = np.array([
    [0.68, -1.78], [0.68, -1.95], [1.38, -1.95], [1.38, -1.78],
])

# ── Perna traseira (direita, visível de perfil) ───────────────────────────────
perna_r_pts = np.array([
    [-1.18, -0.74], [-1.18, -1.78], [-0.82, -1.78], [-0.82, -0.74],
])
pe_r_pts = np.array([
    [-1.38, -1.78], [-1.38, -1.95], [-0.62, -1.95], [-0.62, -1.78],
])

# ── Asa (quadrilátero completo — braço + membrana como corpo rígido 2D) ───────
# Gira em torno do OMBRO  (0.50, 0.80)
OMBRO = np.array([0.50, 0.80])

asa_pts = np.array([
    [ 0.50,  0.80],   # ombro  (joint — ponto fixo)
    [ 0.28,  1.82],   # cotovelo
    [-0.48,  2.55],   # ponta da asa (wingtip)
    [-1.05,  0.83],   # ancoragem traseira no tronco
])

# ── Cauda (corpo rígido que gira em torno do joint cauda-corpo) ───────────────
# Gira em torno de CAUDA_JOINT  (-1.50, 0.00)
CAUDA_JOINT = np.array([-1.50, 0.00])

cauda_pts = np.array([
    [-1.50,  0.20], [-2.50,  0.14], [-3.50,  0.00],
    [-2.50, -0.20], [-1.50, -0.35],
])

# Nadadeiras — seguem a cauda (mesma rotação)
fin_up_pts = np.array([
    [-3.50,  0.00], [-3.10,  0.55], [-3.78,  0.40],
])
fin_lo_pts = np.array([
    [-3.50,  0.00], [-3.12, -0.35], [-3.78, -0.22],
])

# =============================================================================
# CORES
# =============================================================================
C_ESCURO   = '#18202a'
C_CORPO    = '#1e2830'
C_ASA      = '#243040'
C_MEM      = '#2c3a4a'
C_PERNA    = '#1c2430'
C_JOINT    = '#FF6B2B'
C_BORDA    = '#3a5060'
C_BG       = '#0b0f14'

# =============================================================================
# FIGURA
# =============================================================================
fig, ax = plt.subplots(figsize=(15, 8), facecolor=C_BG)
ax.set_facecolor(C_BG)
ax.set_aspect('equal')
ax.set_xlim(-4.6, 4.6)
ax.set_ylim(-2.6, 3.6)
ax.axis('off')

# Grid sutil
for xv in np.arange(-4, 5, 1):
    ax.axvline(xv, color='#111a24', lw=0.4, zorder=0)
for yv in np.arange(-2, 4, 1):
    ax.axhline(yv, color='#111a24', lw=0.4, zorder=0)
ax.axhline(0, color='#1a2a38', lw=0.7, zorder=0)
ax.axvline(0, color='#1a2a38', lw=0.7, zorder=0)

# ── Patches estáticos ─────────────────────────────────────────────────────────
p_perna_r = Polygon(perna_r_pts, closed=True, fc=C_PERNA, ec=C_BORDA, lw=0.9, zorder=2)
p_pe_r    = Polygon(pe_r_pts,    closed=True, fc=C_PERNA, ec=C_BORDA, lw=0.9, zorder=2)
p_corpo   = Polygon(corpo_pts,   closed=True, fc=C_CORPO, ec=C_BORDA, lw=1.3, zorder=4)
p_pescoco = Polygon(pescoco_pts, closed=True, fc=C_CORPO, ec=C_BORDA, lw=1.0, zorder=4)
p_cabeca  = Polygon(cabeca_pts,  closed=True, fc=C_ESCURO,ec=C_BORDA, lw=1.3, zorder=4)
p_perna_f = Polygon(perna_f_pts, closed=True, fc=C_PERNA, ec=C_BORDA, lw=0.9, zorder=3)
p_pe_f    = Polygon(pe_f_pts,    closed=True, fc=C_PERNA, ec=C_BORDA, lw=0.9, zorder=3)

# ── Patches móveis ────────────────────────────────────────────────────────────
p_asa     = Polygon(asa_pts,     closed=True, fc=C_ASA,   ec=C_BORDA, lw=0.9, zorder=3, alpha=0.92)
p_cauda   = Polygon(cauda_pts,   closed=True, fc=C_CORPO, ec=C_BORDA, lw=1.0, zorder=3)
p_fin_up  = Polygon(fin_up_pts,  closed=True, fc=C_MEM,   ec=C_BORDA, lw=0.8, zorder=3)
p_fin_lo  = Polygon(fin_lo_pts,  closed=True, fc=C_MEM,   ec=C_BORDA, lw=0.8, zorder=3)

for p in [p_perna_r, p_pe_r, p_asa,
          p_corpo, p_pescoco, p_cabeca,
          p_cauda, p_fin_up, p_fin_lo,
          p_perna_f, p_pe_f]:
    ax.add_patch(p)

# ── Olho (Banguela — verde brilhante) ─────────────────────────────────────────
ax.add_patch(Circle((3.08,  0.34), 0.130, fc='white',   ec='none', zorder=6))
ax.add_patch(Circle((3.08,  0.34), 0.090, fc='#00e070', ec='none', zorder=7))
ax.add_patch(Circle((3.10,  0.34), 0.048, fc='#001a0a', ec='none', zorder=8))

# ── Articulações ──────────────────────────────────────────────────────────────
JOINTS = {
    'Pescoço\n(esférico·3DOF)':   ( 1.50,  0.10),
    'Cabeça\n(charneira·1DOF)':   ( 2.30,  0.10),
    'Ombro\n(esférico·3DOF)':     ( 0.50,  0.80),
    'Cotovelo\n(charneira·1DOF)': ( 0.28,  1.82),
    'Cauda\n(composto·2DOF)':     (-1.50,  0.00),
    'Nadadeira\n(charneira·1DOF)':(-3.50,  0.00),
    'Quadril D\n(esférico·3DOF)': ( 1.00, -0.80),
    'Quadril T\n(esférico·3DOF)': (-1.00, -0.80),
}

joint_circles = {}
for nome, (jx, jy) in JOINTS.items():
    c = Circle((jx, jy), 0.095, fc=C_JOINT, ec='white', lw=0.7, zorder=9)
    ax.add_patch(c)
    ax.annotate(nome, (jx, jy), xytext=(jx+0.08, jy+0.18),
                fontsize=5.5, color='#FF9F70', zorder=10,
                arrowprops=dict(arrowstyle='-', color='#FF6B2B', lw=0.5))
    joint_circles[nome] = c

# =============================================================================
# ANIMAÇÃO — usa rotação matricial correta em torno dos joints
# =============================================================================
N_FRAMES = 120

def animar(frame):
    t = (frame / N_FRAMES) * 2 * np.pi

    # ── ASA: rotação em torno do ombro ───────────────────────────────────────
    # Fisicamente correto: M = T(ombro) · R(θ) · T(-ombro)
    ang_asa  = -0.38 * np.sin(t)          # ±22° de batimento
    asa_rot  = rodar_em_torno(asa_pts, *OMBRO, ang_asa)
    p_asa.set_xy(asa_rot)

    # Cotovelo acompanha a asa (2º ponto da asa)
    joint_circles['Cotovelo\n(charneira·1DOF)'].center = tuple(asa_rot[1])

    # ── CAUDA: rotação em torno do joint cauda-corpo ──────────────────────────
    ang_cauda  = 0.22 * np.sin(t * 0.65)  # ±13°, ritmo mais lento
    cauda_rot  = rodar_em_torno(cauda_pts,  *CAUDA_JOINT, ang_cauda)
    fin_up_rot = rodar_em_torno(fin_up_pts, *CAUDA_JOINT, ang_cauda)
    fin_lo_rot = rodar_em_torno(fin_lo_pts, *CAUDA_JOINT, ang_cauda)
    p_cauda .set_xy(cauda_rot)
    p_fin_up.set_xy(fin_up_rot)
    p_fin_lo.set_xy(fin_lo_rot)

    # Nadadeira acompanha ponta da cauda (3º ponto)
    joint_circles['Nadadeira\n(charneira·1DOF)'].center = tuple(cauda_rot[2])

    return [p_asa, p_cauda, p_fin_up, p_fin_lo,
            *joint_circles.values()]

ani = anim.FuncAnimation(
    fig, animar,
    frames=N_FRAMES,
    interval=16,      # ~60 FPS
    blit=False,       # False = mais compatível no Windows
    repeat=True
)

# =============================================================================
# TÍTULO E LEGENDA
# =============================================================================
ax.set_title(
    'Banguela  —  Vista Lateral 2D  ·  Animação com rotação correta nos joints\n'
    'Computação Gráfica / UFF  ·  ● pontos laranjas = articulações físicas',
    color='#c8d8e0', fontsize=11, pad=10
)

legend_els = [
    LPatch(fc=C_CORPO, ec=C_BORDA, label='Corpo, pescoço, cauda'),
    LPatch(fc=C_ESCURO,ec=C_BORDA, label='Cabeça'),
    LPatch(fc=C_ASA,   ec=C_BORDA, label='Asa (anima: rotação torno do ombro)'),
    LPatch(fc=C_MEM,   ec=C_BORDA, label='Nadadeiras (animam com a cauda)'),
    LPatch(fc=C_PERNA, ec=C_BORDA, label='Pernas'),
    LPatch(fc='#00e070',ec='none', label='Olho verde — característica do Banguela'),
    mlines.Line2D([],[], marker='o', color=C_BG, markerfacecolor=C_JOINT,
                  markersize=8, label='Articulações físicas (joint type no rótulo)'),
]
ax.legend(handles=legend_els, loc='upper right',
          facecolor='#111820', edgecolor='#2a3a45',
          labelcolor='#c8d8e0', fontsize=8)

plt.tight_layout()
plt.show()
