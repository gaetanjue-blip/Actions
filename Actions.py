import tkinter as tk
from tkinter import messagebox
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
import threading
import numpy as np
import pandas as pd


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
        "period": "2d",
        "interval": "5m"
    },

    "1 semaine": {
        "period": "5d",
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
    "verre_hover": "#2a394d",

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
    "#7DD3FC"
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

fenetre.geometry("2000x1200")

fenetre.minsize(
    1200,
    760
)


# ============================================================
# FOND EN DÉGRADÉ
# ============================================================

fond = tk.Canvas(
    fenetre,
    highlightthickness=0,
    bd=0
)

fond.pack(
    fill="both",
    expand=True
)


def dessiner_degrade():

    fond.delete("degrade")

    largeur = fond.winfo_width()
    hauteur = fond.winfo_height()

    if largeur <= 1:
        return

    if hauteur <= 1:
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
            (couleur_bas[0] - couleur_haut[0])
            * ratio
        )

        g = int(
            couleur_haut[1]
            +
            (couleur_bas[1] - couleur_haut[1])
            * ratio
        )

        b = int(
            couleur_haut[2]
            +
            (couleur_bas[2] - couleur_haut[2])
            * ratio
        )

        couleur = (
            f"#{r:02x}"
            f"{g:02x}"
            f"{b:02x}"
        )

        y1 = int(
            hauteur
            * i
            / nombre_lignes
        )

        y2 = int(
            hauteur
            * (i + 1)
            / nombre_lignes
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
# CONTENEUR PRINCIPAL
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
    bd=0
)

entete.pack(
    fill="x",
    pady=(20, 15)
)


bloc_titre = tk.Frame(
    entete,
    bd=0
)

bloc_titre.pack(
    side="left"
)


titre = tk.Label(
    bloc_titre,
    text="CacVision",
    font=(
        "Segoe UI",
        34,
        "bold"
    ),
    bd=0
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
    bd=0
)

sous_titre.pack(
    anchor="w",
    pady=(1, 0)
)


# ============================================================
# INDICATEUR EN DIRECT
# ============================================================

bloc_live = tk.Frame(
    entete,
    bd=0
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
    bd=0
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
    bd=0
)

label_live.pack(
    side="left"
)


# ============================================================
# BARRE DE CONTRÔLES
# ============================================================

barre_controles = tk.Frame(
    conteneur,
    bd=0
)

barre_controles.pack(
    fill="x",
    pady=(0, 18)
)


# ============================================================
# FONCTION PILULE
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
        cursor="hand2"
    )


    def normal():

        dessiner_pilule(
            bouton,
            largeur,
            hauteur,
            theme["verre"],
            theme["bordure"]
        )


    def hover():

        dessiner_pilule(
            bouton,
            largeur,
            hauteur,
            theme["verre_hover"],
            theme["accent2"]
        )


    normal()


    texte_id = bouton.create_text(
        largeur / 2,
        hauteur / 2,
        text=texte,
        fill=theme["texte"],
        font=(
            "Segoe UI",
            10,
            "bold"
        ),
        tags="texte"
    )


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


    bouton.pilule_largeur = largeur
    bouton.pilule_hauteur = hauteur
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
# SÉLECTEUR DE PÉRIODE
# ============================================================

label_periode = tk.Label(
    barre_controles,
    text="Période",
    font=(
        "Segoe UI",
        10,
        "bold"
    ),
    bd=0
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
    cursor="hand2"
)

bouton_periode.pack(
    side="left"
)


def dessiner_bouton_periode():

    dessiner_pilule(
        bouton_periode,
        190,
        48,
        theme["verre"],
        theme["bordure"]
    )


dessiner_bouton_periode()


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
    lambda event:
        dessiner_pilule(
            bouton_periode,
            190,
            48,
            theme["verre_hover"],
            theme["accent2"]
        )
)


bouton_periode.bind(
    "<Leave>",
    lambda event:
        dessiner_bouton_periode()
)


# ============================================================
# ESPACE
# ============================================================

