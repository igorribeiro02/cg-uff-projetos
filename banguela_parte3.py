"""
==============================================================================
Banguela — PARTE 3 / Trabalho 1
Computação Gráfica / UFF  |  Aluno: Igor Ribeiro

CONCEITOS IMPLEMENTADOS (slides 33–34, Aula-Superficies-2026-1):

  ① Suavização do contorno 2D com CURVAS DE BÉZIER CÚBICAS
     Técnica: Catmull-Rom → Bézier
     Para cada segmento Pi → Pi+1 calcula:
       B0 = Pi
       B1 = Pi + (Pi+1 - Pi-1) / 6
       B2 = Pi+1 - (Pi+2 - Pi) / 6
       B3 = Pi+1
     Resultado: curva C¹-contínua que PASSA pelos pontos originais.

  ② Wire-frame 3D por LOFTING (slide 33):
     - Face frontal : contorno suavizado em z = +espessura/2
     - Face traseira: mesmo contorno em z = −espessura/2
     - Arestas laterais: segmentos ligando pontos correspondentes
     - Projeção oblíqua cavaleira (α = 30°, l = 0.45)
       x' = x + z·0.45·cos(30°)
       y' = y + z·0.45·sin(30°)

  Slider interativo controla a espessura (separação entre faces).

Execute: python banguela_parte3.py
==============================================================================
"""
import sys, io
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Polygon as MplPoly, Circle
from matplotlib.widgets import Slider

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# ===========================================================================
# 1.  ALGORITMO  Catmull-Rom → Bézier Cúbico
# ===========================================================================

def cr2bez_segments(pts, closed=True):
    """
    Converte polígono em segmentos de Bézier cúbicos (Catmull-Rom).

    Fórmula (cada segmento Pi → Pi+1):
      B0 = Pi
      B1 = Pi  + (Pi+1 - Pi-1) / 6
      B2 = Pi+1 - (Pi+2 - Pi)  / 6
      B3 = Pi+1

    closed=True  → trata os pontos como loop fechado
    closed=False → extremidades fixas (sem tangente circular)
    """
    n = len(pts)
    limit = n if closed else n - 1
    segs = []
    for i in range(limit):
        pm = pts[(i - 1) % n]
        p0 = pts[i % n]
        p1 = pts[(i + 1) % n]
        p2 = pts[(i + 2) % n]
        b0 = p0.copy()
        b1 = p0 + (p1 - pm) / 6.0
        b2 = p1 - (p2 - p0) / 6.0
        b3 = p1.copy()
        segs.append((b0, b1, b2, b3))
    return segs

def eval_cubic_bezier(b0, b1, b2, b3, n=35):
    """
    Avalia Bézier cúbico em n pontos via fórmula de Bernstein:
      B(t) = (1-t)³·B0 + 3(1-t)²t·B1 + 3(1-t)t²·B2 + t³·B3
    """
    t = np.linspace(0, 1, n, endpoint=False)
    return (np.outer((1 - t)**3,         b0) +
            np.outer(3 * (1 - t)**2 * t, b1) +
            np.outer(3 * (1 - t) * t**2, b2) +
            np.outer(t**3,               b3))

def smooth_pts(pts, closed=True, spp=35):
    """Retorna os pontos da curva Catmull-Rom suavizada."""
    segs = cr2bez_segments(pts, closed)
    chain = np.vstack([eval_cubic_bezier(*s, spp) for s in segs])
    if closed:
        chain = np.vstack([chain, chain[:1]])   # fecha o loop visualmente
    return chain

def get_ctrl_handles(pts, closed=True):
    """
    Retorna os pontos de controle INTERNOS (B1, B2) de todos os segmentos.
    Esses são os pontos invisíveis que governam a curvatura.
    """
    segs = cr2bez_segments(pts, closed)
    ctrl = []
    for b0, b1, b2, b3 in segs:
        ctrl.extend([b1, b2])
    return np.array(ctrl)

# ===========================================================================
# 2.  GEOMETRIA  (mesmos pontos do banguela_2d_atualizado.py)
# ===========================================================================

