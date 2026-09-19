import tkinter as tk
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import threading
import numpy as np


# ============================================================
# CONFIGURATION
# ============================================================

NOM_APPLICATION = "CacVision"


actions_cac40 = {
    "Accor": "AC.PA",
    "Air Liquide": "AI.PA",
    "Airbus": "AIR.PA",
    "ArcelorMittal": "MT.PA",
    "AXA": "CS.PA",
    "BNP Paribas": "BNP.PA",
    "Bouygues": "EN.PA",
    "Bureau Veritas": "BVI.PA",
    "Capgemini": "CAP.PA",
    "Carrefour": "CA.PA",
    "Crédit Agricole": "ACA.PA",
    "Danone": "BN.PA",
    "Dassault Systèmes": "DSY.PA",
    "Eiffage": "FGR.PA",
    "Engie": "ENGI.PA",
    "EssilorLuxottica": "EL.PA",
    "Eurofins Scientific": "ERF.PA",
    "Euronext": "ENX.PA",
    "Hermès": "RMS.PA",
    "Kering": "KER.PA",
    "L'Oréal": "OR.PA",
    "Legrand": "LR.PA",
    "LVMH": "MC.PA",
    "Michelin": "ML.PA",
    "Orange": "ORA.PA",
    "Pernod Ricard": "RI.PA",
    "Publicis": "PUB.PA",
    "Renault": "RNO.PA",
    "Safran": "SAF.PA",
    "Saint-Gobain": "SGO.PA",
    "Sanofi": "SAN.PA",
    "Schneider Electric": "SU.PA",
    "Société Générale": "GLE.PA",
    "Stellantis": "STLAM.PA",
    "STMicroelectronics": "STM.PA",
    "Thales": "HO.PA",
    "TotalEnergies": "TTE.PA",
    "Unibail-Rodamco-Westfield": "URW.PA",
    "Veolia": "VIE.PA",
    "Vinci": "DG.PA"
}


actions_selectionnees = {
    "Thales",
    "Airbus",
    "Vinci"
}


periodes = {
    "24 h": {
        "period": "5d",
        "interval": "5m"
    },

    "1 semaine": {
        "period": "1mo",
        "interval": "15m"
    },

    "1 mois": {
        "period": "1mo",
        "interval": "1h"
    },

    "1 an": {
        "period": "1y",
        "interval": "1d"
    },

    "Depuis toujours": {
        "period": "max",
        "interval": "1d"
    }
}


periode_actuelle = "24 h"


# ============================================================
# THÈMES
# ============================================================

THEME_SOMBRE = {
    "fond_haut": "#080b12",
    "fond_bas": "#101722",

    "panneau": "#151d2a",
    "panneau2": "#192333",

    "verre": "#202c3d",
    "verre_hover": "#2b3b50",

    "bordure": "#34445a",

    "texte": "#f5f7fb",
    "texte_secondaire": "#9ba8bb",

    "accent": "#4ade80",
    "accent2": "#38bdf8",

    "grille": "#516070",

    "ombre": "#05070b"
}


THEME_CLAIR = {
    "fond_haut": "#e9eef5",
    "fond_bas": "#f7f9fc",

    "panneau": "#ffffff",
    "panneau2": "#f1f4f8",

    "verre": "#edf2f7",
    "verre_hover": "#e3eaf2",

    "bordure": "#d3dbe6",

    "texte": "#172033",
    "texte_secondaire": "#687589",

    "accent": "#159957",
    "accent2": "#1689c7",

    "grille": "#aeb9c7",

    "ombre": "#c9d1dc"
}


theme_sombre = True
theme = THEME_SOMBRE


# ============================================================
# COULEURS DES COURBES
# ============================================================

COULEURS_COURBES = [
    "#55E6A5",
    "#52BFFF",
    "#B58CFF",
    "#FFB86B",
    "#FF6B8A",
    "#6EE7F9",
    "#A3E635",
    "#F59EEC",
    "#FFD166",
    "#7DD3FC",
    "#FF4D6D",
    "#00D1B2",
    "#8A7CFF",
    "#F97316",
    "#22C55E",
    "#EC4899",
    "#06B6D4",
    "#EAB308",
    "#84CC16",
    "#14B8A6",
    "#F43F5E",
    "#6366F1",
    "#10B981",
    "#F59E0B",
    "#D946EF",
    "#0EA5E9",
    "#65A30D",
    "#FB7185",
    "#2DD4BF",
    "#A855F7",
    "#38BDF8",
    "#4ADE80",
    "#FACC15",
    "#C084FC",
    "#34D399",
    "#FB923C",
    "#60A5FA",
    "#F472B6",
    "#2DD4BF",
    "#818CF8"
]


couleurs_actions = {}