tk.Frame(
    barre_controles
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
# ZONE PRINCIPALE : BARRE LATÉRALE + GRAPHIQUE
# ============================================================

zone_principale = tk.Frame(
    conteneur,
    bd=0
)

zone_principale.pack(
    fill="both",
    expand=True
)

# ------------------------------------------------------------
# BARRE LATÉRALE DES ACTIONS
# ------------------------------------------------------------

barre_laterale = tk.Frame(
    zone_principale,
    width=300,
    bd=0,
    highlightthickness=1
)

barre_laterale.pack(
    side="left",
    fill="y",
    padx=(0, 14)
)

barre_laterale.pack_propagate(False)


label_laterale = tk.Label(
    barre_laterale,
    text="VALEURS SÉLECTIONNÉES",
    font=("Segoe UI", 10, "bold"),
    bd=0,
    anchor="w"
)

label_laterale.pack(
    fill="x",
    padx=18,
    pady=(18, 4)
)

label_laterale_info = tk.Label(
    barre_laterale,
    text="Derniers cours disponibles",
    font=("Segoe UI", 9),
    bd=0,
    anchor="w"
)

label_laterale_info.pack(
    fill="x",
    padx=18,
    pady=(0, 12)
)

cartes_actions = tk.Frame(
    barre_laterale,
    bd=0
)

cartes_actions.pack(
    fill="both",
    expand=True,
    padx=12,
    pady=(0, 12)
)


def obtenir_dernieres_valeurs(data):
    """Retourne dernier cours et variation à partir des vraies données."""
    if data is None or data.empty:
        return None, None

    try:
        close = data["Close"]
        if hasattr(close, "columns"):
            close = close.iloc[:, 0]
        close = close.dropna()
        if close.empty:
            return None, None
        valeurs = close.astype(float).tolist()
        dernier = valeurs[-1]
        precedent = valeurs[-2] if len(valeurs) >= 2 else None
        variation = None
        if precedent is not None and precedent != 0:
            variation = (dernier - precedent) / precedent * 100
        return dernier, variation
    except Exception:
        return None, None


def mettre_a_jour_cartes_actions():
    """Reconstruit les cartes de cours dans la barre latérale."""
    for widget in cartes_actions.winfo_children():
        widget.destroy()

    if not actions_selectionnees:
        vide = tk.Label(
            cartes_actions,
            text="Aucune action sélectionnée",
            font=("Segoe UI", 10),
            bg=theme["panneau"],
            fg=theme["texte_secondaire"],
            bd=0
        )
        vide.pack(pady=25)
        return

    for nom in actions_cac40:
        if nom not in actions_selectionnees:
            continue
        carte = tk.Frame(
            cartes_actions,
            bg=theme["verre"],
            bd=0,
            highlightthickness=1,
            highlightbackground=theme["bordure"]
        )
        carte.pack(fill="x", pady=5)

        haut = tk.Frame(carte, bg=theme["verre"], bd=0)
        haut.pack(fill="x", padx=13, pady=(10, 2))

        point = tk.Canvas(
            haut, width=10, height=10,
            highlightthickness=0, bd=0
        )
        point.pack(side="left", padx=(0, 7))
        couleur = couleurs_actions.get(
            nom, COULEURS_COURBES[list(actions_selectionnees).index(nom) % len(COULEURS_COURBES)]
        )
        point.create_oval(2, 2, 9, 9, fill=couleur, outline="")

        nom_label = tk.Label(
            haut, text=nom,
            font=("Segoe UI", 10, "bold"),
            bg=theme["verre"], fg=theme["texte"],
            bd=0, anchor="w"
        )
        nom_label.pack(side="left", fill="x", expand=True)

        data = donnees_actuelles.get(nom)
        dernier, variation = obtenir_dernieres_valeurs(data)

        valeur_text = "—" if dernier is None else f"{dernier:.2f} €"
        valeur_label = tk.Label(
            carte, text=valeur_text,
            font=("Segoe UI", 17, "bold"),
            bg=theme["verre"], fg=theme["texte"],
            bd=0, anchor="w"
        )
        valeur_label.pack(fill="x", padx=13, pady=(0, 1))

        if variation is None:
            variation_text = "Variation indisponible"
        else:
            variation_text = f"{'+' if variation >= 0 else ''}{variation:.2f} %"

        variation_label = tk.Label(
            carte, text=variation_text,
            font=("Segoe UI", 9, "bold"),
            bg=theme["verre"],
            fg=theme["accent"] if variation is None or variation >= 0 else "#ff6b6b",
            bd=0, anchor="w"
        )
        variation_label.pack(fill="x", padx=13, pady=(0, 10))

        carte._point = point
        carte._labels = (nom_label, valeur_label, variation_label)


# ============================================================
# PANNEAU GRAPHIQUE
# ============================================================

cadre_graphique = tk.Frame(
    zone_principale,
    bd=0,
    highlightthickness=1
)

cadre_graphique.pack(
    side="left",
    fill="both",
    expand=True,
    padx=(0, 0),
    pady=0
)

# Garantit que la zone du graphique conserve une vraie place même
# pendant les premières phases de redimensionnement.
cadre_graphique.pack_propagate(False)


# ============================================================
# GRAPHIQUE
# ============================================================

figure, ax = plt.subplots(
    figsize=(14, 8),
    dpi=120
)

ax.set_facecolor(theme["panneau"])
figure.patch.set_facecolor(theme["panneau"])
ax.text(
    0.5, 0.5,
    "Chargement des données…",
    transform=ax.transAxes,
    ha="center",
    va="center",
    color=theme["texte_secondaire"],
    fontsize=14
)


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
    bd=0
)

