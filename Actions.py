```python
import tkinter as tk
from tkinter import ttk
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

# Actualisation automatique toutes les 1 heure
INTERVALLE_ACTUALISATION = 60 * 60 * 1000


# ============================================================
# PÉRIODES DISPONIBLES
# ============================================================

periodes = {
    "24 h": {
        "period": "5d",
        "interval": "15m"
    },

    "2 semaines": {
        "period": "1mo",
        "interval": "1h"
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

titre.pack(pady=(18, 0))


sous_titre = tk.Label(
    fenetre,
    text="Thales • Airbus • Vinci",
    font=("Segoe UI", 11),
    fg=GRIS,
    bg=FOND
)

sous_titre.pack(pady=(2, 10))


# ============================================================
# BARRE DES OPTIONS
# ============================================================

cadre_options = tk.Frame(
    fenetre,
    bg=FOND
)

cadre_options.pack(
    fill="x",
    padx=20,
    pady=(0, 8)
)


# Texte période

label_periode = tk.Label(
    cadre_options,
    text="Période :",
    font=("Segoe UI", 10, "bold"),
    fg=BLANC,
    bg=FOND
)

label_periode.pack(
    side="left",
    padx=(5, 8)
)


# ============================================================
# MENU PÉRIODE
# ============================================================

style = ttk.Style()

try:
    style.theme_use("clam")
except:
    pass

style.configure(
    "TCombobox",
    fieldbackground=FOND2,
    background=FOND2,
    foreground=BLANC
)


menu_periode = ttk.Combobox(
    cadre_options,
    values=list(periodes.keys()),
    state="readonly",
    width=18
)

menu_periode.set("24 h")

menu_periode.pack(
    side="left"
)


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
# STATUT
# ============================================================

statut = tk.Label(
    cadre_bas,
    text="Démarrage...",
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
# VARIABLES DU GRAPHIQUE
# ============================================================

lignes = {}

annotations = []

donnees_actuelles = {}


# ============================================================
# RÉCUPÉRATION DES DONNÉES
# ============================================================

def recuperer_donnees():

    global periode_actuelle

    configuration = periodes[periode_actuelle]

    period = configuration["period"]
    interval = configuration["interval"]

    donnees = {}

    for nom, symbole in actions.items():

        try:

            print(
                f"Téléchargement de {nom} "
                f"({period}, {interval})..."
            )

            data = yf.download(
                symbole,
                period=period,
                interval=interval,
                auto_adjust=False,
                progress=False,
                threads=False
            )

            donnees[nom] = data

        except Exception as erreur:

            print(
                "Erreur pour",
                nom,
                ":",
                erreur
            )

            donnees[nom] = None

    return donnees


# ============================================================
# AFFICHER LE GRAPHIQUE
# ============================================================

def afficher_graphique(donnees):

    global lignes
    global annotations
    global donnees_actuelles

    donnees_actuelles = donnees

    # --------------------------------------------------------
    # Supprimer les anciennes annotations
    # --------------------------------------------------------

    for annotation in annotations:

        try:
            annotation.remove()
        except:
            pass

    annotations = []

    lignes = {}

    # --------------------------------------------------------
    # Nettoyer le graphique
    # --------------------------------------------------------

    ax.clear()

    ax.set_facecolor(FOND2)

    nombre_actions = 0

    toutes_les_dates = []


    # ========================================================
    # TRACER CHAQUE ACTION
    # ========================================================

    for nom in actions:

        data = donnees.get(nom)

        if data is None or data.empty:
            continue


        try:

            # ------------------------------------------------
            # Récupération du cours de clôture
            # ------------------------------------------------

            cours = data["Close"]


            # yfinance peut renvoyer un DataFrame
            # au lieu d'une Series.

            if hasattr(cours, "columns"):

                cours = cours.iloc[:, 0]


            # Supprimer les valeurs vides

            cours = cours.dropna()


            if len(cours) == 0:
                continue


            dates = cours.index

            valeurs = np.array(
                cours.values,
                dtype=float
            )


            # ------------------------------------------------
            # Tracer la courbe
            # ------------------------------------------------

            ligne, = ax.plot(
                dates,
                valeurs,
                label=nom,
                color=couleurs[nom],
                linewidth=2.5,
                marker="o",
                markersize=3,
                picker=8
            )


            # ------------------------------------------------
            # Sauvegarder les informations
            # ------------------------------------------------

            lignes[nom] = {
                "ligne": ligne,
                "dates": dates,
                "valeurs": valeurs
            }


            toutes_les_dates.extend(dates)

            nombre_actions += 1


        except Exception as erreur:

            print(
                "Erreur graphique",
                nom,
                ":",
                erreur
            )


    # ========================================================
    # TITRE
    # ========================================================

    ax.set_title(
        f"Évolution des actions — {periode_actuelle}",
        color=BLANC,
        fontsize=15,
        fontweight="bold",
        pad=15
    )


    # ========================================================
    # AXES
    # ========================================================

    ax.set_xlabel(
        "Date et heure",
        color=BLANC,
        fontsize=11
    )

    ax.set_ylabel(
        "Prix (€)",
        color=BLANC,
        fontsize=11
    )


    # ========================================================
    # FORMAT DE L'AXE TEMPOREL
    # ========================================================

    if periode_actuelle == "24 h":

        ax.xaxis.set_major_formatter(
            mdates.DateFormatter("%H:%M")
        )

    elif periode_actuelle == "2 semaines":

        ax.xaxis.set_major_formatter(
            mdates.DateFormatter("%d/%m %H:%M")
        )

    elif periode_actuelle == "1 mois":

        ax.xaxis.set_major_formatter(
            mdates.DateFormatter("%d/%m")
        )

    else:

        ax.xaxis.set_major_formatter(
            mdates.DateFormatter("%m/%Y")
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

    heure = datetime.now().strftime(
        "%d/%m/%Y %H:%M:%S"
    )

    ax.text(
        0.99,
        0.02,
        "Actualisé : " + heure,
        transform=ax.transAxes,
        color=GRIS,
        fontsize=9,
        ha="right"
    )


    # ========================================================
    # AJUSTEMENT
    # ========================================================

    figure.autofmt_xdate()

    figure.tight_layout()

    canvas.draw_idle()


# ============================================================
# SURVOL DE LA SOURIS
# ============================================================

def afficher_info_souris(event):

    global annotations

    # --------------------------------------------------------
    # Supprimer l'ancienne info
    # --------------------------------------------------------

    for annotation in annotations:

        try:
            annotation.remove()
        except:
            pass

    annotations = []


    # --------------------------------------------------------
    # Vérifier que la souris est dans le graphique
    # --------------------------------------------------------

    if event.inaxes != ax:

        canvas.draw_idle()

        return


    if event.x is None or event.y is None:

        return


    meilleure_distance = float("inf")

    meilleure_info = None


    # ========================================================
    # CHERCHER LA COURBE LA PLUS PROCHE
    # ========================================================

    for nom, infos in lignes.items():

        ligne = infos["ligne"]

        dates = infos["dates"]

        valeurs = infos["valeurs"]


        # ----------------------------------------------------
        # Vérifier si la souris est proche de la ligne
        # ----------------------------------------------------

        try:

            contient, details = ligne.contains(event)

        except:

            contient = False


        if not contient:

            continue


        # ----------------------------------------------------
        # Trouver le point le plus proche
        # ----------------------------------------------------

        x_points = mdates.date2num(dates)

        # Transformation en coordonnées écran

        points = np.column_stack(
            [x_points, valeurs]
        )

        points_ecran = ax.transData.transform(points)


        distances = np.sqrt(
            (points_ecran[:, 0] - event.x) ** 2
            +
            (points_ecran[:, 1] - event.y) ** 2
        )


        index = np.argmin(distances)

        distance = distances[index]


        if distance < meilleure_distance:

            meilleure_distance = distance

            meilleure_info = (
                nom,
                dates[index],
                valeurs[index],
                x_points[index]
            )


    # ========================================================
    # AUCUNE COURBE
    # ========================================================

    if meilleure_info is None:

        canvas.draw_idle()

        return


    # ========================================================
    # INFORMATIONS
    # ========================================================

    nom, date, valeur, x_point = meilleure_info


    # ========================================================
    # CRÉER L'INFO-BULLE
    # ========================================================

    texte = (
        f"{nom}\n"
        f"Date : {date.strftime('%d/%m/%Y')}\n"
        f"Heure : {date.strftime('%H:%M')}\n"
        f"Valeur : {valeur:.2f} €"
    )


    annotation = ax.annotate(
        texte,
        xy=(x_point, valeur),
        xytext=(15, 15),
        textcoords="offset points",
        color=BLANC,
        fontsize=10,
        fontweight="bold",
        bbox=dict(
            boxstyle="round,pad=0.5",
            facecolor=FOND,
            edgecolor=couleurs[nom],
            alpha=0.95
        ),
        arrowprops=dict(
            arrowstyle="->",
            color=couleurs[nom]
        )
    )


    annotations.append(annotation)

    canvas.draw_idle()


# ============================================================
# ÉVÉNEMENT SOURIS
# ============================================================

canvas.mpl_connect(
    "motion_notify_event",
    afficher_info_souris
)


# ============================================================
# ACTUALISATION
# ============================================================

def actualiser():

    bouton_actualiser.config(
        state="disabled",
        text="⟳  Chargement..."
    )


    statut.config(
        text=(
            f"Récupération des données "
            f"({periode_actuelle})..."
        ),
        fg=GRIS
    )


    # --------------------------------------------------------
    # Téléchargement en arrière-plan
    # --------------------------------------------------------

    def telechargement():

        donnees = recuperer_donnees()


        # Retour dans le thread principal

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
# FIN ACTUALISATION
# ============================================================

def terminer_actualisation(donnees):

    afficher_graphique(donnees)


    bouton_actualiser.config(
        state="normal",
        text="⟳  Actualiser"
    )


    heure = datetime.now().strftime(
        "%H:%M:%S"
    )


    statut.config(
        text=f"✓ Données mises à jour à {heure}",
        fg=VERT
    )


# ============================================================
# CHANGEMENT DE PÉRIODE
# ============================================================

def changer_periode(event=None):

    global periode_actuelle

    nouvelle_periode = menu_periode.get()


    if nouvelle_periode not in periodes:

        return


    # Si la période n'a pas changé

    if nouvelle_periode == periode_actuelle:

        return


    periode_actuelle = nouvelle_periode


    # Recharger automatiquement les données

    actualiser()


# ============================================================
# ACTUALISATION AUTOMATIQUE
# ============================================================

def actualisation_automatique():

    print("Actualisation automatique...")

    actualiser()


    # Programmer la prochaine actualisation
    # dans 1 heure

    fenetre.after(
        INTERVALLE_ACTUALISATION,
        actualisation_automatique
    )


# ============================================================
# CONNEXION DU MENU
# ============================================================

menu_periode.bind(
    "<<ComboboxSelected>>",
    changer_periode
)


# ============================================================
# CONNEXION DU BOUTON
# ============================================================

bouton_actualiser.config(
    command=actualiser
)


# ============================================================
# PREMIÈRE ACTUALISATION
# ============================================================

# L'application récupère automatiquement
# les données au démarrage.

actualiser()


# ============================================================
# PROGRAMMER L'ACTUALISATION AUTOMATIQUE
# ============================================================

fenetre.after(
    INTERVALLE_ACTUALISATION,
    actualisation_automatique
)


# ============================================================
# LANCEMENT
# ============================================================

fenetre.mainloop()
```

