import tkinter as tk
from tkinter import messagebox
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import threading
import numpy as np


# ============================================================
# ACTIONS DU CAC 40
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


actions_selectionnees = {
    "Thales",
    "Airbus",
    "Vinci"
}


couleurs = [
    "#00ff66",
    "#00ccff",
    "#ffcc00",
    "#ff5555",
    "#aa66ff",
    "#ff66cc",
    "#66ffff",
    "#ff9900",
    "#66ff33",
    "#ffffff"
]


# ============================================================
# THEMES
# ============================================================

THEME_SOMBRE = {
    "fond": "#0b0b0d",
    "fond2": "#141416",
    "pilule": "#252529",
    "pilule_hover": "#35353a",
    "texte": "#ffffff",
    "gris": "#999999",
    "accent": "#00ff66",
    "graph_grid": "#777777",
    "graph_bordure": "#444444"
}


THEME_CLAIR = {
    "fond": "#f2f2f7",
    "fond2": "#ffffff",
    "pilule": "#ffffff",
    "pilule_hover": "#e2e2e7",
    "texte": "#111111",
    "gris": "#666666",
    "accent": "#008f4c",
    "graph_grid": "#aaaaaa",
    "graph_bordure": "#cccccc"
}


theme_sombre = True
theme = THEME_SOMBRE


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


periode_actuelle = "24 h"


# Actualisation automatique toutes les heures
INTERVALLE_ACTUALISATION = 60 * 60 * 1000


# ============================================================
# FENÊTRE
# ============================================================

fenetre = tk.Tk()

fenetre.title("CacVision")

fenetre.geometry("2000x1200")

fenetre.minsize(
    1200,
    750
)


# ============================================================
# VARIABLES
# ============================================================

lignes = {}

annotations = []

donnees_actuelles = {}

couleurs_actions = {}


# ============================================================
# CADRE PRINCIPAL
# ============================================================

cadre_principal = tk.Frame(fenetre)

cadre_principal.pack(
    fill="both",
    expand=True
)


# ============================================================
# TITRE
# ============================================================

titre = tk.Label(
    cadre_principal,
    text="📈  CacVision",
    font=("Segoe UI", 34, "bold")
)

titre.pack(
    pady=(25, 0)
)


sous_titre = tk.Label(
    cadre_principal,
    text="Suivi détaillé des valeurs du CAC 40",
    font=("Segoe UI", 14)
)

sous_titre.pack(
    pady=(3, 20)
)


# ============================================================
# BARRE D'OPTIONS
# ============================================================

cadre_options = tk.Frame(
    cadre_principal
)

cadre_options.pack(
    fill="x",
    padx=40,
    pady=(0, 15)
)


# ============================================================
# FONCTION POUR DESSINER UNE PILULE
# ============================================================

def dessiner_pilule(
    canvas,
    largeur,
    hauteur,
    couleur
):

    canvas.delete("fond")

    rayon = hauteur // 2

    canvas.create_rectangle(
        rayon,
        1,
        largeur - rayon,
        hauteur - 1,
        fill=couleur,
        outline="",
        tags="fond"
    )

    canvas.create_oval(
        1,
        1,
        hauteur - 1,
        hauteur - 1,
        fill=couleur,
        outline="",
        tags="fond"
    )

    canvas.create_oval(
        largeur - hauteur + 1,
        1,
        largeur - 1,
        hauteur - 1,
        fill=couleur,
        outline="",
        tags="fond"
    )


# ============================================================
# BOUTON PILULE
# ============================================================

def creer_pilule(
    parent,
    texte,
    commande,
    largeur=160,
    hauteur=46
):

    bouton = tk.Canvas(
        parent,
        width=largeur,
        height=hauteur,
        bg=theme["fond"],
        highlightthickness=0,
        bd=0,
        cursor="hand2"
    )

    dessiner_pilule(
        bouton,
        largeur,
        hauteur,
        theme["pilule"]
    )

    texte_id = bouton.create_text(
        largeur // 2,
        hauteur // 2,
        text=texte,
        fill=theme["texte"],
        font=("Segoe UI", 11, "bold")
    )


    def entrer(event):

        dessiner_pilule(
            bouton,
            largeur,
            hauteur,
            theme["pilule_hover"]
        )

        bouton.tag_raise("texte")


    def sortir(event):

        dessiner_pilule(
            bouton,
            largeur,
            hauteur,
            theme["pilule"]
        )

        bouton.tag_raise("texte")


    def cliquer(event):

        commande()


    bouton.bind(
        "<Enter>",
        entrer
    )

    bouton.bind(
        "<Leave>",
        sortir
    )

    bouton.bind(
        "<Button-1>",
        cliquer
    )


    bouton.pilule_largeur = largeur
    bouton.pilule_hauteur = hauteur
    bouton.pilule_texte_id = texte_id

    return bouton