barre_bas.pack(
    fill="x",
    pady=(14, 5)
)


statut = tk.Label(
    barre_bas,
    text="Initialisation...",
    font=(
        "Segoe UI",
        10
    ),
    bd=0
)

statut.pack(
    side="left"
)


bouton_actualiser = creer_bouton_verre(
    barre_bas,
    "↻   Actualiser",
    lambda: actualiser(),
    160,
    45
)

bouton_actualiser.pack(
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


    # Fond
    fenetre.configure(
        bg=theme["fond_bas"]
    )

    zone_principale.configure(
        bg=theme["fond_bas"]
    )

    barre_laterale.configure(
        bg=theme["panneau"],
        highlightbackground=theme["bordure"]
    )

    label_laterale.configure(
        bg=theme["panneau"],
        fg=theme["texte"]
    )

    label_laterale_info.configure(
        bg=theme["panneau"],
        fg=theme["texte_secondaire"]
    )

    cartes_actions.configure(
        bg=theme["panneau"]
    )


    # Cadres
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


    # Texte
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


    # Boutons
    for bouton in [
        bouton_actions,
        bouton_theme,
        bouton_actualiser
    ]:

        bouton.configure(
            bg=theme["fond_bas"]
        )

        bouton.normal()

        bouton.itemconfig(
            bouton.texte_id,
            fill=theme["texte"]
        )


    bouton_periode.configure(
        bg=theme["fond_bas"]
    )

    dessiner_bouton_periode()

    bouton_periode.itemconfig(
        texte_periode,
        fill=theme["texte"]
    )


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


    cadre_graphique.configure(
        bg=theme["bordure"],
        highlightbackground=theme["bordure"]
    )


    dessiner_degrade()

    mettre_a_jour_cartes_actions()

    afficher_graphique(
        donnees_actuelles
    )


# ============================================================
# CHANGER DE THÈME
# ============================================================

def changer_theme():

    global theme_sombre

    theme_sombre = not theme_sombre

    appliquer_theme()


# ============================================================
# TÉLÉCHARGEMENT DES DONNÉES
# ============================================================

def filtrer_donnees_periode(data):
    """Ne conserve que les cotations réellement disponibles dans la fenêtre choisie."""
    if data is None or data.empty:
        return data
    try:
        result = data.copy()
        index = pd.DatetimeIndex(result.index)
        if index.tz is not None:
            index = index.tz_convert(None)
        result.index = index

        durees = {
            "24 h": timedelta(hours=24),
            "1 semaine": timedelta(days=7),
            "1 mois": timedelta(days=30),
            "1 an": timedelta(days=365),
        }
        if periode_actuelle in durees:
            debut = pd.Timestamp(datetime.now() - durees[periode_actuelle])
            result = result.loc[result.index >= debut]
        return result
    except Exception as erreur:
        print("Erreur filtrage période :", erreur)
        return data

def recuperer_donnees():

    configuration = periodes[
        periode_actuelle
    ]

    donnees = {}


    for nom in actions_selectionnees:

        symbole = actions_cac40[nom]


        try:

            statut_temp = (
                f"Téléchargement de {nom}..."
            )


            print(
                statut_temp
            )


            data = yf.download(
                symbole,
                period=configuration["period"],
                interval=configuration["interval"],
                auto_adjust=False,
                progress=False,
                threads=False
            )


            donnees[nom] = filtrer_donnees_periode(data)


        except Exception as erreur:

            print(
                f"Erreur {nom} : {erreur}"
            )

            donnees[nom] = None


    return donnees


# ============================================================
# AFFICHAGE DU GRAPHIQUE
# ============================================================

# ============================================================
# COMPLÉTER LES PÉRIODES SANS DONNÉES
# ============================================================

def construire_courbe_continue(dates, valeurs):
    """
    Conserve les vraies cotations et prolonge horizontalement
    la dernière valeur lorsqu'il n'y a temporairement aucune donnée.

    Exemple :
        vendredi 100 € -> samedi 100 € -> dimanche 100 € -> lundi 105 €

    Les points ajoutés pour combler un trou ne sont pas utilisés
    par l'info-bulle : seules les vraies cotations restent affichées.
    """

    if len(dates) == 0:
        return [], []

    vraies_dates = [
        pd.Timestamp(date).to_pydatetime()
        for date in dates
    ]

    vraies_valeurs = [
        float(valeur)
        for valeur in valeurs
    ]

    courbe_dates = []
    courbe_valeurs = []

    for i in range(len(vraies_dates)):

        date_actuelle = vraies_dates[i]
        valeur_actuelle = vraies_valeurs[i]

        courbe_dates.append(date_actuelle)
        courbe_valeurs.append(valeur_actuelle)

        if i >= len(vraies_dates) - 1:
            continue

        date_suivante = vraies_dates[i + 1]
        valeur_suivante = vraies_valeurs[i + 1]

        ecart = date_suivante - date_actuelle

        # Plus de 24 h sans cotation : week-end, jour férié,
        # ou autre interruption de données.
        if ecart > timedelta(hours=24):

            # On place un point juste avant la prochaine vraie cotation.
            # La courbe reste donc parfaitement horizontale pendant
            # toute la période sans données.
            if date_suivante - timedelta(minutes=1) > date_actuelle:
                courbe_dates.append(
                    date_suivante - timedelta(minutes=1)
                )
                courbe_valeurs.append(
                    valeur_actuelle
                )

            # La prochaine vraie valeur sera ajoutée normalement
            # à l'itération suivante.

    # Si la dernière cotation est ancienne, on la prolonge jusqu'à
    # maintenant. C'est notamment ce qui permet de voir la courbe
    # horizontale pendant tout le week-end.
    maintenant = datetime.now()

    if vraies_dates[-1] < maintenant:

        ecart_final = maintenant - vraies_dates[-1]

        if ecart_final > timedelta(minutes=5):

            courbe_dates.append(maintenant)
            courbe_valeurs.append(vraies_valeurs[-1])

    return courbe_dates, courbe_valeurs


def configurer_dates_graphique(ax, toutes_les_dates):
    """Configure l'axe X pour conserver les jours sans cotation visibles."""

    maintenant = datetime.now()

    if periode_actuelle == "24 h":

        # En semaine : vraie fenêtre de 24 h.
        # Le week-end : on garde la dernière séance visible afin
        # d'éviter un graphique vide.
        if maintenant.weekday() >= 5 and toutes_les_dates:
            debut = min(
                toutes_les_dates[-1] - timedelta(hours=24),
                maintenant - timedelta(days=2)
            )
        else:
            debut = maintenant - timedelta(hours=24)

        fin = maintenant

        ax.set_xlim(debut, fin)

        ax.xaxis.set_major_locator(
            mdates.HourLocator(interval=3)
        )

        ax.xaxis.set_major_formatter(
            mdates.DateFormatter("%H:%M")
        )

    elif periode_actuelle == "1 semaine":

        debut = maintenant.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        ) - timedelta(days=6)

        fin = maintenant.replace(
            hour=23,
            minute=59,
            second=59,
            microsecond=0
        )

        ax.set_xlim(debut, fin)

        ax.xaxis.set_major_locator(
            mdates.DayLocator(interval=1)
        )

        ax.xaxis.set_major_formatter(
            mdates.DateFormatter("%a %d/%m")
        )

    elif periode_actuelle == "1 mois":

        debut = maintenant - timedelta(days=30)
        fin = maintenant

        ax.set_xlim(debut, fin)

        ax.xaxis.set_major_locator(
            mdates.DayLocator(interval=4)
        )

        ax.xaxis.set_major_formatter(
            mdates.DateFormatter("%d/%m")
        )

    elif periode_actuelle == "1 an":

        debut = maintenant - timedelta(days=365)
        fin = maintenant

        ax.set_xlim(debut, fin)

        ax.xaxis.set_major_locator(
            mdates.MonthLocator()
        )

        ax.xaxis.set_major_formatter(
            mdates.DateFormatter("%b %Y")
        )

    else:

        if toutes_les_dates:
            debut = min(toutes_les_dates)
            fin = max(
                maintenant,
                max(toutes_les_dates)
            )

            if debut == fin:
                debut -= timedelta(days=1)
                fin += timedelta(days=1)

            ax.set_xlim(debut, fin)

        locator = mdates.AutoDateLocator(
            minticks=7,
            maxticks=12
        )

        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(
            mdates.ConciseDateFormatter(locator)
        )


