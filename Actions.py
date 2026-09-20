import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
import threading
import ctypes

import numpy as np
import pandas as pd
import yfinance as yf

import matplotlib
matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# ============================================================
# DPI WINDOWS
# ============================================================

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


# ============================================================
# LISTE DES VALEURS DU CAC 40
# ============================================================

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


# ============================================================
# VALEURS SÉLECTIONNÉES PAR DÉFAUT
# ============================================================

actions_selectionnees = [
    "Thales",
    "Airbus",
    "Vinci"
]


# ============================================================
# PÉRIODES
# ============================================================

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


periode_actuelle = "1 semaine"


# ============================================================
# THÈMES
# ============================================================

themes = {

    "sombre": {
        "fond": "#111318",
        "fond_bas": "#171A21",
        "panneau": "#1E222B",
        "panneau2": "#252A34",

        "texte": "#F5F5F5",
        "texte_secondaire": "#AEB4C0",

        "accent": "#4C8DFF",
        "accent_hover": "#619AFF",

        "verre": "#252A34",
        "verre_hover": "#303642",

        "bordure": "#363D49",

        "graph_fond": "#171A21",
        "graph_grille": "#343A46"
    },

    "clair": {
        "fond": "#EEF1F5",
        "fond_bas": "#F7F8FA",
        "panneau": "#FFFFFF",
        "panneau2": "#F0F2F5",

        "texte": "#15171B",
        "texte_secondaire": "#69707C",

        "accent": "#2878F0",
        "accent_hover": "#4288F2",

        "verre": "#E5E8ED",
        "verre_hover": "#D9DDE4",

        "bordure": "#D3D7DE",

        "graph_fond": "#FFFFFF",
        "graph_grille": "#DDE1E7"
    }
}


theme_actuel = "sombre"
theme = themes[theme_actuel]


# ============================================================
# FENÊTRE
# ============================================================

fenetre = tk.Tk()

fenetre.title("CacVision")
fenetre.geometry("1900x1080")
fenetre.minsize(1200, 760)

fenetre.configure(
    bg=theme["fond"]
)


# ============================================================
# VARIABLES
# ============================================================

chargement = False
popup_weekend_deja_affiche = False

figure = None
ax = None
canvas_graphique = None

lignes_graphique = []

tooltip = None


# ============================================================
# COULEURS DES COURBES
# ============================================================

couleurs_courbes = [
    "#4C8DFF",
    "#FF5C5C",
    "#34C759",
    "#FF9F0A",
    "#AF52DE",
    "#00C7BE",
    "#FF375F",
    "#64D2FF",
    "#30D158",
    "#FFD60A",
    "#BF5AF2",
    "#FF6482",
    "#5E5CE6",
    "#AC8E68",
    "#0A84FF"
]


def couleur_action(index):
    return couleurs_courbes[
        index % len(couleurs_courbes)
    ]


# ============================================================
# FOND
# ============================================================

canvas_fond = tk.Canvas(
    fenetre,
    highlightthickness=0,
    bd=0,
    bg=theme["fond"]
)

canvas_fond.pack(
    fill="both",
    expand=True
)


def dessiner_fond():
    canvas_fond.delete("fond")

    largeur = max(
        canvas_fond.winfo_width(),
        1
    )

    hauteur = max(
        canvas_fond.winfo_height(),
        1
    )

    if theme_actuel == "sombre":

        haut = "#111318"
        bas = "#171A21"

    else:

        haut = "#EEF1F5"
        bas = "#F7F8FA"

    # Dégradé très léger
    for i in range(70):

        ratio = i / 69

        r1 = int(haut[1:3], 16)
        g1 = int(haut[3:5], 16)
        b1 = int(haut[5:7], 16)

        r2 = int(bas[1:3], 16)
        g2 = int(bas[3:5], 16)
        b2 = int(bas[5:7], 16)

        r = int(r1 + (r2 - r1) * ratio)
        g = int(g1 + (g2 - g1) * ratio)
        b = int(b1 + (b2 - b1) * ratio)

        couleur = f"#{r:02x}{g:02x}{b:02x}"

        y1 = int(hauteur * i / 70)
        y2 = int(hauteur * (i + 1) / 70) + 1

        canvas_fond.create_rectangle(
            0,
            y1,
            largeur,
            y2,
            fill=couleur,
            outline="",
            tags="fond"
        )


canvas_fond.bind(
    "<Configure>",
    lambda event: dessiner_fond()
)


# ============================================================
# CONTENEUR PRINCIPAL
# ============================================================

conteneur = tk.Frame(
    canvas_fond,
    bg=theme["fond_bas"]
)