# ============================================================
# DONNÉES
# ============================================================

donnees_actuelles = {}
lignes = {}
annotations = []


# ============================================================
# FENÊTRE
# ============================================================

fenetre = tk.Tk()

fenetre.title(NOM_APPLICATION)

fenetre.geometry("1800x1000")

fenetre.minsize(
    1200,
    760
)


# ============================================================
# FOND
# ============================================================

fond = tk.Canvas(
    fenetre,
    highlightthickness=0,
    bd=0,
    bg=theme["fond_bas"]
)

fond.pack(
    fill="both",
    expand=True
)


def dessiner_degrade():

    fond.delete("degrade")

    largeur = fond.winfo_width()
    hauteur = fond.winfo_height()

    if largeur <= 1 or hauteur <= 1:
        return

    if theme_sombre:

        couleur_haut = (8, 11, 18)
        couleur_bas = (16, 23, 34)

    else:

        couleur_haut = (233, 238, 245)
        couleur_bas = (247, 249, 252)

    nombre_lignes = max(
        100,
        min(300, hauteur)
    )

    for i in range(nombre_lignes):

        ratio = i / (nombre_lignes - 1)

        r = int(
            couleur_haut[0]
            +
            (couleur_bas[0] - couleur_haut[0]) * ratio
        )

        g = int(
            couleur_haut[1]
            +
            (couleur_bas[1] - couleur_haut[1]) * ratio
        )

        b = int(
            couleur_haut[2]
            +
            (couleur_bas[2] - couleur_haut[2]) * ratio
        )

        couleur = (
            f"#{r:02x}"
            f"{g:02x}"
            f"{b:02x}"
        )

        y1 = int(
            hauteur * i / nombre_lignes
        )

        y2 = int(
            hauteur * (i + 1) / nombre_lignes
        )

        fond.create_rectangle(
            0,
            y1,
            largeur,
            y2 + 1,
            fill=couleur,
            outline="",
            tags="degrade"
        )


# ============================================================
# CONTENEUR
# ============================================================

conteneur = tk.Frame(
    fond,
    bd=0,
    bg=theme["fond_bas"]
)

conteneur.place(
    relx=0.5,
    rely=0.5,
    relwidth=0.96,
    relheight=0.96,
    anchor="center"
)


# ============================================================
# EN-TÊTE
# ============================================================

entete = tk.Frame(
    conteneur,
    bd=0,
    bg=theme["fond_bas"]
)

entete.pack(
    fill="x",
    pady=(18, 12)
)


bloc_titre = tk.Frame(
    entete,
    bd=0,
    bg=theme["fond_bas"]
)

bloc_titre.pack(
    side="left"
)


titre = tk.Label(
    bloc_titre,
    text="CacVision",
    font=(
        "Segoe UI",
        32,
        "bold"
    ),
    bd=0,
    bg=theme["fond_bas"],
    fg=theme["texte"]
)

titre.pack(
    anchor="w"
)


sous_titre = tk.Label(
    bloc_titre,
    text="Suivi détaillé des valeurs du CAC 40",
    font=(
        "Segoe UI",
        12
    ),
    bd=0,
    bg=theme["fond_bas"],
    fg=theme["texte_secondaire"]
)

sous_titre.pack(
    anchor="w",
    pady=(1, 0)
)


# ============================================================
# LIVE
# ============================================================

bloc_live = tk.Frame(
    entete,
    bd=0,
    bg=theme["fond_bas"]
)

bloc_live.pack(
    side="right",
    padx=10
)


point_live = tk.Canvas(
    bloc_live,
    width=12,
    height=12,
    highlightthickness=0,
    bd=0,
    bg=theme["fond_bas"]
)

point_live.pack(
    side="left",
    padx=(0, 7)
)


point_live.create_oval(
    2,
    2,
    10,
    10,
    fill="#4ade80",
    outline=""
)


label_live = tk.Label(
    bloc_live,
    text="DONNÉES EN DIRECT",
    font=(
        "Segoe UI",
        9,
        "bold"
    ),
    bd=0,
    bg=theme["fond_bas"],
    fg=theme["texte_secondaire"]
)

label_live.pack(
    side="left"
)


# ============================================================
# BARRE DE CONTRÔLES
# ============================================================

barre_controles = tk.Frame(
    conteneur,
    bd=0,
    bg=theme["fond_bas"]
)

barre_controles.pack(
    fill="x",
    pady=(0, 15)
)


# ============================================================
# PILULE
# ============================================================