RAW = {
    'corpo':   np.array([
        [ 1.50, 0.30],[ 1.30, 0.78],[ 0.50, 0.85],
        [-0.50, 0.82],[-1.20, 0.65],[-1.50, 0.20],
        [-1.50,-0.35],[-1.20,-0.76],[ 0.00,-0.80],
        [ 1.20,-0.68],[ 1.50,-0.30]]),
    'cabeca':  np.array([
        [2.30, 0.50],[2.60, 0.70],[3.10, 0.68],[3.40, 0.52],
        [3.50, 0.15],[3.50,-0.05],[3.20,-0.28],[2.80,-0.30],[2.30,-0.10]]),
    'pescoco': np.array([
        [1.50, 0.30],[2.30, 0.50],[2.30,-0.10],[1.50,-0.30]]),
    'asa':     np.array([
        [ 0.50, 0.80],[ 0.28, 1.82],[-0.48, 2.55],[-1.05, 0.83]]),
    'cauda':   np.array([
        [-1.50, 0.20],[-2.50, 0.14],[-3.50, 0.00],
        [-2.50,-0.20],[-1.50,-0.35]]),
    'fin_up':  np.array([[-3.50, 0.00],[-3.10, 0.55],[-3.78, 0.40]]),
    'fin_lo':  np.array([[-3.50, 0.00],[-3.12,-0.35],[-3.78,-0.22]]),
}

RECT = {                          # pernas — retângulos, sem suavização
    'perna_r': np.array([[-1.18,-0.74],[-1.18,-1.78],[-0.82,-1.78],[-0.82,-0.74]]),
    'pe_r':    np.array([[-1.38,-1.78],[-1.38,-1.95],[-0.62,-1.95],[-0.62,-1.78]]),
    'perna_f': np.array([[ 0.85,-0.74],[ 0.85,-1.78],[ 1.18,-1.78],[ 1.18,-0.74]]),
    'pe_f':    np.array([[ 0.68,-1.78],[ 0.68,-1.95],[ 1.38,-1.95],[ 1.38,-1.78]]),
}

# Pré-computa curvas suavizadas
SM = {k: smooth_pts(v, closed=True, spp=35) for k, v in RAW.items()}

# Cores (fc, ec)
CLR = {
    'corpo':   ('#1e2830','#4a6070'),
    'cabeca':  ('#181e22','#4a6070'),
    'pescoco': ('#1e2830','#4a6070'),
    'asa':     ('#243040','#4a6070'),
    'cauda':   ('#1e2830','#4a6070'),
    'fin_up':  ('#2c3a4a','#4a6070'),
    'fin_lo':  ('#2c3a4a','#4a6070'),
    'perna_r': ('#1c2430','#4a6070'),
    'pe_r':    ('#1c2430','#4a6070'),
    'perna_f': ('#1c2430','#4a6070'),
    'pe_f':    ('#1c2430','#4a6070'),
}

DRAW_ORDER  = ['perna_r','pe_r','asa','corpo','pescoco','cauda','fin_up','fin_lo','cabeca','perna_f','pe_f']
CURVE_NAMES = list(RAW.keys())    # partes que recebem suavização

C_BG    = '#0b0f14'
C_CTRL  = '#FF6B2B'   # pontos de controle originais (nós)
C_HDLS  = '#FFB060'   # handles internos (B1, B2)
C_CURVE = '#6ec6f0'   # curva Bézier suavizada
C_WFRT  = '#6ec6f0'   # wire-frame face frontal
C_WBCK  = '#1a3050'   # wire-frame face traseira
C_WLFT  = '#2a4060'   # wire-frame arestas de lofting

# ===========================================================================
# 3.  PROJEÇÃO OBLÍQUA CAVALEIRA
# ===========================================================================

def cavalier(pts2d, z_val, ang_deg=30, sc=0.45):
    """
    Projeção oblíqua cavaleira (preserva dimensões frontais exatas).
      x' = x + z · sc · cos(α)
      y' = y + z · sc · sin(α)
    """
    ang = np.radians(ang_deg)
    xs = pts2d[:, 0] + z_val * sc * np.cos(ang)
    ys = pts2d[:, 1] + z_val * sc * np.sin(ang)
    return np.column_stack([xs, ys])

# ===========================================================================
# 4.  FUNÇÕES DE DESENHO
# ===========================================================================

def _eye(ax, z_proj=None, ang_deg=30, sc=0.45, zo=8):
    """Olho verde do Banguela (pode ser projetado para z-offset)."""
    cx, cy, r1, r2, r3 = 3.08, 0.34, 0.13, 0.09, 0.05
    if z_proj is not None:
        ang = np.radians(ang_deg)
        cx = cx + z_proj * sc * np.cos(ang)
        cy = cy + z_proj * sc * np.sin(ang)
    ax.add_patch(Circle((cx,      cy),      r1, fc='white',   ec='none', zorder=zo))
    ax.add_patch(Circle((cx,      cy),      r2, fc='#00e070', ec='none', zorder=zo+1))
    ax.add_patch(Circle((cx+0.02, cy),      r3, fc='#001a0a', ec='none', zorder=zo+2))