fenetre.after(
    100,
    lambda: canvas_fond.create_window(
        0,
        0,
        anchor="nw",
        window=conteneur,
        width=canvas_fond.winfo_width(),
        height=canvas_fond.winfo_height()
    )
)


# ============================================================
# TITRE
# ============================================================

cadre_titre = tk.Frame(
    conteneur,
    bg=theme["fond_bas"]
)

cadre_titre.pack(
    fill="x",
    padx=35,
    pady=(25, 5)
)


titre = tk.Label(
    cadre_titre,
    text="CacVision",
    font=("Segoe UI", 30, "bold"),
    bg=theme["fond_bas"],
    fg=theme["texte"]
)

titre.pack(
    anchor="w"
)


sous_titre = tk.Label(
    cadre_titre,
    text="Suivi détaillé des valeurs du CAC 40",
    font=("Segoe UI", 12),
    bg=theme["fond_bas"],
    fg=theme["texte_secondaire"]
)

sous_titre.pack(
    anchor="w",
    pady=(2, 0)
)


# ============================================================
# BARRE DE CONTRÔLES
# ============================================================

barre_controles = tk.Frame(
    conteneur,
    bg=theme["fond_bas"]
)

barre_controles.pack(
    fill="x",
    padx=35,
    pady=(18, 10)
)


# ============================================================
# BOUTONS ARRONDIS
# ============================================================

def dessiner_bouton(
    bouton_canvas,
    largeur,
    hauteur,
    couleur,
    texte,
    couleur_texte
):

    bouton_canvas.delete("all")

    rayon = hauteur // 2

    # Pas de contour :
    # cela supprime la ligne bleue au survol.

    bouton_canvas.create_rectangle(
        rayon,
        0,
        largeur - rayon,
        hauteur,
        fill=couleur,
        outline=""
    )

    bouton_canvas.create_oval(
        0,
        0,
        hauteur,
        hauteur,
        fill=couleur,
        outline=""
    )

    bouton_canvas.create_oval(
        largeur - hauteur,
        0,
        largeur,
        hauteur,
        fill=couleur,
        outline=""
    )

    bouton_canvas.create_text(
        largeur // 2,
        hauteur // 2,
        text=texte,
        fill=couleur_texte,
        font=("Segoe UI", 10, "bold")
    )


def creer_bouton_verre(
    parent,
    texte,
    commande,
    largeur=160
):

    hauteur = 42

    bouton = tk.Canvas(
        parent,
        width=largeur,
        height=hauteur,
        bg=theme["fond_bas"],
        highlightthickness=0,
        bd=0,
        takefocus=0
    )

    bouton.pack(
        side="left",
        padx=6
    )

    def normal():
        dessiner_bouton(
            bouton,
            largeur,
            hauteur,
            theme["verre"],
            texte,
            theme["texte"]
        )

    def survol():
        dessiner_bouton(
            bouton,
            largeur,
            hauteur,
            theme["verre_hover"],
            texte,
            theme["texte"]
        )

    normal()

    bouton.bind(
        "<Enter>",
        lambda event: survol()
    )

    bouton.bind(
        "<Leave>",
        lambda event: normal()
    )

    bouton.bind(
        "<Button-1>",
        lambda event: commande()
    )

    return bouton


# ============================================================
# CHOIX DE PÉRIODE
# ============================================================

label_periode = tk.Label(
    barre_controles,
    text="Période :",
    font=("Segoe UI", 10, "bold"),
    bg=theme["fond_bas"],
    fg=theme["texte"]
)

label_periode.pack(
    side="left",
    padx=(0, 5)
)


def changer_periode(nouvelle_periode):

    global periode_actuelle

    periode_actuelle = nouvelle_periode

    actualiser()


for nom_periode in periodes:

    creer_bouton_verre(
        barre_controles,
        nom_periode,
        lambda p=nom_periode: changer_periode(p),
        largeur=130
    )


# ============================================================
# BOUTON VALEURS
# ============================================================

creer_bouton_verre(
    barre_controles,
    "Choisir les valeurs",
    lambda: ouvrir_selection_actions(),
    largeur=175
)


# ============================================================
# BOUTON THÈME
# ============================================================

def changer_theme():

    global theme_actuel
    global theme

    if theme_actuel == "sombre":
        theme_actuel = "clair"
    else:
        theme_actuel = "sombre"

    theme = themes[theme_actuel]

    appliquer_theme()


bouton_theme = creer_bouton_verre(
    barre_controles,
    "Mode sombre / clair",
    changer_theme,
    largeur=190
)


# ============================================================
# ZONE GRAPHIQUE
# ============================================================

cadre_graphique = tk.Frame(
    conteneur,
    bg=theme["panneau"],
    highlightthickness=0,
    bd=0
)