def dessiner_pilule(
    canvas,
    largeur,
    hauteur,
    couleur,
    bordure=None
):

    canvas.delete("pilule")

    rayon = hauteur / 2

    canvas.create_rectangle(
        rayon,
        1,
        largeur - rayon,
        hauteur - 1,
        fill=couleur,
        outline="",
        tags="pilule"
    )

    canvas.create_oval(
        1,
        1,
        hauteur - 1,
        hauteur - 1,
        fill=couleur,
        outline="",
        tags="pilule"
    )

    canvas.create_oval(
        largeur - hauteur + 1,
        1,
        largeur - 1,
        hauteur - 1,
        fill=couleur,
        outline="",
        tags="pilule"
    )

    if bordure:

        canvas.create_line(
            rayon,
            1,
            largeur - rayon,
            1,
            fill=bordure,
            width=1,
            tags="pilule"
        )

    # Très important :
    # la pilule reste derrière le texte
    canvas.tag_lower("pilule")


# ============================================================
# BOUTON VERRE
# ============================================================

def creer_bouton_verre(
    parent,
    texte,
    commande,
    largeur=170,
    hauteur=46
):

    bouton = tk.Canvas(
        parent,
        width=largeur,
        height=hauteur,
        highlightthickness=0,
        bd=0,
        cursor="hand2",
        bg=theme["fond_bas"]
    )

    def obtenir_couleur_verre():

        # On garde un effet "verre"
        # en mélangeant légèrement le panneau
        # avec le fond.
        if theme_sombre:

            return "#1d2838"

        return "#f0f4f9"

    def normal():

        bouton.configure(
            bg=theme["fond_bas"]
        )

        dessiner_pilule(
            bouton,
            largeur,
            hauteur,
            obtenir_couleur_verre(),
            theme["bordure"]
        )

        bouton.itemconfig(
            texte_id,
            fill=theme["texte"]
        )

        bouton.tag_raise(
            texte_id
        )

    def hover():

        bouton.configure(
            bg=theme["fond_bas"]
        )

        dessiner_pilule(
            bouton,
            largeur,
            hauteur,
            theme["verre_hover"],
            theme["accent2"]
        )

        bouton.itemconfig(
            texte_id,
            fill=theme["texte"]
        )

        bouton.tag_raise(
            texte_id
        )

    # Le texte est créé AVANT le dessin de la pilule
    texte_id = bouton.create_text(
        largeur / 2,
        hauteur / 2,
        text=texte,
        fill=theme["texte"],
        font=(
            "Segoe UI",
            10,
            "bold"
        )
    )

    normal()

    bouton.bind(
        "<Enter>",
        lambda event: hover()
    )

    bouton.bind(
        "<Leave>",
        lambda event: normal()
    )

    bouton.bind(
        "<Button-1>",
        lambda event: commande()
    )

    bouton.texte_id = texte_id
    bouton.normal = normal
    bouton.hover = hover

    return bouton


# ============================================================
# BOUTON ACTIONS
# ============================================================

bouton_actions = creer_bouton_verre(
    barre_controles,
    "☰   Actions",
    lambda: ouvrir_selection_actions(),
    175,
    48
)

bouton_actions.pack(
    side="left",
    padx=(0, 10)
)


# ============================================================
# PÉRIODE
# ============================================================

label_periode = tk.Label(
    barre_controles,
    text="Période",
    font=(
        "Segoe UI",
        10,
        "bold"
    ),
    bd=0,
    bg=theme["fond_bas"],
    fg=theme["texte_secondaire"]
)

label_periode.pack(
    side="left",
    padx=(12, 8)
)


bouton_periode = tk.Canvas(
    barre_controles,
    width=190,
    height=48,
    highlightthickness=0,
    bd=0,
    cursor="hand2",
    bg=theme["fond_bas"]
)

bouton_periode.pack(
    side="left"
)


texte_periode = bouton_periode.create_text(
    95,
    24,
    text="24 h     ▾",
    fill=theme["texte"],
    font=(
        "Segoe UI",
        10,
        "bold"
    )
)


def dessiner_bouton_periode():

    bouton_periode.configure(
        bg=theme["fond_bas"]
    )

    dessiner_pilule(
        bouton_periode,
        190,
        48,
        "#1d2838" if theme_sombre else "#f0f4f9",
        theme["bordure"]
    )

    bouton_periode.itemconfig(
        texte_periode,
        fill=theme["texte"]
    )

    bouton_periode.tag_raise(
        texte_periode
    )


dessiner_bouton_periode()


menu_periode = None