def draw_original(ax):
    """Painel 1 — figura original com polígonos retos."""
    ax.set_xlim(-4.5, 4.5)
    ax.set_ylim(-2.5, 3.5)
    for z, name in enumerate(DRAW_ORDER, start=1):
        pts = RAW.get(name, RECT.get(name))
        fc, ec = CLR[name]
        ax.add_patch(MplPoly(pts, closed=True, fc=fc, ec=ec, lw=0.9, zorder=z))
    _eye(ax, zo=20)


def draw_smooth(ax, show_handles=True):
    """
    Painel 2 — suavizado com Bézier + visualização dos pontos de controle.

    Pontos laranjas (●) = nós originais (o que você digitou — a curva PASSA por eles)
    Pontos amarelados (◆) = handles internos B1, B2 (governam a curvatura)
    Linha azul = curva de Bézier resultante
    """
    ax.set_xlim(-4.5, 4.5)
    ax.set_ylim(-2.5, 3.5)

    for z, name in enumerate(DRAW_ORDER, start=1):
        fc, ec = CLR[name]
        if name in SM:
            pts_smooth = SM[name]
            ax.add_patch(MplPoly(pts_smooth, closed=False,
                                 fc=fc, ec='none', lw=0, zorder=z))
            ax.plot(pts_smooth[:, 0], pts_smooth[:, 1],
                    color=C_CURVE, lw=1.1, alpha=0.9, zorder=z + 100)
            if show_handles:
                raw = RAW[name]
                # handles internos — linhas tracejadas
                hdls = get_ctrl_handles(raw, closed=True)
                segs = cr2bez_segments(raw, closed=True)
                for b0, b1, b2, b3 in segs:
                    ax.plot([b0[0], b1[0]], [b0[1], b1[1]],
                            color=C_HDLS, lw=0.5, alpha=0.55,
                            linestyle='--', zorder=z+101)
                    ax.plot([b3[0], b2[0]], [b3[1], b2[1]],
                            color=C_HDLS, lw=0.5, alpha=0.55,
                            linestyle='--', zorder=z+101)
                # nós de interpolação
                ax.scatter(raw[:, 0], raw[:, 1],
                           color=C_CTRL, s=28, zorder=z+102,
                           edgecolors='white', linewidths=0.5)
                # handles
                ax.scatter(hdls[:, 0], hdls[:, 1],
                           color=C_HDLS, s=14, marker='D', zorder=z+102,
                           edgecolors='none', alpha=0.8)
        else:
            pts = RECT[name]
            ax.add_patch(MplPoly(pts, closed=True,
                                 fc=fc, ec=ec, lw=0.9, zorder=z))
    _eye(ax, zo=200)


def draw_wireframe(ax, thickness=1.0):
    """
    Painel 3 — Wire-frame 3D por lofting (slide 33).

    Lofting: para cada parte:
      1. Projeta o contorno suavizado na face frontal (z = +e/2)
      2. Projeta o contorno suavizado na face traseira (z = −e/2)
      3. Conecta pontos correspondentes com arestas laterais
    """
    ax.cla()
    ax.set_facecolor(C_BG)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('(3) Wire-frame 3D — Lofting\n'
                 'projeção oblíqua cavaleira 30°  ·  '
                 f'espessura = {thickness:.2f} u',
                 color='#c8d8e0', fontsize=10)
    ax.set_xlim(-4.5, 5.5)
    ax.set_ylim(-2.5, 4.0)

    zf = +thickness / 2
    zb = -thickness / 2

    # Todas as partes: curvas suavizadas + retas
    all_parts = {}
    for k, v in SM.items():
        all_parts[k] = v[:-1]          # sem ponto duplo de fechamento
    for k, v in RECT.items():
        all_parts[k] = v

    # ── Arestas de lofting (desenhadas primeiro — ficam "atrás") ──────────
    for name in DRAW_ORDER:
        pts2d = all_parts[name]
        n = len(pts2d)
        n_edges = min(18, n)
        idx = np.round(np.linspace(0, n - 1, n_edges)).astype(int)

        pf = cavalier(pts2d[idx], zf)
        pb = cavalier(pts2d[idx], zb)

        for i in range(len(idx)):
            ax.plot([pb[i, 0], pf[i, 0]], [pb[i, 1], pf[i, 1]],
                    color=C_WLFT, lw=0.55, alpha=0.65, zorder=2)

    # ── Face traseira ─────────────────────────────────────────────────────
    for name in DRAW_ORDER:
        pts2d = np.vstack([all_parts[name], all_parts[name][:1]])  # fechar
        pb = cavalier(pts2d, zb)
        ax.plot(pb[:, 0], pb[:, 1],
                color=C_WBCK, lw=1.2, alpha=0.9, zorder=3)

    # ── Face frontal (desenhada por cima) ─────────────────────────────────
    for name in DRAW_ORDER:
        pts2d = np.vstack([all_parts[name], all_parts[name][:1]])
        pf = cavalier(pts2d, zf)
        ax.plot(pf[:, 0], pf[:, 1],
                color=C_WFRT, lw=1.5, alpha=0.97, zorder=4)

    # Olho na face frontal
    _eye(ax, z_proj=zf, zo=5)

    # Anotações das faces
    ang = np.radians(30)
    xf_lbl = -4.0 + zf * 0.45 * np.cos(ang)
    yf_lbl = -2.0 + zf * 0.45 * np.sin(ang)
    xb_lbl = -4.0 + zb * 0.45 * np.cos(ang)
    yb_lbl = -2.0 + zb * 0.45 * np.sin(ang)
    ax.annotate('face frontal\n(z = +{:.2f})'.format(zf),
                (xf_lbl, yf_lbl), color=C_WFRT, fontsize=7,
                ha='left', va='top', zorder=10)
    ax.annotate('face traseira\n(z = −{:.2f})'.format(abs(zb)),
                (xb_lbl, yb_lbl), color='#5080b0', fontsize=7,
                ha='left', va='bottom', zorder=10)