cadre_graphique.pack(
    fill="both",
    expand=True,
    padx=35,
    pady=(5, 5)
)


# ============================================================
# FIGURE MATPLOTLIB
# ============================================================

figure = plt.Figure(
    figsize=(16, 8),
    dpi=180
)

ax = figure.add_subplot(
    111
)

canvas_graphique = FigureCanvasTkAgg(
    figure,
    master=cadre_graphique
)

widget_graphique = canvas_graphique.get_tk_widget()

widget_graphique.pack(
    fill="both",
    expand=True,
    padx=8,
    pady=8
)


# ============================================================
# LÉGENDE SÉPARÉE
# ============================================================

legende_externe = tk.Frame(
    conteneur,
    bg=theme["panneau2"],
    highlightthickness=0,
    bd=0
)

legende_externe.pack(
    fill="x",
    padx=35,
    pady=(5, 5)
)


legende_interne = tk.Frame(
    legende_externe,
    bg=theme["panneau2"]
)

legende_interne.pack(
    fill="x",
    padx=10,
    pady=7
)


def reconstruire_legende():

    for widget in legende_interne.winfo_children():
        widget.destroy()

    nombre = len(actions_selectionnees)

    if nombre == 0:

        label = tk.Label(
            legende_interne,
            text="Aucune valeur sélectionnée",
            font=("Segoe UI", 9),
            bg=theme["panneau2"],
            fg=theme["texte_secondaire"]
        )

        label.pack()

        return

    if nombre <= 4:
        colonnes = nombre

    elif nombre <= 12:
        colonnes = 4

    else:
        colonnes = 6

    for colonne in range(colonnes):

        legende_interne.grid_columnconfigure(
            colonne,
            weight=1
        )

    for index, nom in enumerate(actions_selectionnees):

        ligne = index // colonnes
        colonne = index % colonnes

        couleur = couleur_action(index)

        cellule = tk.Frame(
            legende_interne,
            bg=theme["panneau2"]
        )

        cellule.grid(
            row=ligne,
            column=colonne,
            sticky="w",
            padx=8,
            pady=2
        )

        point = tk.Canvas(
            cellule,
            width=12,
            height=12,
            bg=theme["panneau2"],
            highlightthickness=0,
            bd=0
        )

        point.pack(
            side="left",
            padx=(0, 5)
        )

        point.create_oval(
            2,
            2,
            10,
            10,
            fill=couleur,
            outline=""
        )

        texte = tk.Label(
            cellule,
            text=nom,
            font=("Segoe UI", 8),
            bg=theme["panneau2"],
            fg=theme["texte"]
        )

        texte.pack(
            side="left"
        )


# ============================================================
# BARRE DU BAS
# ============================================================

barre_bas = tk.Frame(
    conteneur,
    bg=theme["fond_bas"]
)

barre_bas.pack(
    fill="x",
    padx=35,
    pady=(5, 20)
)


statut = tk.Label(
    barre_bas,
    text="Prêt",
    font=("Segoe UI", 10),
    bg=theme["fond_bas"],
    fg=theme["texte_secondaire"]
)

statut.pack(
    side="left"
)


# ============================================================
# BOUTON ACTUALISER
# ============================================================

def bouton_actualiser():

    actualiser()


bouton_actualiser_canvas = creer_bouton_verre(
    barre_bas,
    "↻  Actualiser",
    bouton_actualiser,
    largeur=150
)


# ============================================================
# NORMALISATION DES DATES
# ============================================================

def convertir_dates_france(index):

    index = pd.DatetimeIndex(index)

    try:

        if index.tz is not None:

            index = index.tz_convert(
                "Europe/Paris"
            )

            index = index.tz_localize(
                None
            )

    except Exception:
        pass

    return index


# ============================================================
# COUPER LES LIGNES ENTRE LES JOURS SANS DONNÉES
# ============================================================

def couper_weekends(dates, valeurs):

    nouvelles_dates = []
    nouvelles_valeurs = []

    if len(dates) == 0:
        return nouvelles_dates, nouvelles_valeurs

    for i in range(len(dates)):

        date_actuelle = pd.Timestamp(
            dates[i]
        ).to_pydatetime()

        valeur_actuelle = valeurs[i]

        nouvelles_dates.append(
            date_actuelle
        )

        nouvelles_valeurs.append(
            valeur_actuelle
        )

        if i < len(dates) - 1:

            date_suivante = pd.Timestamp(
                dates[i + 1]
            ).to_pydatetime()

            ecart_heures = (
                date_suivante - date_actuelle
            ).total_seconds() / 3600

            # Plus de 24 h entre deux données :
            # on insère NaN pour casser la courbe.
            if ecart_heures > 24:

                milieu = (
                    date_actuelle
                    +
                    (date_suivante - date_actuelle) / 2
                )

                nouvelles_dates.append(
                    milieu
                )

                nouvelles_valeurs.append(
                    np.nan
                )

    return (
        nouvelles_dates,
        nouvelles_valeurs
    )