def ouvrir_menu_periode():

    global menu_periode

    if menu_periode is not None:

        try:
            menu_periode.destroy()
        except:
            pass

    menu_periode = tk.Toplevel(
        fenetre
    )

    menu_periode.overrideredirect(True)

    menu_periode.configure(
        bg=theme["bordure"]
    )

    x = bouton_periode.winfo_rootx()

    y = (
        bouton_periode.winfo_rooty()
        +
        bouton_periode.winfo_height()
        +
        7
    )

    menu_periode.geometry(
        f"220x270+{x}+{y}"
    )

    panneau = tk.Frame(
        menu_periode,
        bg=theme["panneau"],
        bd=0
    )

    panneau.pack(
        fill="both",
        expand=True,
        padx=1,
        pady=1
    )

    for periode in periodes:

        bouton = tk.Button(
            panneau,
            text=periode,
            font=(
                "Segoe UI",
                10,
                "bold"
            ),
            bg=theme["panneau"],
            fg=theme["texte"],
            activebackground=theme["verre_hover"],
            activeforeground=theme["texte"],
            relief="flat",
            bd=0,
            cursor="hand2",
            anchor="w",
            padx=18,
            pady=9,
            command=lambda p=periode:
                choisir_periode(p)
        )

        bouton.pack(
            fill="x"
        )

    menu_periode.focus_force()


def choisir_periode(periode):

    global periode_actuelle

    periode_actuelle = periode

    bouton_periode.itemconfig(
        texte_periode,
        text=f"{periode}     ▾"
    )

    fermer_menu_periode()

    actualiser()


def fermer_menu_periode():

    global menu_periode

    if menu_periode is not None:

        try:
            menu_periode.destroy()
        except:
            pass

        menu_periode = None


bouton_periode.bind(
    "<Button-1>",
    lambda event: ouvrir_menu_periode()
)


bouton_periode.bind(
    "<Enter>",
    lambda event: (
        dessiner_pilule(
            bouton_periode,
            190,
            48,
            theme["verre_hover"],
            theme["accent2"]
        ),
        bouton_periode.tag_raise(
            texte_periode
        )
    )
)


bouton_periode.bind(
    "<Leave>",
    lambda event:
        dessiner_bouton_periode()
)


# ============================================================
# BOUTON RAFRAÎCHIR
# ============================================================

bouton_rafraichir = creer_bouton_verre(
    barre_controles,
    "↻   Rafraîchir",
    lambda: actualiser(),
    160,
    48
)

bouton_rafraichir.pack(
    side="left",
    padx=(12, 0)
)


# ============================================================
# ESPACE
# ============================================================

tk.Frame(
    barre_controles,
    bg=theme["fond_bas"]
).pack(
    side="left",
    expand=True
)


# ============================================================
# BOUTON THÈME
# ============================================================

bouton_theme = creer_bouton_verre(
    barre_controles,
    "☀   Clair",
    lambda: changer_theme(),
    145,
    48
)

bouton_theme.pack(
    side="right",
    padx=(10, 0)
)


# ============================================================
# PANNEAU GRAPHIQUE
# ============================================================

cadre_graphique = tk.Frame(
    conteneur,
    bd=0,
    highlightthickness=1,
    bg=theme["bordure"],
    highlightbackground=theme["bordure"]
)

cadre_graphique.pack(
    fill="both",
    expand=True
)


# ============================================================
# FIGURE
# ============================================================

figure = plt.figure(
    figsize=(17, 9.4),
    dpi=180
)

ax = figure.add_subplot(
    111
)

legende_ax = None


canvas_graphique = FigureCanvasTkAgg(
    figure,
    master=cadre_graphique
)

widget_graphique = canvas_graphique.get_tk_widget()

widget_graphique.pack(
    fill="both",
    expand=True,
    padx=1,
    pady=1
)


# ============================================================
# BARRE INFÉRIEURE
# ============================================================

barre_bas = tk.Frame(
    conteneur,
    bd=0,
    bg=theme["fond_bas"]
)

barre_bas.pack(
    fill="x",
    pady=(12, 4)
)


statut = tk.Label(
    barre_bas,
    text="Initialisation...",
    font=(
        "Segoe UI",
        10
    ),
    bd=0,
    bg=theme["fond_bas"],
    fg=theme["texte_secondaire"]
)

statut.pack(
    side="left"
)


# ============================================================
# ORDRE ACTIONS
# ============================================================

def obtenir_ordre_actions():

    return [
        nom
        for nom in actions_cac40
        if nom in actions_selectionnees
    ]


# ============================================================
# COULEURS ACTIONS
# ============================================================

def generer_couleurs_actions():

    global couleurs_actions

    couleurs_actions = {}

    noms = obtenir_ordre_actions()

    for i, nom in enumerate(noms):

        couleurs_actions[nom] = (
            COULEURS_COURBES[
                i % len(COULEURS_COURBES)
            ]
        )


# ============================================================
# AFFICHAGE GRAPHIQUE
# ============================================================

