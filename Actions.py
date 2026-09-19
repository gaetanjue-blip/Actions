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


# ============================================================
# CONFIGURATION
# ============================================================

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


THEME_SOMBRE = {
    "fond": "#0d0d0f",
    "fond2": "#151518",
    "pilule": "#242428",
    "pilule_hover": "#303035",
    "texte": "#ffffff",
    "gris": "#999999",
    "accent": "#00ff66"
}


THEME_CLAIR = {
    "fond": "#f2f2f7",
    "fond2": "#ffffff",
    "pilule": "#ffffff",
    "pilule_hover": "#e5e5ea",
    "texte": "#111111",
    "gris": "#666666",
    "accent": "#00994d"
}


theme_sombre = True
theme = THEME_SOMBRE


periodes = {
    "24 h": {
        "period": "5d",
        "interval": "15m"
    },

    "1 semaine": {
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

INTERVALLE_ACTUALISATION = 60 * 60 * 1000


# ============================================================
# FENÊTRE
# ============================================================

fenetre = tk.Tk()

fenetre.title("CacVision")

fenetre.geometry(
    "1250x800"
)

fenetre.minsize(
    950,
    650
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

cadre_principal = tk.Frame(
    fenetre
)

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
    font=(
        "Segoe UI",
        27,
        "bold"
    )
)

titre.pack(
    pady=(18, 0)
)


sous_titre = tk.Label(
    cadre_principal,
    text="Suivi des valeurs du CAC 40",
    font=(
        "Segoe UI",
        11
    )
)

sous_titre.pack(
    pady=(2, 12)
)


# ============================================================
# BARRE D'OPTIONS
# ============================================================

cadre_options = tk.Frame(
    cadre_principal
)

cadre_options.pack(
    fill="x",
    padx=25,
    pady=(0, 12)
)


# ============================================================
# BOUTON PILULE
# ============================================================

def creer_pilule(
    parent,
    texte,
    commande,
    largeur=150
):

    hauteur = 38

    canvas_bouton = tk.Canvas(
        parent,
        width=largeur,
        height=hauteur,
        bg=theme["fond"],
        highlightthickness=0,
        bd=0,
        cursor="hand2"
    )

    rayon = hauteur // 2

    fond = canvas_bouton.create_rounded_rectangle(
        2,
        2,
        largeur - 2,
        hauteur - 2,
        radius=rayon,
        fill=theme["pilule"],
        outline=""
    ) if hasattr(
        canvas_bouton,
        "create_rounded_rectangle"
    ) else None


    # --------------------------------------------------------
    # Tkinter ne possède pas create_rounded_rectangle.
    # On dessine donc la pilule avec 3 formes.
    # --------------------------------------------------------

    canvas_bouton.delete("all")


    canvas_bouton.create_rectangle(
        rayon,
        2,
        largeur - rayon,
        hauteur - 2,
        fill=theme["pilule"],
        outline=""
    )


    canvas_bouton.create_oval(
        2,
        2,
        hauteur - 2,
        hauteur - 2,
        fill=theme["pilule"],
        outline=""
    )


    canvas_bouton.create_oval(
        largeur - hauteur + 2,
        2,
        largeur - 2,
        hauteur - 2,
        fill=theme["pilule"],
        outline=""
    )


    texte_id = canvas_bouton.create_text(
        largeur // 2,
        hauteur // 2,
        text=texte,
        fill=theme["texte"],
        font=(
            "Segoe UI",
            10,
            "bold"
        )
    )


    def survol(event):

        canvas_bouton.itemconfig(
            texte_id,
            fill=theme["texte"]
        )

        dessiner_pilule(
            theme["pilule_hover"]
        )


    def quitter(event):

        dessiner_pilule(
            theme["pilule"]
        )


    def cliquer(event):

        commande()


    def dessiner_pilule(couleur):

        canvas_bouton.delete(
            "fond"
        )

        canvas_bouton.create_rectangle(
            rayon,
            2,
            largeur - rayon,
            hauteur - 2,
            fill=couleur,
            outline="",
            tags="fond"
        )

        canvas_bouton.create_oval(
            2,
            2,
            hauteur - 2,
            hauteur - 2,
            fill=couleur,
            outline="",
            tags="fond"
        )

        canvas_bouton.create_oval(
            largeur - hauteur + 2,
            2,
            largeur - 2,
            hauteur - 2,
            fill=couleur,
            outline="",
            tags="fond"
        )

        canvas_bouton.tag_lower(
            "fond"
        )


    canvas_bouton.bind(
        "<Enter>",
        survol
    )

    canvas_bouton.bind(
        "<Leave>",
        quitter
    )

    canvas_bouton.bind(
        "<Button-1>",
        cliquer
    )


    canvas_bouton.pilule_texte = texte

    canvas_bouton.pilule_largeur = largeur

    canvas_bouton.pilule_texte_id = texte_id

    canvas_bouton.pilule_dessiner = dessiner_pilule

    return canvas_bouton


# ============================================================
# ACTIONS
# ============================================================

bouton_actions = creer_pilule(
    cadre_options,
    "☰  Actions",
    lambda: ouvrir_selection_actions(),
    145
)

bouton_actions.pack(
    side="left",
    padx=(0, 15)
)


# ============================================================
# LABEL PÉRIODE
# ============================================================

label_periode = tk.Label(
    cadre_options,
    text="Période",
    font=(
        "Segoe UI",
        10,
        "bold"
    )
)

label_periode.pack(
    side="left",
    padx=(0, 7)
)


# ============================================================
# MENU PÉRIODE
# ============================================================

style = ttk.Style()

try:

    style.theme_use(
        "clam"
    )

except:

    pass


style.configure(
    "TCombobox",
    padding=5
)


menu_periode = ttk.Combobox(
    cadre_options,
    values=list(
        periodes.keys()
    ),
    state="readonly",
    width=17
)

menu_periode.set(
    "24 h"
)

menu_periode.pack(
    side="left"
)


# ============================================================
# MODE SOMBRE / CLAIR
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
    125
)

bouton_theme.pack(
    side="right"
)


label_theme = tk.Label(
    cadre_options,
    text="Apparence",
    font=(
        "Segoe UI",
        10,
        "bold"
    )
)

label_theme.pack(
    side="right",
    padx=(0, 7)
)


# ============================================================
# GRAPHIQUE
# ============================================================

cadre_graphique = tk.Frame(
    cadre_principal
)

cadre_graphique.pack(
    fill="both",
    expand=True,
    padx=25,
    pady=5
)


plt.rcParams[
    "font.family"
] = "Segoe UI"


figure, ax = plt.subplots(
    figsize=(10, 6)
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
    padx=25,
    pady=(8, 18)
)


statut = tk.Label(
    cadre_bas,
    text="Démarrage...",
    font=(
        "Segoe UI",
        10
    )
)

statut.pack(
    side="left"
)


# ============================================================
# ACTUALISER
# ============================================================

bouton_actualiser = creer_pilule(
    cadre_bas,
    "⟳  Actualiser",
    lambda: actualiser(),
    145
)

bouton_actualiser.pack(
    side="right"
)


# ============================================================
# APPLIQUER LE THÈME
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


    # --------------------------------------------------------
    # BOUTONS PILULES
    # --------------------------------------------------------

    for bouton in [
        bouton_actions,
        bouton_theme,
        bouton_actualiser
    ]:

        bouton.configure(
            bg=theme["fond"]
        )

        bouton.pilule_dessiner(
            theme["pilule"]
        )

        bouton.itemconfig(
            bouton.pilule_texte_id,
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
# RÉCUPÉRER LES DONNÉES
# ============================================================

def recuperer_donnees():

    configuration = periodes[
        periode_actuelle
    ]

    period = configuration[
        "period"
    ]

    interval = configuration[
        "interval"
    ]

    donnees = {}


    for nom in actions_selectionnees:

        symbole = actions_cac40[
            nom
        ]

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
# AFFICHER LE GRAPHIQUE
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

        data = donnees.get(
            nom
        )


        if data is None or data.empty:

            continue


        try:

            cours = data[
                "Close"
            ]


            if hasattr(
                cours,
                "columns"
            ):

                cours = cours.iloc[
                    :,
                    0
                ]


            cours = cours.dropna()


            if len(cours) == 0:

                continue


            dates = cours.index


            valeurs = np.array(
                cours.values,
                dtype=float
            )


            couleur = couleurs_actions[
                nom
            ]


            ligne, = ax.plot(
                dates,
                valeurs,
                label=nom,
                color=couleur,
                linewidth=2.3,
                marker="o",
                markersize=2.5,
                picker=8
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


    ax.set_title(
        f"CAC 40 — {periode_actuelle}",
        color=theme["texte"],
        fontsize=15,
        fontweight="bold",
        pad=15
    )


    ax.set_xlabel(
        "Date",
        color=theme["texte"],
        fontsize=10
    )


    ax.set_ylabel(
        "Prix (€)",
        color=theme["texte"],
        fontsize=10
    )


    if periode_actuelle == "24 h":

        ax.xaxis.set_major_formatter(
            mdates.DateFormatter(
                "%H:%M"
            )
        )

    elif periode_actuelle == "1 semaine":

        ax.xaxis.set_major_formatter(
            mdates.DateFormatter(
                "%d/%m"
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


    ax.tick_params(
        axis="both",
        colors=theme["texte"],
        labelsize=9
    )


    ax.grid(
        True,
        color="#777777",
        alpha=0.25,
        linestyle="--"
    )


    for bordure in ax.spines.values():

        bordure.set_color(
            "#555555"
        )


    if nombre_actions > 0:

        legend = ax.legend(
            loc="upper left",
            frameon=True,
            facecolor=theme["fond"],
            edgecolor="#777777",
            fontsize=9
        )


        for texte in legend.get_texts():

            texte.set_color(
                theme["texte"]
            )


    heure = datetime.now().strftime(
        "%d/%m/%Y %H:%M:%S"
    )


    ax.text(
        0.99,
        0.02,
        "Actualisé : " + heure,
        transform=ax.transAxes,
        color=theme["gris"],
        fontsize=8,
        ha="right"
    )


    figure.autofmt_xdate()

    figure.tight_layout()

    canvas.draw_idle()


# ============================================================
# INFO SOURIS
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


            distance = distances[
                index
            ]


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
        fontsize=10,
        fontweight="bold",
        bbox=dict(
            boxstyle="round,pad=0.5",
            facecolor=theme["fond"],
            edgecolor=couleurs_actions[nom],
            alpha=0.95
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
# ACTUALISER
# ============================================================

def actualiser():

    bouton_actualiser.itemconfig(
        bouton_actualiser.pilule_texte_id,
        text="⟳  Chargement..."
    )


    statut.config(
        text=f"Récupération des données ({periode_actuelle})...",
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
# CHANGEMENT DE PÉRIODE
# ============================================================

def changer_periode(event=None):

    global periode_actuelle


    nouvelle_periode = menu_periode.get()


    if nouvelle_periode not in periodes:

        return


    periode_actuelle = nouvelle_periode

    actualiser()


menu_periode.bind(
    "<<ComboboxSelected>>",
    changer_periode
)


# ============================================================
# FENÊTRE DE SÉLECTION DES ACTIONS
# ============================================================

def ouvrir_selection_actions():

    fenetre_selection = tk.Toplevel(
        fenetre
    )


    fenetre_selection.title(
        "Actions"
    )


    fenetre_selection.geometry(
        "650x650"
    )


    fenetre_selection.configure(
        bg=theme["fond"]
    )


    titre_selection = tk.Label(
        fenetre_selection,
        text="Choisir les actions",
        font=(
            "Segoe UI",
            18,
            "bold"
        ),
        bg=theme["fond"],
        fg=theme["texte"]
    )


    titre_selection.pack(
        pady=(18, 5)
    )


    sous_titre_selection = tk.Label(
        fenetre_selection,
        text="Sélectionne les valeurs à afficher",
        font=(
            "Segoe UI",
            10
        ),
        bg=theme["fond"],
        fg=theme["gris"]
    )


    sous_titre_selection.pack(
        pady=(0, 12)
    )


    cadre_liste = tk.Frame(
        fenetre_selection,
        bg=theme["fond2"]
    )


    cadre_liste.pack(
        fill="both",
        expand=True,
        padx=20,
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
            font=(
                "Segoe UI",
                10
            ),
            bg=theme["fond2"],
            fg=theme["texte"],
            selectcolor=theme["fond"],
            activebackground=theme["fond2"],
            activeforeground=theme["texte"],
            padx=10,
            pady=5
        )


        case.grid(
            row=index // 2,
            column=index % 2,
            sticky="w",
            padx=15,
            pady=2
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


    cadre_boutons = tk.Frame(
        fenetre_selection,
        bg=theme["fond"]
    )


    cadre_boutons.pack(
        fill="x",
        padx=20,
        pady=(5, 15)
    )


    # ========================================================
    # TOUT SÉLECTIONNER
    # ========================================================

    def tout_selectionner():

        for variable in variables_actions.values():

            variable.set(True)


    bouton_tout = tk.Button(
        cadre_boutons,
        text="Tout sélectionner",
        font=(
            "Segoe UI",
            10,
            "bold"
        ),
        bg=theme["pilule"],
        fg=theme["texte"],
        relief="flat",
        bd=0,
        padx=12,
        pady=6,
        cursor="hand2",
        command=tout_selectionner
    )


    bouton_tout.pack(
        side="left"
    )


    # ========================================================
    # TOUT DÉSELECTIONNER
    # ========================================================

    def tout_desselectionner():

        for variable in variables_actions.values():

            variable.set(False)


    bouton_aucun = tk.Button(
        cadre_boutons,
        text="Tout désélectionner",
        font=(
            "Segoe UI",
            10,
            "bold"
        ),
        bg=theme["pilule"],
        fg=theme["texte"],
        relief="flat",
        bd=0,
        padx=12,
        pady=6,
        cursor="hand2",
        command=tout_desselectionner
    )


    bouton_aucun.pack(
        side="left",
        padx=8
    )


    # ========================================================
    # VALIDER
    # ========================================================

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


        actions_selectionnees = nouvelle_selection


        fenetre_selection.destroy()


        actualiser()


    bouton_valider = tk.Button(
        cadre_boutons,
        text="✓  Valider",
        font=(
            "Segoe UI",
            10,
            "bold"
        ),
        bg=theme["pilule"],
        fg=theme["texte"],
        relief="flat",
        bd=0,
        padx=14,
        pady=6,
        cursor="hand2",
        command=valider_selection
    )


    bouton_valider.pack(
        side="right"
    )


    # ========================================================
    # SURVOL
    # ========================================================

    for bouton in [
        bouton_tout,
        bouton_aucun,
        bouton_valider
    ]:

        def entrer(
            event,
            b=bouton
        ):

            b.configure(
                bg=theme["pilule_hover"]
            )


        def sortir(
            event,
            b=bouton
        ):

            b.configure(
                bg=theme["pilule"]
            )


        bouton.bind(
            "<Enter>",
            entrer
        )

        bouton.bind(
            "<Leave>",
            sortir
        )


# ============================================================
# THÈME INITIAL
# ============================================================

appliquer_theme()


# ============================================================
# PREMIÈRE ACTUALISATION
# ============================================================

actualiser()


# ============================================================
# ACTUALISATION AUTOMATIQUE
# ============================================================

def actualisation_automatique():

    actualiser()


    fenetre.after(
        INTERVALLE_ACTUALISATION,
        actualisation_automatique
    )


fenetre.after(
    INTERVALLE_ACTUALISATION,
    actualisation_automatique
)


# ============================================================
# LANCEMENT
# ============================================================

fenetre.mainloop()