# ============================================================
# FILTRAGE DES DONNÉES
# ============================================================

def filtrer_donnees(index, valeurs):

    maintenant = datetime.now()

    if len(index) == 0:
        return index, valeurs

    # 24 heures :
    # on se base sur le dernier cours disponible
    # pour éviter d'avoir un graphique vide le week-end.

    if periode_actuelle == "24 h":

        dernier = pd.Timestamp(
            index[-1]
        ).to_pydatetime()

        debut = dernier - timedelta(
            hours=24
        )

        masque = (
            index >= debut
        ) & (
            index <= dernier
        )

    elif periode_actuelle == "1 semaine":

        debut = maintenant - timedelta(
            days=7
        )

        masque = (
            index >= debut
        )

    elif periode_actuelle == "1 mois":

        debut = maintenant - timedelta(
            days=30
        )

        masque = (
            index >= debut
        )

    elif periode_actuelle == "1 an":

        debut = maintenant - timedelta(
            days=365
        )

        masque = (
            index >= debut
        )

    else:

        masque = np.ones(
            len(index),
            dtype=bool
        )

    return (
        index[masque],
        valeurs[masque]
    )


# ============================================================
# CONFIGURATION DE L'AXE X
# ============================================================

def configurer_axe_dates():

    maintenant = datetime.now()

    if periode_actuelle == "24 h":

        ax.xaxis.set_major_locator(
            mdates.HourLocator(
                interval=2
            )
        )

        ax.xaxis.set_major_formatter(
            mdates.DateFormatter(
                "%H:%M"
            )
        )

        # Pour le week-end, garder le dernier jour coté.
        if lignes_graphique:

            toutes_dates = []

            for ligne in lignes_graphique:

                x = ligne.get_xdata()

                if len(x) > 0:
                    toutes_dates.extend(x)

            if toutes_dates:

                dates_converties = [
                    mdates.num2date(x).replace(
                        tzinfo=None
                    )
                    for x in toutes_dates
                    if np.isfinite(x)
                ]

                if dates_converties:

                    fin = max(
                        dates_converties
                    )

                    debut = fin - timedelta(
                        hours=24
                    )

                    ax.set_xlim(
                        debut,
                        fin
                    )

    elif periode_actuelle == "1 semaine":

        debut = maintenant - timedelta(
            days=6
        )

        fin = maintenant

        ax.set_xlim(
            debut,
            fin
        )

        ax.xaxis.set_major_locator(
            mdates.DayLocator(
                interval=1
            )
        )

        ax.xaxis.set_major_formatter(
            mdates.DateFormatter(
                "%d/%m"
            )
        )

    elif periode_actuelle == "1 mois":

        debut = maintenant - timedelta(
            days=29
        )

        fin = maintenant

        ax.set_xlim(
            debut,
            fin
        )

        # Chaque jour est affiché.
        ax.xaxis.set_major_locator(
            mdates.DayLocator(
                interval=1
            )
        )

        ax.xaxis.set_major_formatter(
            mdates.DateFormatter(
                "%d/%m"
            )
        )

    elif periode_actuelle == "1 an":

        debut = maintenant - timedelta(
            days=365
        )

        fin = maintenant

        ax.set_xlim(
            debut,
            fin
        )

        ax.xaxis.set_major_locator(
            mdates.MonthLocator(
                interval=1
            )
        )

        ax.xaxis.set_major_formatter(
            mdates.DateFormatter(
                "%m/%Y"
            )
        )

    else:

        # Depuis toujours
        dates_min = None

        for ligne in lignes_graphique:

            x = ligne.get_xdata()

            if len(x) > 0:

                x_valides = [
                    x_value
                    for x_value in x
                    if np.isfinite(x_value)
                ]

                if x_valides:

                    minimum = min(
                        x_valides
                    )

                    if (
                        dates_min is None
                        or minimum < dates_min
                    ):
                        dates_min = minimum

        if dates_min is not None:

            ax.set_xlim(
                mdates.num2date(
                    dates_min
                ).replace(tzinfo=None),
                maintenant
            )

        ax.xaxis.set_major_locator(
            mdates.AutoDateLocator(
                maxticks=12
            )
        )

        ax.xaxis.set_major_formatter(
            mdates.DateFormatter(
                "%m/%Y"
            )
        )

    ax.tick_params(
        axis="x",
        labelrotation=45,
        labelsize=8,
        colors=theme["texte_secondaire"]
    )

    ax.tick_params(
        axis="y",
        labelsize=9,
        colors=theme["texte_secondaire"]
    )