def afficher_graphique(donnees):

    global donnees_actuelles
    global lignes
    global annotations
    global couleurs_actions
    global ax
    global legende_ax

    donnees_actuelles = donnees

    # ========================================================
    # NETTOYAGE
    # ========================================================

    for annotation in annotations:

        try:
            annotation.remove()
        except:
            pass

    annotations = []
    lignes = {}

    noms_actions = obtenir_ordre_actions()

    # ========================================================
    # NOMBRE D'ACTIONS
    # ========================================================

    nombre_selectionne = len(
        noms_actions
    )

    # ========================================================
    # CONFIGURATION LÉGENDE
    # ========================================================

    if nombre_selectionne <= 4:

        colonnes = max(
            1,
            nombre_selectionne
        )

        taille_texte = 9

    elif nombre_selectionne <= 10:

        colonnes = 5
        taille_texte = 8

    elif nombre_selectionne <= 20:

        colonnes = 5
        taille_texte = 7.5

    elif nombre_selectionne <= 30:

        colonnes = 5
        taille_texte = 7

    else:

        # 40 actions
        colonnes = 5
        taille_texte = 6.5

    lignes_legende = max(
        1,
        int(
            np.ceil(
                max(
                    1,
                    nombre_selectionne
                )
                / colonnes
            )
        )
    )

    # ========================================================
    # HAUTEUR ZONE LÉGENDE
    # ========================================================

    hauteur_legende = (
        0.10
        +
        lignes_legende * 0.028
    )

    hauteur_legende = max(
        0.14,
        min(
            0.40,
            hauteur_legende
        )
    )

    # ========================================================
    # RECRÉATION DE LA FIGURE
    # ========================================================

    figure.clear()

    grille = figure.add_gridspec(
        2,
        1,
        height_ratios=[
            hauteur_legende,
            1 - hauteur_legende
        ],
        hspace=0.015
    )

    # ========================================================
    # ZONE LÉGENDE
    # ========================================================

    legende_ax = figure.add_subplot(
        grille[0]
    )

    legende_ax.set_facecolor(
        theme["panneau"]
    )

    legende_ax.axis(
        "off"
    )

    # ========================================================
    # ZONE GRAPHIQUE
    # ========================================================

    ax = figure.add_subplot(
        grille[1]
    )

    ax.set_facecolor(
        theme["panneau"]
    )

    figure.patch.set_facecolor(
        theme["panneau"]
    )

    # ========================================================
    # COULEURS
    # ========================================================

    generer_couleurs_actions()

    # ========================================================
    # COURBES
    # ========================================================

    for nom in noms_actions:

        data = donnees.get(
            nom
        )

        if data is None:
            continue

        if data.empty:
            continue

        try:

            cours = data["Close"]

            if hasattr(
                cours,
                "columns"
            ):

                cours = cours.iloc[:, 0]

            cours = cours.dropna()

            if len(cours) < 2:
                continue

            dates = cours.index

            valeurs = np.asarray(
                cours.values,
                dtype=float
            )

            couleur = couleurs_actions[
                nom
            ]

            ligne, = ax.plot(
                dates,
                valeurs,
                color=couleur,
                linewidth=1.45,
                alpha=0.95,
                solid_capstyle="round",
                solid_joinstyle="round",
                antialiased=True,
                picker=7,
                label=nom
            )

            # Halo discret
            ax.plot(
                dates,
                valeurs,
                color=couleur,
                linewidth=4,
                alpha=0.025,
                solid_capstyle="round",
                antialiased=True
            )

            # Points
            if len(dates) < 250:

                ax.scatter(
                    dates,
                    valeurs,
                    color=couleur,
                    s=5,
                    alpha=0.4,
                    linewidths=0
                )

            lignes[nom] = {
                "ligne": ligne,
                "dates": dates,
                "valeurs": valeurs
            }

        except Exception as erreur:

            print(
                "Erreur graphique :",
                erreur
            )

    # ========================================================
    # TITRE
    # ========================================================

    legende_ax.text(
        0.01,
        0.92,
        periode_actuelle,
        transform=legende_ax.transAxes,
        ha="left",
        va="top",
        color=theme["texte"],
        fontsize=15,
        fontweight="bold"
    )

    # ========================================================
    # LÉGENDE
    # ========================================================

    if lignes:

        handles, labels = (
            ax.get_legend_handles_labels()
        )

        legende = legende_ax.legend(
            handles,
            labels,
            loc="center",
            ncol=colonnes,
            frameon=False,
            fontsize=taille_texte,
            handlelength=1.8,
            handletextpad=0.4,
            columnspacing=1.3,
            labelspacing=0.45,
            borderaxespad=0
        )

        for texte in legende.get_texts():

            texte.set_color(
                theme["texte"]
            )

    # ========================================================
    # AXES
    # ========================================================

    ax.set_xlabel("")

    ax.set_ylabel(
        "Cours (€)",
        color=theme["texte_secondaire"],
        fontsize=10,
        labelpad=8
    )

    # ========================================================
    # DATES
    # ========================================================

    locator = mdates.AutoDateLocator(
        minticks=6,
        maxticks=9
    )

    formatter = mdates.ConciseDateFormatter(
        locator
    )

    formatter.offset_formats = [
        "",
        "%Y",
        "%b %Y",
        "%d %b",
        "%H:%M",
        "%H:%M:%S"
    ]

    ax.xaxis.set_major_locator(
        locator
    )

    ax.xaxis.set_major_formatter(
        formatter
    )

    # ========================================================
    # GRILLE
    # ========================================================

    ax.grid(
        True,
        which="major",
        color=theme["grille"],
        alpha=0.13,
        linewidth=0.65
    )

    ax.grid(
        True,
        which="minor",
        color=theme["grille"],
        alpha=0.04,
        linewidth=0.4
    )

    ax.minorticks_on()

    # ========================================================
    # TICKS
    # ========================================================

    ax.tick_params(
        axis="x",
        colors=theme["texte_secondaire"],
        labelsize=8,
        length=0,
        pad=8
    )

    ax.tick_params(
        axis="y",
        colors=theme["texte_secondaire"],
        labelsize=9,
        length=0,
        pad=7
    )

    # ========================================================
    # BORDURES
    # ========================================================

    for bordure in ax.spines.values():

        bordure.set_visible(False)

    # ========================================================
    # MISE À JOUR
    # ========================================================

    heure = datetime.now().strftime(
        "%H:%M:%S"
    )

    figure.text(
        0.065,
        0.025,
        f"Mise à jour : {heure}",
        ha="left",
        va="bottom",
        color=theme["texte_secondaire"],
        fontsize=8
    )

    # ========================================================
    # ESPACEMENTS
    # ========================================================

    figure.subplots_adjust(
        left=0.065,
        right=0.985,
        top=0.985,
        bottom=0.105
    )

    canvas_graphique.draw_idle()