# ============================================================
# BOUTON ACTIONS
# ============================================================

bouton_actions = creer_pilule(
    cadre_options,
    "☰  Actions",
    lambda: ouvrir_selection_actions(),
    170,
    48
)

bouton_actions.pack(
    side="left",
    padx=(0, 18)
)


# ============================================================
# SÉLECTEUR DE PÉRIODE
# ============================================================

label_periode = tk.Label(
    cadre_options,
    text="Période",
    font=("Segoe UI", 11, "bold")
)

label_periode.pack(
    side="left",
    padx=(0, 10)
)


# ============================================================
# PILULE PÉRIODE PERSONNALISÉE
# ============================================================

menu_ouvert = False


def afficher_menu_periode():

    global menu_ouvert

    if menu_ouvert:
        return

    menu_ouvert = True

    popup = tk.Toplevel(fenetre)

    popup.overrideredirect(True)

    popup.configure(
        bg=theme["fond2"]
    )

    x = menu_periode.winfo_rootx()

    y = (
        menu_periode.winfo_rooty()
        + menu_periode.winfo_height()
        + 5
    )

    popup.geometry(
        f"220x260+{x}+{y}"
    )

    cadre_popup = tk.Frame(
        popup,
        bg=theme["fond2"]
    )

    cadre_popup.pack(
        fill="both",
        expand=True,
        padx=8,
        pady=8
    )


    def choisir(periode):

        global periode_actuelle
        global menu_ouvert

        periode_actuelle = periode

        bouton_periode.itemconfig(
            texte_periode,
            text=periode
        )

        popup.destroy()

        menu_ouvert = False

        actualiser()


    for periode in periodes.keys():

        bouton = tk.Button(
            cadre_popup,
            text=periode,
            font=("Segoe UI", 11, "bold"),
            bg=theme["fond2"],
            fg=theme["texte"],
            activebackground=theme["pilule_hover"],
            activeforeground=theme["texte"],
            relief="flat",
            bd=0,
            cursor="hand2",
            anchor="w",
            padx=15,
            pady=8,
            command=lambda p=periode: choisir(p)
        )

        bouton.pack(
            fill="x"
        )


    def fermer(event=None):

        global menu_ouvert

        if popup.winfo_exists():

            popup.destroy()

        menu_ouvert = False


    popup.bind(
        "<FocusOut>",
        fermer
    )

    popup.focus_force()


# ============================================================
# BOUTON PÉRIODE
# ============================================================

bouton_periode = tk.Canvas(
    cadre_options,
    width=220,
    height=48,
    bg=theme["fond"],
    highlightthickness=0,
    bd=0,
    cursor="hand2"
)

dessiner_pilule(
    bouton_periode,
    220,
    48,
    theme["pilule"]
)


texte_periode = bouton_periode.create_text(
    110,
    24,
    text="24 h  ▾",
    fill=theme["texte"],
    font=("Segoe UI", 11, "bold")
)


bouton_periode.bind(
    "<Button-1>",
    lambda event: afficher_menu_periode()
)

bouton_periode.bind(
    "<Enter>",
    lambda event: dessiner_pilule(
        bouton_periode,
        220,
        48,
        theme["pilule_hover"]
    )
)

bouton_periode.bind(
    "<Leave>",
    lambda event: dessiner_pilule(
        bouton_periode,
        220,
        48,
        theme["pilule"]
    )
)

bouton_periode.pack(
    side="left"
)


# ============================================================
# BOUTON THÈME
# ============================================================

def changer_theme():

    global theme_sombre

    theme_sombre = not theme_sombre

    appliquer_theme()

    if donnees_actuelles:

        afficher_graphique(
            donnees_actuelles
        )