# ============================================================
# AFFICHAGE DU GRAPHIQUE
# ============================================================

def afficher_graphique(donnees):

    global lignes_graphique
    global tooltip

    ax.clear()

    lignes_graphique = []

    ax.set_facecolor(
        theme["graph_fond"]
    )

    figure.patch.set_facecolor(
        theme["graph_fond"]
    )

    ax.grid(
        True,
        color=theme["graph_grille"],
        alpha=0.35,
        linewidth=0.7
    )

    for index, nom in enumerate(actions_selectionnees):

        if nom not in donnees:
            continue

        serie = donnees[nom]

        if serie is None or len(serie) == 0:
            continue

        dates = convertir_dates_france(
            serie.index
        )

        valeurs = np.asarray(
            serie.values,
            dtype=float
        )

        dates, valeurs = filtrer_donnees(
            dates,
            valeurs
        )

        if len(dates) == 0:
            continue

        dates_graphique, valeurs_graphique = couper_weekends(
            dates,
            valeurs
        )

        couleur = couleur_action(
            index
        )

        ligne, = ax.plot(
            dates_graphique,
            valeurs_graphique,
            color=couleur,
            linewidth=1.8,
            alpha=0.96,
            solid_capstyle="round",
            solid_joinstyle="round",
            antialiased=True,
            picker=7
        )

        ligne.nom_action = nom

        lignes_graphique.append(
            ligne
        )

    # --------------------------------------------------------
    # TITRE
    # --------------------------------------------------------

    ax.set_title(
        f"Évolution des valeurs — {periode_actuelle}",
        fontsize=15,
        fontweight="bold",
        color=theme["texte"],
        pad=15
    )

    ax.set_ylabel(
        "Cours (€)",
        color=theme["texte_secondaire"],
        fontsize=10
    )

    ax.set_xlabel(
        "",
        color=theme["texte_secondaire"]
    )

    # --------------------------------------------------------
    # AXE DES DATES
    # --------------------------------------------------------

    configurer_axe_dates()

    # --------------------------------------------------------
    # BORDURES
    # --------------------------------------------------------

    for bordure in ax.spines.values():

        bordure.set_color(
            theme["graph_grille"]
        )

    # --------------------------------------------------------
    # MISE EN PAGE
    # --------------------------------------------------------

    figure.subplots_adjust(
        left=0.06,
        right=0.98,
        top=0.91,
        bottom=0.16
    )

    # --------------------------------------------------------
    # TOOLTIP
    # --------------------------------------------------------

    tooltip = ax.annotate(
        "",
        xy=(0, 0),
        xytext=(15, 15),
        textcoords="offset points",

        bbox=dict(
            boxstyle="round,pad=0.5",
            fc=theme["panneau"],
            ec=theme["bordure"],
            alpha=0.96
        ),

        color=theme["texte"],
        fontsize=9
    )

    tooltip.set_visible(
        False
    )

    canvas_graphique.draw_idle()


# ============================================================
# TOOLTIP AU SURVOL
# ============================================================

def afficher_tooltip(event):

    global tooltip

    if (
        event.inaxes != ax
        or not lignes_graphique
    ):
        if tooltip is not None:
            tooltip.set_visible(False)
            canvas_graphique.draw_idle()

        return

    meilleur = None
    meilleure_distance = float("inf")

    for ligne in lignes_graphique:

        try:

            contient, info = ligne.contains(
                event
            )

            if contient:

                xdata = ligne.get_xdata()
                ydata = ligne.get_ydata()

                index = info["ind"][0]

                if index < len(xdata):

                    distance = abs(
                        xdata[index] - event.xdata
                    )

                    if distance < meilleure_distance:

                        meilleure_distance = distance

                        meilleur = (
                            ligne,
                            index
                        )

        except Exception:
            pass

    if meilleur is None:

        if tooltip is not None:
            tooltip.set_visible(False)

        canvas_graphique.draw_idle()

        return

    ligne, index = meilleur

    x = ligne.get_xdata()[index]
    y = ligne.get_ydata()[index]

    if not np.isfinite(x) or not np.isfinite(y):

        tooltip.set_visible(False)
        canvas_graphique.draw_idle()

        return

    date = mdates.num2date(
        x
    ).replace(
        tzinfo=None
    )

    if periode_actuelle in [
        "1 an",
        "Depuis toujours"
    ]:

        date_texte = date.strftime(
            "%d/%m/%Y"
        )

    else:

        date_texte = date.strftime(
            "%d/%m/%Y %H:%M"
        )

    texte = (
        f"{ligne.nom_action}\n"
        f"{date_texte}\n"
        f"{y:.2f} €"
    )

    tooltip.xy = (
        x,
        y
    )

    tooltip.set_text(
        texte
    )

    tooltip.set_visible(
        True
    )

    canvas_graphique.draw_idle()