def afficher_popup_weekend():

    maintenant = datetime.now()

    if maintenant.weekday() >= 5:

        messagebox.showinfo(
            "Bourse fermée",
            "La Bourse est fermée ce week-end.\n\n"
            "Les dernières valeurs disponibles restent affichées.\n"
            "Reprise lundi."
        )


def afficher_graphique(donnees):

    global donnees_actuelles
    global lignes
    global annotations
    global couleurs_actions


    donnees_actuelles = donnees


    # Nettoyage
    for annotation in annotations:

        try:

            annotation.remove()

        except:

            pass


    annotations = []

    lignes = {}


    ax.clear()


    # Couleurs du graphique
    ax.set_facecolor(
        theme["panneau"]
    )


    figure.patch.set_facecolor(
        theme["panneau"]
    )


    # ========================================================
    # COULEURS
    # ========================================================

    couleurs_actions = {}


    for i, nom in enumerate(
        actions_selectionnees
    ):

        couleurs_actions[nom] = (
            COULEURS_COURBES[
                i % len(COULEURS_COURBES)
            ]
        )


    # ========================================================
    # COURBES
    # ========================================================

    toutes_les_dates = []

    for nom in actions_selectionnees:

        data = donnees.get(nom)

        if data is None or data.empty:
            continue

        try:

            cours = data["Close"]

            if hasattr(cours, "columns"):
                cours = cours.iloc[:, 0]

            cours = cours.dropna()

            if len(cours) == 0:
                continue

            dates = pd.DatetimeIndex(cours.index)

            # Retirer proprement le fuseau horaire éventuel de yfinance.
            if dates.tz is not None:
                dates = dates.tz_convert(None)

            valeurs = np.asarray(
                cours.values,
                dtype=float
            )

            dates_reelles = [
                date.to_pydatetime()
                for date in dates
            ]

            toutes_les_dates.extend(
                dates_reelles
            )

            couleur = couleurs_actions[nom]

            # Courbe complétée : les périodes sans cotation restent
            # horizontales au dernier cours connu.
            dates_courbe, valeurs_courbe = construire_courbe_continue(
                dates_reelles,
                valeurs
            )

            if not dates_courbe:
                continue

            ligne, = ax.plot(
                dates_courbe,
                valeurs_courbe,
                color=couleur,
                linewidth=2.0,
                alpha=0.97,
                solid_capstyle="round",
                solid_joinstyle="round",
                antialiased=True,
                picker=7,
                label=nom
            )

            # Petit halo visuel
            ax.plot(
                dates_courbe,
                valeurs_courbe,
                color=couleur,
                linewidth=5,
                alpha=0.035,
                solid_capstyle="round",
                antialiased=True,
                picker=False
            )

            # Les points sont uniquement les vraies cotations.
            if len(dates_reelles) < 250:

                ax.scatter(
                    dates_reelles,
                    valeurs,
                    color=couleur,
                    s=7,
                    alpha=0.55,
                    linewidths=0
                )

            lignes[nom] = {
                "ligne": ligne,
                "dates": dates,
                "valeurs": valeurs,
                "dates_reelles": dates_reelles,
                "valeurs_reelles": valeurs
            }

        except Exception as erreur:

            print(
                "Erreur graphique :",
                erreur
            )

    # Mise à jour des cartes de cours dans la barre latérale.
    mettre_a_jour_cartes_actions()

    # S'il n'y a qu'une seule vraie valeur, on prolonge explicitement
    # cette valeur jusqu'à maintenant : la courbe reste horizontale.
    for nom, infos in lignes.items():

        if len(infos["dates_reelles"]) == 1:

            date_unique = infos["dates_reelles"][0]
            valeur_unique = infos["valeurs_reelles"][0]

            fin = max(
                datetime.now(),
                date_unique + timedelta(hours=1)
            )

            # La ligne est déjà horizontale grâce à construire_courbe_continue.
            # On ne modifie pas les données utilisées par l'info-bulle.
            if date_unique < fin:
                pass

    # Axe calendrier : les week-ends restent visibles même sans cotation.
    if toutes_les_dates:
        configurer_dates_graphique(
            ax,
            sorted(toutes_les_dates)
        )
    else:
        locator = mdates.AutoDateLocator(
            minticks=7,
            maxticks=12
        )
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(
            mdates.ConciseDateFormatter(locator)
        )

    # ========================================================
    # TITRE / AXES / GRILLE
    # ========================================================

    ax.set_title(
        f"{periode_actuelle}",
        color=theme["texte"],
        fontsize=18,
        fontweight="bold",
        loc="left",
        pad=12
    )

    ax.set_xlabel(
        "",
        color=theme["texte_secondaire"]
    )

    ax.set_ylabel(
        "Cours (€)",
        color=theme["texte_secondaire"],
        fontsize=10,
        labelpad=10
    )

    ax.grid(
        True,
        which="major",
        color=theme["grille"],
        alpha=0.16,
        linewidth=0.7
    )

    ax.grid(
        True,
        which="minor",
        color=theme["grille"],
        alpha=0.06,
        linewidth=0.45
    )

    ax.minorticks_on()

    # Les graduations sont volontairement espacées et les textes ne
    # tournent pas : cela évite tout chevauchement sur les petites fenêtres.
    ax.tick_params(
        axis="x",
        colors=theme["texte_secondaire"],
        labelsize=8,
        length=0,
        pad=7,
        rotation=0
    )

    ax.tick_params(
        axis="y",
        colors=theme["texte_secondaire"],
        labelsize=9,
        length=0,
        pad=8
    )

    for bordure in ax.spines.values():
        bordure.set_visible(False)

    # ========================================================
    # LÉGENDE
    # ========================================================

    if lignes:
        nombre = len(lignes)
        colonnes = min(nombre, 4)
        lignes_legende = (nombre + colonnes - 1) // colonnes

        legende = ax.legend(
            loc="upper center",
            bbox_to_anchor=(0.5, 1.015),
            bbox_transform=ax.transAxes,
            frameon=False,
            fontsize=9,
            ncol=colonnes,
            columnspacing=1.4,
            handlelength=2.4,
            handletextpad=0.5,
            labelspacing=0.7,
            borderaxespad=0
        )

        for texte in legende.get_texts():
            texte.set_color(theme["texte"])

    # ========================================================
    # DERNIÈRE MISE À JOUR
    # ========================================================

    heure = datetime.now().strftime("%H:%M:%S")

    # Placée sous l'axe mais dans une zone réservée par subplots_adjust.
    ax.text(
        0.0,
        -0.16,
        f"Dernière mise à jour : {heure}",
        transform=ax.transAxes,
        color=theme["texte_secondaire"],
        fontsize=8,
        ha="left",
        va="top",
        clip_on=False
    )

    # Marges généreuses : gauche pour le label Y, haut pour la légende,
    # bas pour les dates + l'heure de mise à jour.
    figure.subplots_adjust(
        left=0.095,
        right=0.985,
        top=0.78 if lignes else 0.90,
        bottom=0.20
    )

    canvas_graphique.draw_idle()