bouton_theme = creer_pilule(
    cadre_options,
    "☀  Clair",
    changer_theme,
    150,
    48
)

bouton_theme.pack(
    side="right"
)


label_theme = tk.Label(
    cadre_options,
    text="Apparence",
    font=("Segoe UI", 11, "bold")
)

label_theme.pack(
    side="right",
    padx=(0, 10)
)


# ============================================================
# CADRE GRAPHIQUE
# ============================================================

cadre_graphique = tk.Frame(
    cadre_principal
)

cadre_graphique.pack(
    fill="both",
    expand=True,
    padx=40,
    pady=5
)


# ============================================================
# GRAPHIQUE HAUTE RÉSOLUTION
# ============================================================

plt.rcParams["font.family"] = "Segoe UI"


figure, ax = plt.subplots(
    figsize=(16, 9),
    dpi=180
)


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
    cadre_principal
)

cadre_bas.pack(
    fill="x",
    padx=40,
    pady=(10, 25)
)


statut = tk.Label(
    cadre_bas,
    text="Démarrage...",
    font=("Segoe UI", 11)
)

statut.pack(
    side="left"
)


# ============================================================
# BOUTON ACTUALISER
# ============================================================

bouton_actualiser = creer_pilule(
    cadre_bas,
    "⟳  Actualiser",
    lambda: actualiser(),
    170,
    48
)

bouton_actualiser.pack(
    side="right"
)


# ============================================================
# ADAPTATION AUTOMATIQUE DE LA QUALITÉ
# ============================================================

def adapter_resolution(event=None):

    largeur = cadre_graphique.winfo_width()
    hauteur = cadre_graphique.winfo_height()

    if largeur <= 10 or hauteur <= 10:
        return

    dpi = 180

    largeur_pouces = largeur / dpi
    hauteur_pouces = hauteur / dpi

    figure.set_dpi(dpi)

    figure.set_size_inches(
        largeur_pouces,
        hauteur_pouces,
        forward=False
    )

    canvas.draw_idle()


cadre_graphique.bind(
    "<Configure>",
    adapter_resolution
)


# ============================================================
# RÉCUPÉRATION DES DONNÉES
# ============================================================