canvas_graphique.mpl_connect(
    "motion_notify_event",
    afficher_tooltip
)


# ============================================================
# TÉLÉCHARGEMENT DES DONNÉES
# ============================================================

def telecharger_donnees():

    donnees = {}

    configuration = periodes[
        periode_actuelle
    ]

    for nom in actions_selectionnees:

        try:

            ticker = actions_cac40[
                nom
            ]

            data = yf.download(
                ticker,
                period=configuration["period"],
                interval=configuration["interval"],
                auto_adjust=False,
                progress=False,
                threads=False
            )

            if data is None or data.empty:

                continue

            if "Close" not in data.columns:

                continue

            cours = data["Close"]

            # Dans certains cas yfinance renvoie
            # un DataFrame au lieu d'une série.

            if isinstance(
                cours,
                pd.DataFrame
            ):

                if ticker in cours.columns:

                    cours = cours[ticker]

                else:

                    cours = cours.iloc[:, 0]

            cours = cours.dropna()

            if len(cours) == 0:
                continue

            donnees[nom] = cours

        except Exception as erreur:

            print(
                f"Erreur pour {nom} : {erreur}"
            )

    return donnees


# ============================================================
# ACTUALISATION
# ============================================================

def actualiser():

    global chargement

    if chargement:
        return

    chargement = True

    statut.config(
        text="Téléchargement des données..."
    )

    bouton_actualiser_canvas.config(
        state="disabled"
    )

    thread = threading.Thread(
        target=actualiser_thread,
        daemon=True
    )

    thread.start()


def actualiser_thread():

    try:

        donnees = telecharger_donnees()

        fenetre.after(
            0,
            lambda: actualisation_terminee(
                donnees
            )
        )

    except Exception as erreur:

        fenetre.after(
            0,
            lambda: actualisation_erreur(
                erreur
            )
        )


def actualisation_terminee(donnees):

    global chargement

    chargement = False

    bouton_actualiser_canvas.config(
        state="normal"
    )

    if donnees:

        afficher_graphique(
            donnees
        )

        maintenant = datetime.now().strftime(
            "%d/%m/%Y %H:%M"
        )

        statut.config(
            text=f"Dernière actualisation : {maintenant}"
        )

    else:

        afficher_graphique(
            {}
        )

        statut.config(
            text="Aucune donnée disponible."
        )

    reconstruire_legende()