# ============================================================
# SURVOL DU GRAPHIQUE
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


    meilleure_distance = float("inf")

    meilleure_info = None


    for nom, infos in lignes.items():

        dates = infos["dates"]

        valeurs = infos["valeurs"]

        ligne = infos["ligne"]


        try:

            points = np.column_stack(
                [
                    mdates.date2num(dates),
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
                np.argmin(distances)
            )


            distance = distances[index]


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
            alpha=0.97
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

actualisation_en_cours = False


def actualiser():
    global actualisation_en_cours

    if actualisation_en_cours:
        return

    actualisation_en_cours = True
    bouton_actualiser.itemconfig(
        bouton_actualiser.texte_id,
        text="↻   Chargement..."
    )
    statut.configure(
        text=f"Récupération des données • {periode_actuelle}"
    )

    def travail():
        try:
            donnees = recuperer_donnees()
            fenetre.after(
                0,
                lambda: terminer_actualisation(donnees)
            )
        except Exception as erreur:
            fenetre.after(
                0,
                lambda: terminer_actualisation({}, erreur)
            )

    threading.Thread(
        target=travail,
        daemon=True
    ).start()


# ============================================================
# FIN ACTUALISATION
# ============================================================

def terminer_actualisation(donnees, erreur=None):
    global actualisation_en_cours

    try:
        if erreur is not None:
            print("Erreur actualisation :", erreur)
            statut.configure(text="⚠ Erreur pendant le téléchargement")
            return

        afficher_graphique(donnees)
        heure = datetime.now().strftime("%H:%M:%S")
        statut.configure(text=f"● Données mises à jour à {heure}")
    finally:
        actualisation_en_cours = False
        bouton_actualiser.itemconfig(
            bouton_actualiser.texte_id,
            text="↻   Actualiser"
        )


# ============================================================
# SÉLECTION DES ACTIONS
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


    fenetre_selection.update_idletasks()

    selection_window_id = canvas_selection.create_window(
        (0, 0),
        window=cadre_cases,
        anchor="nw"
    )

    def ajuster_largeur_cases(event=None):
        canvas_selection.itemconfigure(
            selection_window_id,
            width=max(1, canvas_selection.winfo_width())
        )

    canvas_selection.bind("<Configure>", ajuster_largeur_cases)


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
    boutons_actions = {}

    def actualiser_style_action(nom):
        bouton = boutons_actions[nom]
        if variables[nom].get():
            bouton.configure(
                text=f"✓   {nom}",
                bg=theme["verre"],
                fg=theme["texte"],
                activebackground=theme["verre_hover"],
                activeforeground=theme["texte"]
            )
        else:
            bouton.configure(
                text=f"     {nom}",
                bg=theme["panneau"],
                fg=theme["texte_secondaire"],
                activebackground=theme["verre_hover"],
                activeforeground=theme["texte"]
            )

    def basculer_action(nom):
        variables[nom].set(not variables[nom].get())
        actualiser_style_action(nom)

    for index, nom in enumerate(actions_cac40):
        variables[nom] = tk.BooleanVar(value=(nom in actions_selectionnees))

        bouton = tk.Button(
            cadre_cases,
            font=("Segoe UI", 10, "bold"),
            anchor="w",
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=theme["bordure"],
            highlightcolor=theme["accent2"],
            cursor="hand2",
            padx=18,
            pady=10,
            command=lambda n=nom: basculer_action(nom)
        )
        bouton.grid(
            row=index // 2,
            column=index % 2,
            sticky="ew",
            padx=8,
            pady=5
        )
        boutons_actions[nom] = bouton
        actualiser_style_action(nom)

    cadre_cases.columnconfigure(0, weight=1, uniform="actions")
    cadre_cases.columnconfigure(1, weight=1, uniform="actions")

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
        for nom, variable in variables.items():
            variable.set(True)
            actualiser_style_action(nom)


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
        for nom, variable in variables.items():
            variable.set(False)
            actualiser_style_action(nom)


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
# REDIMENSIONNEMENT
# ============================================================

def redimensionner(event=None):

    dessiner_degrade()


fond.bind(
    "<Configure>",
    redimensionner
)


# ============================================================
# QUALITÉ GRAPHIQUE AUTOMATIQUE
# ============================================================

def adapter_graphique(event=None):
    """Adapte la figure sans recréer les widgets ni écraser les marges."""

    largeur = cadre_graphique.winfo_width()
    hauteur = cadre_graphique.winfo_height()

    if largeur < 120 or hauteur < 120:
        return

    # DPI raisonnable : le rendu reste net sans provoquer une figure
    # gigantesque qui accentuerait les problèmes de placement.
    dpi = 120
    figure.set_dpi(dpi)
    figure.set_size_inches(
        max(6.0, largeur / dpi),
        max(4.0, hauteur / dpi),
        forward=False
    )

    # Recalcule les marges après chaque redimensionnement.
    if lignes:
        figure.subplots_adjust(
            left=0.095, right=0.985, top=0.78, bottom=0.20
        )
    else:
        figure.subplots_adjust(
            left=0.095, right=0.985, top=0.90, bottom=0.20
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


# Information affichée une fois au lancement si nous sommes le week-end.
fenetre.after(900, afficher_popup_weekend)


fenetre.after(
    60 * 60 * 1000,
    actualisation_automatique
)


fenetre.mainloop()