# ===========================================================================
# 5.  FIGURA PRINCIPAL
# ===========================================================================

fig = plt.figure(figsize=(21, 10), facecolor=C_BG)
fig.patch.set_facecolor(C_BG)

# Layout: 3 painéis de visualização + 1 linha para slider
gs = fig.add_gridspec(2, 3,
                      left=0.01, right=0.99,
                      top=0.91, bottom=0.13,
                      hspace=0.05, wspace=0.04,
                      height_ratios=[1, 0.001])

ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1])
ax3 = fig.add_subplot(gs[0, 2])

for ax in [ax1, ax2, ax3]:
    ax.set_facecolor(C_BG)
    ax.set_aspect('equal')
    ax.axis('off')

ax1.set_title('(1) Original — polígonos retos\n(como estava na Parte 1)',
              color='#c8d8e0', fontsize=10)
ax2.set_title('(2) Suavizado — Bézier Cúbico (Catmull-Rom)\n'
              '● laranjas = nós interpolados  ◆ amarelos = handles de curvatura',
              color='#c8d8e0', fontsize=10)
ax3.set_title('(3) Wire-frame 3D — Lofting\n'
              'projeção oblíqua cavaleira 30°  ·  espessura = 1.00 u',
              color='#c8d8e0', fontsize=10)

draw_original(ax1)
draw_smooth(ax2, show_handles=True)
draw_wireframe(ax3, thickness=1.0)

# ── Slider de espessura (separação entre faces) ────────────────────────────
ax_sl = fig.add_axes([0.32, 0.05, 0.36, 0.025], facecolor='#1a2430')
slider = Slider(ax_sl, 'Espessura (u)  —  slide para ajustar',
                0.05, 3.0, valinit=1.0, color='#3a7090')
slider.label.set_color('#c8d8e0')
slider.valtext.set_color('#6ec6f0')

def on_slide(val):
    draw_wireframe(ax3, slider.val)
    fig.canvas.draw_idle()

slider.on_changed(on_slide)

# ── Legenda ────────────────────────────────────────────────────────────────
legend_els = [
    mpatches.Patch(color=C_CTRL,  label='Nós de interpolação (curva PASSA aqui)'),
    mpatches.Patch(color=C_HDLS,  label='Handles internos B₁/B₂ (controlam curvatura)'),
    mpatches.Patch(color=C_CURVE, label='Curva de Bézier cúbica resultante (C¹)'),
    mpatches.Patch(color=C_WFRT,  label='Face frontal  (z = +e/2)'),
    mpatches.Patch(color='#5080b0', label='Face traseira (z = −e/2)'),
    mpatches.Patch(color=C_WLFT,  label='Arestas de lofting (segmentos conectores)'),
]
fig.legend(handles=legend_els, loc='lower center', ncol=3,
           facecolor='#111820', edgecolor='#2a3a45',
           labelcolor='#c8d8e0', fontsize=8.5,
           bbox_to_anchor=(0.5, 0.085))

# ── Título ─────────────────────────────────────────────────────────────────
fig.suptitle(
    'Banguela — Trabalho 1 / Parte 3  ·  '
    'Suavização com Bézier Cúbico + Wire-frame 3D por Lofting\n'
    'Catmull-Rom → Bézier:  B0=Pi,  B1=Pi+(Pi₊₁−Pi₋₁)/6,  '
    'B2=Pi₊₁−(Pi₊₂−Pi)/6,  B3=Pi₊₁   |   '
    'Cavaleira: x\'=x+z·0.45·cos 30°,  y\'=y+z·0.45·sin 30°',
    color='#c8d8e0', fontsize=10, y=0.975
)

plt.show()