def actualisation_erreur(erreur):

    global chargement

    chargement = False

    bouton_actualiser_canvas.config(
        state="normal"
    )

    statut.config(
        text="Erreur pendant le téléchargement."
    )

    print(
        "Erreur :",
        erreur
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
# POPUP SÉLECTION DES ACTIONS
# ============================================================

def ouvrir_selection_actions():

    popup = tk.Toplevel(
        fenetre
    )

    popup.title(
        "Choisir les valeurs"
    )

    popup.geometry(
        "850x760"
    )

    popup.minsize(
        700,
        600
    )

    popup.configure(
        bg=theme["fond_bas"]
    )

    popup.transient(
        fenetre
    )

    # --------------------------------------------------------
    # TITRE
    # --------------------------------------------------------

    titre_popup = tk.Label(
        popup,
        text="Valeurs du CAC 40",
        font=("Segoe UI", 20, "bold"),
        bg=theme["fond_bas"],
        fg=theme["texte"]
    )

    titre_popup.pack(
        pady=(20, 5)
    )

    sous_titre_popup = tk.Label(
        popup,
        text="Sélectionne les valeurs que tu veux afficher.",
        font=("Segoe UI", 10),
        bg=theme["fond_bas"],
        fg=theme["texte_secondaire"]
    )

    sous_titre_popup.pack(
        pady=(0, 15)
    )

    # --------------------------------------------------------
    # BOUTONS TOUT / RIEN
    # --------------------------------------------------------

    barre_selection = tk.Frame(
        popup,
        bg=theme["fond_bas"]
    )

    barre_selection.pack(
        fill="x",
        padx=20,
        pady=(0, 10)
    )

    def tout_selectionner():

        for nom in variables:

            variables[nom].set(
                True
            )

    def tout_deselectionner():

        for nom in variables:

            variables[nom].set(
                False
            )

    creer_bouton_verre(
        barre_selection,
        "Tout sélectionner",
        tout_selectionner,
        largeur=175
    )

    creer_bouton_verre(
        barre_selection,
        "Tout désélectionner",
        tout_deselectionner,
        largeur=185
    )

    # --------------------------------------------------------
    # ZONE SCROLLABLE
    # --------------------------------------------------------

    cadre_scroll = tk.Frame(
        popup,
        bg=theme["panneau"]
    )

    cadre_scroll.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=5
    )

    canvas_scroll = tk.Canvas(
        cadre_scroll,
        bg=theme["panneau"],
        highlightthickness=0,
        bd=0
    )

    scrollbar = tk.Scrollbar(
        cadre_scroll,
        orient="vertical",
        command=canvas_scroll.yview
    )

    contenu_scroll = tk.Frame(
        canvas_scroll,
        bg=theme["panneau"]
    )

    contenu_scroll.bind(
        "<Configure>",
        lambda event: canvas_scroll.configure(
            scrollregion=canvas_scroll.bbox("all")
        )
    )

    canvas_scroll.create_window(
        (0, 0),
        window=contenu_scroll,
        anchor="nw"
    )

    canvas_scroll.configure(
        yscrollcommand=scrollbar.set
    )

    canvas_scroll.pack(
        side="left",
        fill="both",
        expand=True
    )

    scrollbar.pack(
        side="right",
        fill="y"
    )

    # --------------------------------------------------------
    # VARIABLES
    # --------------------------------------------------------

    variables = {}

    noms = list(
        actions_cac40.keys()
    )

    for nom in noms:

        variables[nom] = tk.BooleanVar(
            value=nom in actions_selectionnees
        )

    # --------------------------------------------------------
    # CHECKBUTTONS
    # --------------------------------------------------------

    for index, nom in enumerate(noms):

        colonne = index % 2
        ligne = index // 2

        check = tk.Checkbutton(
            contenu_scroll,
            text=nom,
            variable=variables[nom],

            font=("Segoe UI", 10),

            bg=theme["panneau"],
            fg=theme["texte"],

            activebackground=theme["panneau"],
            activeforeground=theme["texte"],

            selectcolor=theme["accent"],

            highlightthickness=0,
            bd=0,

            takefocus=0,

            anchor="w"
        )

        check.grid(
            row=ligne,
            column=colonne,
            sticky="ew",
            padx=15,
            pady=6
        )

    contenu_scroll.grid_columnconfigure(
        0,
        weight=1
    )

    contenu_scroll.grid_columnconfigure(
        1,
        weight=1
    )

    # --------------------------------------------------------
    # VALIDER
    # --------------------------------------------------------

    def valider():

        global actions_selectionnees

        actions_selectionnees = [
            nom
            for nom in noms
            if variables[nom].get()
        ]

        popup.destroy()

        reconstruire_legende()

        actualiser()

    bouton_valider = tk.Button(
        popup,
        text="Afficher les valeurs",
        command=valider,

        font=("Segoe UI", 11, "bold"),

        bg=theme["accent"],
        fg="white",

        activebackground=theme["accent_hover"],
        activeforeground="white",

        bd=0,
        relief="flat",

        padx=25,
        pady=10,

        cursor="hand2",

        highlightthickness=0
    )

    bouton_valider.pack(
        pady=15
    )


# ============================================================
# POPUP WEEK-END
# ============================================================

def afficher_popup_weekend():

    global popup_weekend_deja_affiche

    if popup_weekend_deja_affiche:
        return

    # 5 = samedi
    # 6 = dimanche

    if datetime.now().weekday() < 5:
        return

    popup_weekend_deja_affiche = True

    popup = tk.Toplevel(
        fenetre
    )

    popup.title(
        "Bourse fermée"
    )

    popup.geometry(
        "480x260"
    )

    popup.resizable(
        False,
        False
    )

    popup.configure(
        bg=theme["panneau"]
    )

    popup.transient(
        fenetre
    )

    # --------------------------------------------------------
    # ICÔNE
    # --------------------------------------------------------

    icone = tk.Label(
        popup,
        text="📈",
        font=("Segoe UI Emoji", 34),
        bg=theme["panneau"],
        fg=theme["texte"]
    )

    icone.pack(
        pady=(20, 5)
    )

    # --------------------------------------------------------
    # MESSAGE
    # --------------------------------------------------------

    message = tk.Label(
        popup,
        text=(
            "La Bourse de Paris est fermée ce week-end.\n\n"
            "Les cotations reprendront lundi."
        ),
        font=("Segoe UI", 12),
        bg=theme["panneau"],
        fg=theme["texte"],
        justify="center"
    )

    message.pack(
        pady=5
    )

    # --------------------------------------------------------
    # BOUTON
    # --------------------------------------------------------

    bouton_ok = tk.Button(
        popup,
        text="OK",
        command=popup.destroy,

        font=("Segoe UI", 10, "bold"),

        bg=theme["accent"],
        fg="white",

        activebackground=theme["accent_hover"],
        activeforeground="white",

        bd=0,
        relief="flat",

        padx=35,
        pady=8,

        highlightthickness=0,

        cursor="hand2"
    )

    bouton_ok.pack(
        pady=15
    )