def recuperer_donnees():

    configuration = periodes[
        periode_actuelle
    ]

    period = configuration["period"]

    interval = configuration["interval"]

    donnees = {}


    for nom in actions_selectionnees:

        symbole = actions_cac40[nom]

        try:

            print(
                f"Téléchargement : {nom}"
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
# AFFICHAGE DU GRAPHIQUE
# ============================================================

def afficher_graphique(donnees):

    global lignes
    global annotations
    global donnees_actuelles
    global couleurs_actions


    donnees_actuelles = donnees


    for annotation in annotations:

        try:

            annotation.remove()

        except:

            pass


    annotations = []

    lignes = {}


    ax.clear()


    ax.set_facecolor(
        theme["fond2"]
    )

    figure.patch.set_facecolor(
        theme["fond2"]
    )


    couleurs_actions = {}


    for index, nom in enumerate(
        actions_selectionnees
    ):

        couleurs_actions[nom] = couleurs[
            index % len(couleurs)
        ]


    nombre_actions = 0


    for nom in actions_selectionnees:

        data = donnees.get(nom)


        if data is None or data.empty:

            continue


        try:

            cours = data["Close"]


            if hasattr(
                cours,
                "columns"
            ):

                cours = cours.iloc[:, 0]


            cours = cours.dropna()


            if len(cours) == 0:

                continue


            dates = cours.index


            valeurs = np.array(
                cours.values,
                dtype=float
            )


            couleur = couleurs_actions[nom]


            ligne, = ax.plot(
                dates,
                valeurs,
                label=nom,
                color=couleur,
                linewidth=2.2,
                marker="o",
                markersize=2.2,
                picker=8,
                antialiased=True
            )


            lignes[nom] = {
                "ligne": ligne,
                "dates": dates,
                "valeurs": valeurs
            }


            nombre_actions += 1


        except Exception as erreur:

            print(
                "Erreur graphique :",
                nom,
                erreur
            )


    # ========================================================
    # TITRE
    # ========================================================

    ax.set_title(
        f"CAC 40 — {periode_actuelle}",
        color=theme["texte"],
        fontsize=20,
        fontweight="bold",
        pad=20
    )


    ax.set_xlabel(
        "Date",
        color=theme["texte"],
        fontsize=12
    )


    ax.set_ylabel(
        "Prix (€)",
        color=theme["texte"],
        fontsize=12
    )


    # ========================================================
    # AXE DES DATES
    # ========================================================

    if periode_actuelle == "24 h":

        ax.xaxis.set_major_formatter(
            mdates.DateFormatter("%H:%M")
        )

        ax.xaxis.set_major_locator(
            mdates.AutoDateLocator(
                minticks=10,
                maxticks=20
            )
        )

    elif periode_actuelle == "1 semaine":

        ax.xaxis.set_major_formatter(
            mdates.DateFormatter(
                "%d/%m %H:%M"
            )
        )

    elif periode_actuelle == "1 mois":

        ax.xaxis.set_major_formatter(
            mdates.DateFormatter(
                "%d/%m"
            )
        )

    else:

        ax.xaxis.set_major_formatter(
            mdates.DateFormatter(
                "%m/%Y"
            )
        )


    # ========================================================
    # GRILLE
    # ========================================================

    ax.tick_params(
        axis="both",
        colors=theme["texte"],
        labelsize=10
    )


    ax.grid(
        True,
        which="major",
        color=theme["graph_grid"],
        alpha=0.28,
        linestyle="--",
        linewidth=0.9
    )


    ax.minorticks_on()


    ax.grid(
        True,
        which="minor",
        color=theme["graph_grid"],
        alpha=0.12,
        linestyle=":",
        linewidth=0.55
    )


    # ========================================================
    # BORDURES
    # ========================================================

    for bordure in ax.spines.values():

        bordure.set_color(
            theme["graph_bordure"]
        )


    # ========================================================
    # LÉGENDE
    # ========================================================

    if nombre_actions > 0:

        legend = ax.legend(
            loc="upper left",
            frameon=True,
            facecolor=theme["fond"],
            edgecolor=theme["graph_bordure"],
            fontsize=11
        )


        for texte in legend.get_texts():

            texte.set_color(
                theme["texte"]
            )


    # ========================================================
    # DATE DE MISE À JOUR
    # ========================================================

    heure = datetime.now().strftime(
        "%d/%m/%Y %H:%M:%S"
    )


    ax.text(
        0.99,
        0.02,
        "Actualisé : " + heure,
        transform=ax.transAxes,
        color=theme["gris"],
        fontsize=9,
        ha="right"
    )


    figure.autofmt_xdate()


    figure.tight_layout()


    canvas.draw_idle()


# ============================================================
# INFORMATIONS AU SURVOL
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

        canvas.draw_idle()

        return


    if event.x is None or event.y is None:

        return


    meilleure_distance = float(
        "inf"
    )

    meilleure_info = None


    for nom, infos in lignes.items():

        ligne = infos["ligne"]

        dates = infos["dates"]

        valeurs = infos["valeurs"]


        try:

            contient, details = ligne.contains(
                event
            )

        except:

            contient = False


        if not contient:

            continue


        try:

            x_points = mdates.date2num(
                dates
            )


            points = np.column_stack(
                [
                    x_points,
                    valeurs
                ]
            )


            points_ecran = ax.transData.transform(
                points
            )


            distances = np.sqrt(
                (points_ecran[:, 0] - event.x) ** 2
                +
                (points_ecran[:, 1] - event.y) ** 2
            )


            index = np.argmin(
                distances
            )


            distance = distances[index]


        except:

            continue


        if distance < meilleure_distance:

            meilleure_distance = distance

            meilleure_info = (
                nom,
                dates[index],
                valeurs[index],
                x_points[index]
            )


    if meilleure_info is None:

        canvas.draw_idle()

        return


    nom, date, valeur, x_point = meilleure_info


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
        color=theme["texte"],
        fontsize=11,
        fontweight="bold",
        bbox=dict(
            boxstyle="round,pad=0.6",
            facecolor=theme["fond"],
            edgecolor=couleurs_actions[nom],
            alpha=0.96
        ),
        arrowprops=dict(
            arrowstyle="->",
            color=couleurs_actions[nom]
        )
    )


    annotations.append(
        annotation
    )


    canvas.draw_idle()