# ============================================================
# SURVOL GRAPHIQUE
# ============================================================

def afficher_info_souris(event):

    global annotations

    for annotation in annotations:

        try:
            annotation.remove()
        except:
            pass

    annotations = []

    if event.inaxes != ax:

        canvas_graphique.draw_idle()
        return

    meilleure_distance = float(
        "inf"
    )

    meilleure_info = None

    for nom, infos in lignes.items():

        dates = infos["dates"]
        valeurs = infos["valeurs"]

        try:

            points = np.column_stack(
                [
                    mdates.date2num(
                        dates
                    ),
                    valeurs
                ]
            )

            points_ecran = ax.transData.transform(
                points
            )

            distances = np.sqrt(
                (
                    points_ecran[:, 0]
                    -
                    event.x
                ) ** 2
                +
                (
                    points_ecran[:, 1]
                    -
                    event.y
                ) ** 2
            )

            index = int(
                np.argmin(
                    distances
                )
            )

            distance = distances[
                index
            ]

            if distance < meilleure_distance:

                meilleure_distance = distance

                meilleure_info = (
                    nom,
                    dates[index],
                    valeurs[index],
                    mdates.date2num(
                        dates[index]
                    )
                )

        except:
            pass

    if (
        meilleure_info is None
        or
        meilleure_distance > 35
    ):

        canvas_graphique.draw_idle()
        return

    nom, date, valeur, x = (
        meilleure_info
    )

    texte = (
        f"{nom}\n"
        f"{date.strftime('%d/%m/%Y %H:%M')}\n"
        f"{valeur:.2f} €"
    )

    couleur = couleurs_actions[
        nom
    ]

    annotation = ax.annotate(
        texte,
        xy=(x, valeur),
        xytext=(16, 16),
        textcoords="offset points",
        fontsize=10,
        fontweight="bold",
        color=theme["texte"],
        bbox=dict(
            boxstyle="round,pad=0.65",
            facecolor=theme["panneau2"],
            edgecolor=couleur,
            linewidth=1.2,
            alpha=0.98
        ),
        arrowprops=dict(
            arrowstyle="-",
            color=couleur,
            linewidth=1.2
        )
    )

    annotations.append(
        annotation
    )

    canvas_graphique.draw_idle()


canvas_graphique.mpl_connect(
    "motion_notify_event",
    afficher_info_souris
)


# ============================================================
# ACTUALISATION
# ============================================================

def actualiser():

    bouton_rafraichir.itemconfig(
        bouton_rafraichir.texte_id,
        text="↻   Chargement..."
    )

    bouton_rafraichir.tag_raise(
        bouton_rafraichir.texte_id
    )

    statut.configure(
        text=(
            f"Récupération des données "
            f"• {periode_actuelle}"
        )
    )

    def travail():

        donnees = recuperer_donnees()

        fenetre.after(
            0,
            lambda:
                terminer_actualisation(
                    donnees
                )
        )

    threading.Thread(
        target=travail,
        daemon=True
    ).start()


