import tkinter as tk
from tkinter import messagebox
import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import threading

# ============================================================
# CONFIGURATION
# ============================================================

actions = {
    "Thales": "HO.PA",
    "Airbus": "AIR.PA",
    "Vinci": "DG.PA"
}

couleurs = {
    "Thales": "#00ff00",
    "Airbus": "#00cc66",
    "Vinci": "#00994d"
}

FOND = "#111111"
FOND2 = "#181818"
BLANC = "#ffffff"
GRIS = "#aaaaaa"
VERT = "#00ff66"

# ============================================================
# FENÊTRE
# ============================================================

fenetre = tk.Tk()
fenetre.title("Actions - Suivi des marchés")
fenetre.geometry("1200x750")
fenetre.minsize(900, 600)
fenetre.configure(bg=FOND)

# ============================================================
# TITRE
# ============================================================

titre = tk.Label(
    fenetre,
    text="📈  ACTIONS",
    font=("Segoe UI", 26, "bold"),
    fg=VERT,
    bg=FOND
)

titre.pack(pady=(20, 0))

sous_titre = tk.Label(
    fenetre,
    text="Thales • Airbus • Vinci",
    font=("Segoe UI", 11),
    fg=GRIS,
    bg=FOND
)

sous_titre.pack(pady=(2, 15))

# ============================================================
# CADRE DU GRAPHIQUE
# ============================================================

cadre_graphique = tk.Frame(
    fenetre,
    bg=FOND2
)

cadre_graphique.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=5
)

# ============================================================
# GRAPHIQUE MATPLOTLIB
# ============================================================

plt.rcParams["font.family"] = "Segoe UI"

figure, ax = plt.subplots(
    figsize=(10, 6),
    facecolor=FOND2
)

ax.set_facecolor(FOND2)

canvas = FigureCanvasTkAgg(
    figure,
    master=cadre_graphique
)

canvas_widget = canvas.get_tk_widget()

canvas_widget.pack(
    fill="both",
    expand=True
)

# ============================================================
# BARRE DU BAS
# ============================================================

cadre_bas = tk.Frame(
    fenetre,
    bg=FOND
)

cadre_bas.pack(
    fill="x",
    padx=20,
    pady=(8, 15)
)

# ============================================================
# TEXTE DE STATUT
# ============================================================

statut = tk.Label(
    cadre_bas,
    text="Prêt à récupérer les données...",
    font=("Segoe UI", 10),
    fg=GRIS,
    bg=FOND
)

statut.pack(
    side="left"
)

# ============================================================
# BOUTON ACTUALISER
# ============================================================

bouton_actualiser = tk.Button(
    cadre_bas,
    text="⟳  Actualiser",
    font=("Segoe UI", 11, "bold"),
    fg=FOND,
    bg=VERT,
    activeforeground=FOND,
    activebackground="#00cc55",
    relief="flat",
    cursor="hand2",
    padx=20,
    pady=8
)

bouton_actualiser.pack(
    side="right"
)

# ============================================================
# RÉCUPÉRATION DES DONNÉES
# ============================================================

def recuperer_donnees():

    donnees = {}

    for nom, symbole in actions.items():

        try:

            data = yf.download(
                symbole,
                start="2026-09-01",
                auto_adjust=False,
                progress=False
            )

            donnees[nom] = data

        except Exception as erreur:

            print("Erreur pour", nom, ":", erreur)

            donnees[nom] = None

    return donnees


# ============================================================
# MISE À JOUR DE L'INTERFACE
# ============================================================

def afficher_graphique(donnees):

    ax.clear()

    ax.set_facecolor(FOND2)

    nombre_actions = 0

    for nom in actions:

        data = donnees.get(nom)

        if data is None or data.empty:
            continue

        try:

            # Récupération du cours de clôture
            cours = data["Close"]

            # Certaines versions de yfinance renvoient
            # un DataFrame au lieu d'une Series
            if hasattr(cours, "columns"):
                cours = cours.iloc[:, 0]

            ax.plot(
                data.index,
                cours,
                label=nom,
                color=couleurs[nom],
                linewidth=2.5
            )

            nombre_actions += 1

        except Exception as erreur:

            print("Erreur graphique", nom, erreur)

    # ========================================================
    # TITRE DU GRAPHIQUE
    # ========================================================

    ax.set_title(
        "Évolution des actions depuis le 1er septembre 2026",
        color=BLANC,
        fontsize=15,
        fontweight="bold",
        pad=15
    )

    # ========================================================
    # AXES
    # ========================================================

    ax.set_xlabel(
        "Date",
        color=BLANC,
        fontsize=11
    )

    ax.set_ylabel(
        "Prix (€)",
        color=BLANC,
        fontsize=11
    )

    # ========================================================
    # GRADUATIONS
    # ========================================================

    ax.tick_params(
        axis="both",
        colors=BLANC,
        labelsize=9
    )

    # ========================================================
    # GRILLE
    # ========================================================

    ax.grid(
        True,
        color="#555555",
        alpha=0.25,
        linestyle="--"
    )

    # ========================================================
    # BORDURES
    # ========================================================

    for bordure in ax.spines.values():
        bordure.set_color("#555555")

    # ========================================================
    # LÉGENDE
    # ========================================================

    if nombre_actions > 0:

        legend = ax.legend(
            loc="upper left",
            frameon=True,
            facecolor=FOND,
            edgecolor="#444444",
            fontsize=10
        )

        for texte in legend.get_texts():
            texte.set_color(BLANC)

    # ========================================================
    # DATE D'ACTUALISATION
    # ========================================================

    heure = datetime.now().strftime("%H:%M:%S")

    ax.text(
        0.99,
        0.02,
        "Dernière actualisation : " + heure,
        transform=ax.transAxes,
        color=GRIS,
        fontsize=9,
        ha="right"
    )

    figure.tight_layout()

    canvas.draw()


# ============================================================
# ACTUALISATION EN ARRIÈRE-PLAN
# ============================================================

def actualiser():

    bouton_actualiser.config(
        state="disabled",
        text="⟳  Chargement..."
    )

    statut.config(
        text="Téléchargement des données...",
        fg=GRIS
    )

    # On utilise un thread pour éviter que
    # la fenêtre se bloque pendant le téléchargement

    def telechargement():

        donnees = recuperer_donnees()

        fenetre.after(
            0,
            lambda: terminer_actualisation(donnees)
        )

    thread = threading.Thread(
        target=telechargement,
        daemon=True
    )

    thread.start()


# ============================================================
# FIN DE L'ACTUALISATION
# ============================================================

def terminer_actualisation(donnees):

    afficher_graphique(donnees)

    bouton_actualiser.config(
        state="normal",
        text="⟳  Actualiser"
    )

    heure = datetime.now().strftime("%H:%M:%S")

    statut.config(
        text=f"✓ Données mises à jour à {heure}",
        fg=VERT
    )


# ============================================================
# ACTUALISATION AUTOMATIQUE
# ============================================================

def actualisation_automatique():

    actualiser()

    # 60 secondes = 60 000 millisecondes

    fenetre.after(
        60000,
        actualisation_automatique
    )


# ============================================================
# BOUTON
# ============================================================

bouton_actualiser.config(
    command=actualiser
)

# ============================================================
# DÉMARRAGE
# ============================================================

actualiser()

fenetre.after(
    60000,
    actualisation_automatique
)

# ============================================================
# LANCEMENT
# ============================================================

fenetre.mainloop()