canvas.mpl_connect(
    "motion_notify_event",
    afficher_info_souris
)


# ============================================================
# ACTUALISATION
# ============================================================

def actualiser():

    bouton_actualiser.itemconfig(
        bouton_actualiser.pilule_texte_id,
        text="⟳  Chargement..."
    )


    statut.config(
        text=(
            f"Récupération des données "
            f"({periode_actuelle})..."
        ),
        fg=theme["gris"]
    )


    def telechargement():

        donnees = recuperer_donnees()


        fenetre.after(
            0,
            lambda: terminer_actualisation(
                donnees
            )
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

    afficher_graphique(
        donnees
    )


    bouton_actualiser.itemconfig(
        bouton_actualiser.pilule_texte_id,
        text="⟳  Actualiser"
    )


    heure = datetime.now().strftime(
        "%H:%M:%S"
    )


    statut.config(
        text=f"✓ Mis à jour à {heure}",
        fg=theme["accent"]
    )


# ============================================================
# SÉLECTION DES ACTIONS
# ============================================================

def ouvrir_selection_actions():

    fenetre_selection = tk.Toplevel(
        fenetre
    )


    fenetre_selection.title(
        "Choisir les actions"
    )


    fenetre_selection.geometry(
        "800x800"
    )


    fenetre_selection.configure(
        bg=theme["fond"]
    )


    # ========================================================
    # TITRE
    # ========================================================

    titre_selection = tk.Label(
        fenetre_selection,
        text="Choisir les actions",
        font=("Segoe UI", 24, "bold"),
        bg=theme["fond"],
        fg=theme["texte"]
    )


    titre_selection.pack(
        pady=(25, 5)
    )


    sous_titre_selection = tk.Label(
        fenetre_selection,
        text="Sélectionne les valeurs à afficher",
        font=("Segoe UI", 11),
        bg=theme["fond"],
        fg=theme["gris"]
    )


    sous_titre_selection.pack(
        pady=(0, 20)
    )


    # ========================================================
    # LISTE
    # ========================================================

    cadre_liste = tk.Frame(
        fenetre_selection,
        bg=theme["fond2"]
    )


    cadre_liste.pack(
        fill="both",
        expand=True,
        padx=30,
        pady=10
    )


    canvas_selection = tk.Canvas(
        cadre_liste,
        bg=theme["fond2"],
        highlightthickness=0
    )


    scrollbar = tk.Scrollbar(
        cadre_liste,
        orient="vertical",
        command=canvas_selection.yview
    )


    cadre_cases = tk.Frame(
        canvas_selection,
        bg=theme["fond2"]
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


    variables_actions = {}


    # ========================================================
    # CASES
    # ========================================================

    for index, nom in enumerate(
        actions_cac40.keys()
    ):

        variable = tk.BooleanVar(
            value=nom in actions_selectionnees
        )


        variables_actions[nom] = variable


        case = tk.Checkbutton(
            cadre_cases,
            text=nom,
            variable=variable,
            anchor="w",
            font=("Segoe UI", 11),
            bg=theme["fond2"],
            fg=theme["texte"],
            selectcolor=theme["fond"],
            activebackground=theme["fond2"],
            activeforeground=theme["texte"],
            padx=15,
            pady=8
        )


        case.grid(
            row=index // 2,
            column=index % 2,
            sticky="w",
            padx=25,
            pady=4
        )


    def mettre_a_jour_scroll(
        event=None
    ):

        canvas_selection.configure(
            scrollregion=canvas_selection.bbox(
                "all"
            )
        )


    cadre_cases.bind(
        "<Configure>",
        mettre_a_jour_scroll
    )


    # ========================================================
    # BOUTONS
    # ========================================================

    cadre_boutons = tk.Frame(
        fenetre_selection,
        bg=theme["fond"]
    )


    cadre_boutons.pack(
        fill="x",
        padx=30,
        pady=(10, 25)
    )


    def tout_selectionner():

        for variable in variables_actions.values():

            variable.set(True)


    bouton_tout = tk.Button(
        cadre_boutons,
        text="Tout sélectionner",
        font=("Segoe UI", 11, "bold"),
        bg=theme["pilule"],
        fg=theme["texte"],
        activebackground=theme["pilule_hover"],
        activeforeground=theme["texte"],
        relief="flat",
        bd=0,
        padx=18,
        pady=10,
        cursor="hand2",
        command=tout_selectionner
    )


    bouton_tout.pack(
        side="left"
    )


    def tout_desselectionner():

        for variable in variables_actions.values():

            variable.set(False)


    bouton_aucun = tk.Button(
        cadre_boutons,
        text="Tout désélectionner",
        font=("Segoe UI", 11, "bold"),
        bg=theme["pilule"],
        fg=theme["texte"],
        activebackground=theme["pilule_hover"],
        activeforeground=theme["texte"],
        relief="flat",
        bd=0,
        padx=18,
        pady=10,
        cursor="hand2",
        command=tout_desselectionner
    )


    bouton_aucun.pack(
        side="left",
        padx=12
    )


    def valider_selection():

        global actions_selectionnees


        nouvelle_selection = set()


        for nom, variable in variables_actions.items():

            if variable.get():

                nouvelle_selection.add(
                    nom
                )


        if len(nouvelle_selection) == 0:

            statut.config(
                text="⚠ Sélectionne au moins une action.",
                fg="#ff5555"
            )

            return


        actions_selectionnees = (
            nouvelle_selection
        )


        fenetre_selection.destroy()


        actualiser()


    bouton_valider = tk.Button(
        cadre_boutons,
        text="✓  Valider",
        font=("Segoe UI", 11, "bold"),
        bg=theme["pilule"],
        fg=theme["texte"],
        activebackground=theme["pilule_hover"],
        activeforeground=theme["texte"],
        relief="flat",
        bd=0,
        padx=22,
        pady=10,
        cursor="hand2",
        command=valider_selection
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
        bg=theme["fond"]
    )


    cadre_principal.configure(
        bg=theme["fond"]
    )


    cadre_options.configure(
        bg=theme["fond"]
    )


    cadre_bas.configure(
        bg=theme["fond"]
    )


    cadre_graphique.configure(
        bg=theme["fond"]
    )


    titre.configure(
        bg=theme["fond"],
        fg=theme["accent"]
    )


    sous_titre.configure(
        bg=theme["fond"],
        fg=theme["gris"]
    )


    label_periode.configure(
        bg=theme["fond"],
        fg=theme["texte"]
    )


    label_theme.configure(
        bg=theme["fond"],
        fg=theme["texte"]
    )


    statut.configure(
        bg=theme["fond"],
        fg=theme["gris"]
    )


    # ========================================================
    # BOUTONS PILULES
    # ========================================================

    for bouton in [
        bouton_actions,
        bouton_theme,
        bouton_actualiser
    ]:

        bouton.configure(
            bg=theme["fond"]
        )


        dessiner_pilule(
            bouton,
            bouton.pilule_largeur,
            bouton.pilule_hauteur,
            theme["pilule"]
        )


        bouton.itemconfig(
            bouton.pilule_texte_id,
            fill=theme["texte"]
        )


    # ========================================================
    # BOUTON PÉRIODE
    # ========================================================

    bouton_periode.configure(
        bg=theme["fond"]
    )


    dessiner_pilule(
        bouton_periode,
        220,
        48,
        theme["pilule"]
    )


    bouton_periode.itemconfig(
        texte_periode,
        fill=theme["texte"]
    )


    if theme_sombre:

        bouton_theme.itemconfig(
            bouton_theme.pilule_texte_id,
            text="☀  Clair"
        )

    else:

        bouton_theme.itemconfig(
            bouton_theme.pilule_texte_id,
            text="🌙  Sombre"
        )


    ax.set_facecolor(
        theme["fond2"]
    )


    figure.patch.set_facecolor(
        theme["fond2"]
    )


    canvas.draw_idle()


# ============================================================
# ACTUALISATION AUTOMATIQUE
# ============================================================

def actualisation_automatique():

    actualiser()


    fenetre.after(
        INTERVALLE_ACTUALISATION,
        actualisation_automatique
    )


# ============================================================
# DÉMARRAGE
# ============================================================

appliquer_theme()


actualiser()


fenetre.after(
    INTERVALLE_ACTUALISATION,
    actualisation_automatique
)


fenetre.mainloop()