# ============================================================
# RÉCUPÉRATION
# ============================================================

def recuperer_donnees():

    configuration = periodes[
        periode_actuelle
    ]

    donnees = {}

    for nom in obtenir_ordre_actions():

        symbole = actions_cac40[nom]

        try:

            print(
                f"Téléchargement de {nom}..."
            )

            data = yf.download(
                symbole,
                period=configuration["period"],
                interval=configuration["interval"],
                auto_adjust=False,
                progress=False,
                threads=False
            )

            donnees[nom] = data

        except Exception as erreur:

            print(
                f"Erreur {nom} : {erreur}"
            )

            donnees[nom] = None

    return donnees


# ============================================================
# FIN ACTUALISATION
# ============================================================

def terminer_actualisation(donnees):

    afficher_graphique(
        donnees
    )

    bouton_rafraichir.itemconfig(
        bouton_rafraichir.texte_id,
        text="↻   Rafraîchir"
    )

    bouton_rafraichir.tag_raise(
        bouton_rafraichir.texte_id
    )

    heure = datetime.now().strftime(
        "%H:%M:%S"
    )

    statut.configure(
        text=f"● Données mises à jour à {heure}"
    )


# ============================================================
# SÉLECTION ACTIONS
# ============================================================

def ouvrir_selection_actions():

    fenetre_selection = tk.Toplevel(
        fenetre
    )

    fenetre_selection.title(
        "Sélection des actions"
    )

    fenetre_selection.geometry(
        "820x800"
    )

    fenetre_selection.configure(
        bg=theme["fond_haut"]
    )

    fenetre_selection.transient(
        fenetre
    )

    # ========================================================
    # TITRE
    # ========================================================

    titre_selection = tk.Label(
        fenetre_selection,
        text="Actions du CAC 40",
        font=(
            "Segoe UI",
            25,
            "bold"
        ),
        bg=theme["fond_haut"],
        fg=theme["texte"]
    )

    titre_selection.pack(
        pady=(25, 3)
    )

    sous_titre_selection = tk.Label(
        fenetre_selection,
        text="Sélectionne les valeurs à afficher",
        font=(
            "Segoe UI",
            11
        ),
        bg=theme["fond_haut"],
        fg=theme["texte_secondaire"]
    )

    sous_titre_selection.pack(
        pady=(0, 20)
    )

    # ========================================================
    # LISTE
    # ========================================================

    cadre_liste = tk.Frame(
        fenetre_selection,
        bg=theme["panneau"],
        highlightthickness=1,
        highlightbackground=theme["bordure"]
    )

    cadre_liste.pack(
        fill="both",
        expand=True,
        padx=30,
        pady=5
    )

    canvas_selection = tk.Canvas(
        cadre_liste,
        bg=theme["panneau"],
        highlightthickness=0,
        bd=0
    )

    scrollbar = tk.Scrollbar(
        cadre_liste,
        orient="vertical",
        command=canvas_selection.yview
    )

    cadre_cases = tk.Frame(
        canvas_selection,
        bg=theme["panneau"]
    )

    canvas_selection.create_window(
        (0, 0),
        window=cadre_cases,
        anchor="nw"
    )

    canvas_selection.configure(
        yscrollcommand=scrollbar.set
    )

    canvas_selection.pack(
        side="left",
        fill="both",
        expand=True
    )

    scrollbar.pack(
        side="right",
        fill="y"
    )

    variables = {}

    for index, nom in enumerate(
        actions_cac40
    ):

        variable = tk.BooleanVar(
            value=(
                nom
                in actions_selectionnees
            )
        )

        variables[nom] = variable

        case = tk.Checkbutton(
            cadre_cases,
            text=nom,
            variable=variable,
            anchor="w",
            font=(
                "Segoe UI",
                10
            ),
            bg=theme["panneau"],
            fg=theme["texte"],
            activebackground=theme["panneau"],
            activeforeground=theme["texte"],
            selectcolor=theme["verre"],
            relief="flat",
            bd=0,
            padx=18,
            pady=8
        )

        case.grid(
            row=index // 2,
            column=index % 2,
            sticky="ew",
            padx=12,
            pady=2
        )

    cadre_cases.columnconfigure(
        0,
        weight=1
    )

    cadre_cases.columnconfigure(
        1,
        weight=1
    )

    def maj_scroll(event=None):

        canvas_selection.configure(
            scrollregion=canvas_selection.bbox(
                "all"
            )
        )

    cadre_cases.bind(
        "<Configure>",
        maj_scroll
    )

    # ========================================================
    # BOUTONS
    # ========================================================

    cadre_boutons = tk.Frame(
        fenetre_selection,
        bg=theme["fond_haut"]
    )

    cadre_boutons.pack(
        fill="x",
        padx=30,
        pady=(15, 25)
    )

    def selectionner_tout():

        for variable in variables.values():

            variable.set(True)

    bouton_tout = creer_bouton_verre(
        cadre_boutons,
        "Tout sélectionner",
        selectionner_tout,
        190,
        45
    )

    bouton_tout.pack(
        side="left"
    )

    def deselectionner_tout():

        for variable in variables.values():

            variable.set(False)

    bouton_aucun = creer_bouton_verre(
        cadre_boutons,
        "Tout désélectionner",
        deselectionner_tout,
        205,
        45
    )

    bouton_aucun.pack(
        side="left",
        padx=10
    )

    def valider():

        global actions_selectionnees

        selection = {
            nom
            for nom, variable
            in variables.items()
            if variable.get()
        }

        if not selection:

            statut.configure(
                text=(
                    "⚠ Sélectionne au moins "
                    "une action."
                )
            )

            return

        actions_selectionnees = selection

        fenetre_selection.destroy()

        actualiser()

    bouton_valider = creer_bouton_verre(
        cadre_boutons,
        "✓   Valider",
        valider,
        155,
        45
    )

    bouton_valider.pack(
        side="right"
    )