# ============================================================
# APPLICATION DU THÈME
# ============================================================

def appliquer_theme():

    global theme

    theme = themes[
        theme_actuel
    ]

    fenetre.configure(
        bg=theme["fond"]
    )

    canvas_fond.configure(
        bg=theme["fond"]
    )

    conteneur.configure(
        bg=theme["fond_bas"]
    )

    cadre_titre.configure(
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

    barre_controles.configure(
        bg=theme["fond_bas"]
    )

    label_periode.configure(
        bg=theme["fond_bas"],
        fg=theme["texte"]
    )

    cadre_graphique.configure(
        bg=theme["panneau"]
    )

    legende_externe.configure(
        bg=theme["panneau2"]
    )

    legende_interne.configure(
        bg=theme["panneau2"]
    )

    barre_bas.configure(
        bg=theme["fond_bas"]
    )

    statut.configure(
        bg=theme["fond_bas"],
        fg=theme["texte_secondaire"]
    )

    # Recoloration des boutons Canvas

    for widget in barre_controles.winfo_children():

        if isinstance(
            widget,
            tk.Canvas
        ):

            try:

                largeur = int(
                    widget.cget("width")
                )

                hauteur = int(
                    widget.cget("height")
                )

                # Récupération du texte existant
                objets = widget.find_all()

                texte = ""

                for objet in objets:

                    if widget.type(objet) == "text":

                        texte = widget.itemcget(
                            objet,
                            "text"
                        )

                        break

                if texte:

                    dessiner_bouton(
                        widget,
                        largeur,
                        hauteur,
                        theme["verre"],
                        texte,
                        theme["texte"]
                    )

            except Exception:
                pass

    for widget in barre_bas.winfo_children():

        if isinstance(
            widget,
            tk.Canvas
        ):

            try:

                largeur = int(
                    widget.cget("width")
                )

                hauteur = int(
                    widget.cget("height")
                )

                objets = widget.find_all()

                texte = ""

                for objet in objets:

                    if widget.type(objet) == "text":

                        texte = widget.itemcget(
                            objet,
                            "text"
                        )

                        break

                if texte:

                    dessiner_bouton(
                        widget,
                        largeur,
                        hauteur,
                        theme["verre"],
                        texte,
                        theme["texte"]
                    )

            except Exception:
                pass

    dessiner_fond()

    reconstruire_legende()

    if ax is not None:

        ax.set_facecolor(
            theme["graph_fond"]
        )

        figure.patch.set_facecolor(
            theme["graph_fond"]
        )

        for bordure in ax.spines.values():

            bordure.set_color(
                theme["graph_grille"]
            )

        ax.tick_params(
            colors=theme["texte_secondaire"]
        )

        ax.grid(
            True,
            color=theme["graph_grille"],
            alpha=0.35
        )

        ax.title.set_color(
            theme["texte"]
        )

        ax.yaxis.label.set_color(
            theme["texte_secondaire"]
        )

        canvas_graphique.draw_idle()


# ============================================================
# REDIMENSIONNEMENT DU GRAPHIQUE
# ============================================================

def adapter_graphique(event=None):

    try:

        largeur = cadre_graphique.winfo_width()
        hauteur = cadre_graphique.winfo_height()

        if largeur < 300 or hauteur < 250:
            return

        largeur_pouces = max(
            largeur / 120,
            8
        )

        hauteur_pouces = max(
            hauteur / 120,
            4.5
        )

        figure.set_size_inches(
            largeur_pouces,
            hauteur_pouces,
            forward=False
        )

        canvas_graphique.draw_idle()

    except Exception:
        pass


cadre_graphique.bind(
    "<Configure>",
    adapter_graphique
)


# ============================================================
# INITIALISATION
# ============================================================

appliquer_theme()

reconstruire_legende()

# Première actualisation
fenetre.after(
    300,
    actualiser
)

# Popup du week-end
fenetre.after(
    1200,
    afficher_popup_weekend
)

# Actualisation automatique toutes les heures
fenetre.after(
    60 * 60 * 1000,
    actualisation_automatique
)


# ============================================================
# LANCEMENT
# ============================================================

fenetre.mainloop()