# ============================================================
# THÈME
# ============================================================

def appliquer_theme():

    global theme

    if theme_sombre:

        theme = THEME_SOMBRE

    else:

        theme = THEME_CLAIR

    fenetre.configure(
        bg=theme["fond_bas"]
    )

    fond.configure(
        bg=theme["fond_bas"]
    )

    for cadre in [
        conteneur,
        entete,
        bloc_titre,
        bloc_live,
        barre_controles,
        barre_bas
    ]:

        cadre.configure(
            bg=theme["fond_bas"]
        )

    point_live.configure(
        bg=theme["fond_bas"]
    )

    titre.configure(
        bg=theme["fond_bas"],
        fg=theme["texte"]
    )

    sous_titre.configure(
        bg=theme["fond_bas"],
        fg=theme["texte_secondaire"]
    )

    label_live.configure(
        bg=theme["fond_bas"],
        fg=theme["texte_secondaire"]
    )

    label_periode.configure(
        bg=theme["fond_bas"],
        fg=theme["texte_secondaire"]
    )

    statut.configure(
        bg=theme["fond_bas"],
        fg=theme["texte_secondaire"]
    )

    for bouton in [
        bouton_actions,
        bouton_rafraichir,
        bouton_theme
    ]:

        bouton.configure(
            bg=theme["fond_bas"]
        )

        bouton.normal()

    bouton_periode.configure(
        bg=theme["fond_bas"]
    )

    dessiner_bouton_periode()

    if theme_sombre:

        bouton_theme.itemconfig(
            bouton_theme.texte_id,
            text="☀   Clair"
        )

    else:

        bouton_theme.itemconfig(
            bouton_theme.texte_id,
            text="☾   Sombre"
        )

    bouton_theme.tag_raise(
        bouton_theme.texte_id
    )

    cadre_graphique.configure(
        bg=theme["bordure"],
        highlightbackground=theme["bordure"]
    )

    dessiner_degrade()

    afficher_graphique(
        donnees_actuelles
    )


# ============================================================
# CHANGER THÈME
# ============================================================

def changer_theme():

    global theme_sombre

    theme_sombre = not theme_sombre

    appliquer_theme()


# ============================================================
# REDIMENSIONNEMENT
# ============================================================

def redimensionner(event=None):

    dessiner_degrade()


fond.bind(
    "<Configure>",
    redimensionner
)


# ============================================================
# ADAPTATION GRAPHIQUE
# ============================================================

def adapter_graphique(event=None):

    largeur = cadre_graphique.winfo_width()
    hauteur = cadre_graphique.winfo_height()

    if largeur < 50:
        return

    if hauteur < 50:
        return

    dpi = 180

    figure.set_dpi(
        dpi
    )

    figure.set_size_inches(
        max(
            5,
            (largeur - 12) / dpi
        ),
        max(
            4,
            (hauteur - 12) / dpi
        ),
        forward=False
    )

    canvas_graphique.draw_idle()


cadre_graphique.bind(
    "<Configure>",
    adapter_graphique
)


# ============================================================
# ACTUALISATION AUTOMATIQUE
# ============================================================

def actualisation_automatique():

    actualiser()

    fenetre.after(
        60 * 60 * 1000,
        actualisation_automatique
    )


# ============================================================
# INITIALISATION
# ============================================================

appliquer_theme()

actualiser()

fenetre.after(
    60 * 60 * 1000,
    actualisation_automatique
)

fenetre.mainloop()
