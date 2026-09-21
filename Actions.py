
import tkinter as tk
from tkinter import messagebox
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import threading
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

NOM_APPLICATION = "CacVision"

PARIS = ZoneInfo("Europe/Paris")

# ACTUALISATION AUTOMATIQUE : 1 HEURE
INTERVALLE_ACTUALISATION = 60 * 60 * 1000

INTERVALLE_MARCHE = 30000


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
# ACTIONS SÉLECTIONNÉES
# ============================================================

actions_selectionnees = {
    "Thales",
    "Airbus",
    "Vinci"
}


# ============================================================
# PÉRIODES
# ============================================================

periodes = {
    "24 h": {
        "interval": "5m"
    },

    "1 semaine": {
        "interval": "15m"
    },

    "1 mois": {
        "interval": "1h"
    },

    "1 an": {
        "interval": "1d"
    },

    "Depuis toujours": {
        "interval": "1d"
    }
}

periode_actuelle = "24 h"


# ============================================================
# THÈMES
# ============================================================

THEME_SOMBRE = {
    "fond_haut": "#0B1220",
    "fond_bas": "#111827",
    "panneau": "#172033",
    "verre": "#1E293B",
    "verre_hover": "#27364D",
    "texte": "#F8FAFC",
    "texte_secondaire": "#94A3B8",
    "bordure": "#334155",
    "accent": "#55E6A5",
    "accent2": "#52BFFF",
    "danger": "#FF6B8A",
    "graphique": "#101827"
}


THEME_CLAIR = {
    "fond_haut": "#E8EEF5",
    "fond_bas": "#F5F7FA",
    "panneau": "#FFFFFF",
    "verre": "#E9EEF5",
    "verre_hover": "#DDE6F0",
    "texte": "#172033",
    "texte_secondaire": "#64748B",
    "bordure": "#CBD5E1",
    "accent": "#16A34A",
    "accent2": "#0284C7",
    "danger": "#E11D48",
    "graphique": "#FFFFFF"
}


# ============================================================
# MODE CLAIR AU LANCEMENT
# ============================================================

theme = THEME_CLAIR


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


# ============================================================
# VARIABLES GLOBALES
# ============================================================

donnees_actuelles = {}
lignes = {}

actualisation_en_cours = False

menu_periode = None
fenetre_selection = None

canvas_principal = None
conteneur = None
sidebar = None

cadre_actions = None
cadre_scroll_actions = None
canvas_actions = None
scrollbar_actions = None
fenetre_actions_canvas = None

graph_frame = None
statut_label = None

fig = None
ax = None
canvas_graphique = None

bouton_actions = None
bouton_periode = None
bouton_theme = None
bouton_actualiser = None

fond_a_dessiner = True


# ============================================================
# FENÊTRE PRINCIPALE
# ============================================================

fenetre = tk.Tk()

fenetre.title(NOM_APPLICATION)

fenetre.state("zoomed")

fenetre.configure(
    bg=theme["fond_bas"]
)


# ============================================================
# FOND
# ============================================================

canvas_principal = tk.Canvas(
    fenetre,
    highlightthickness=0,
    bd=0
)

canvas_principal.pack(
    fill="both",
    expand=True
)


def dessiner_fond(event=None):

    largeur = canvas_principal.winfo_width()
    hauteur = canvas_principal.winfo_height()

    if largeur <= 0 or hauteur <= 0:
        return

    canvas_principal.delete("fond")

    h1 = theme["fond_haut"].lstrip("#")
    h2 = theme["fond_bas"].lstrip("#")

    r1 = int(h1[0:2], 16)
    g1 = int(h1[2:4], 16)
    b1 = int(h1[4:6], 16)

    r2 = int(h2[0:2], 16)
    g2 = int(h2[2:4], 16)
    b2 = int(h2[4:6], 16)

    nombre_lignes = 80

    hauteur_ligne = hauteur / nombre_lignes

    for i in range(nombre_lignes):

        ratio = i / max(nombre_lignes - 1, 1)

        r = int(r1 + (r2 - r1) * ratio)
        g = int(g1 + (g2 - g1) * ratio)
        b = int(b1 + (b2 - b1) * ratio)

        couleur = f"#{r:02X}{g:02X}{b:02X}"

        canvas_principal.create_rectangle(
            0,
            i * hauteur_ligne,
            largeur,
            (i + 1) * hauteur_ligne + 1,
            fill=couleur,
            outline="",
            tags="fond"
        )


canvas_principal.bind(
    "<Configure>",
    dessiner_fond
)


# ============================================================
# CONTENEUR
# ============================================================

conteneur = tk.Frame(
    canvas_principal,
    bg=theme["panneau"],
    highlightthickness=1,
    highlightbackground=theme["bordure"]
)

conteneur.place(
    relx=0.02,
    rely=0.025,
    relwidth=0.96,
    relheight=0.95
)


# ============================================================
# HEADER
# ============================================================

header = tk.Frame(
    conteneur,
    bg=theme["panneau"],
    height=95
)

header.pack(
    fill="x",
    padx=25,
    pady=(20, 5)
)

header.pack_propagate(False)


titre = tk.Label(
    header,
    text="CacVision",
    font=("Segoe UI", 30, "bold"),
    fg=theme["texte"],
    bg=theme["panneau"]
)

titre.pack(
    side="left",
    anchor="w"
)


sous_titre = tk.Label(
    header,
    text="Suivi des actions du CAC 40",
    font=("Segoe UI", 12),
    fg=theme["texte_secondaire"],
    bg=theme["panneau"]
)

sous_titre.pack(
    side="left",
    padx=(18, 0),
    pady=(15, 0)
)


live_frame = tk.Frame(
    header,
    bg=theme["panneau"]
)

live_frame.pack(
    side="right",
    pady=10
)


live_point = tk.Label(
    live_frame,
    text="●",
    font=("Segoe UI", 14),
    fg=theme["accent"],
    bg=theme["panneau"]
)

live_point.pack(
    side="left"
)


live_label = tk.Label(
    live_frame,
    text=" Marché",
    font=("Segoe UI", 11, "bold"),
    fg=theme["texte"],
    bg=theme["panneau"]
)

live_label.pack(
    side="left"
)


# ============================================================
# BARRE DE COMMANDES
# ============================================================

barre_commandes = tk.Frame(
    conteneur,
    bg=theme["panneau"],
    height=60
)

barre_commandes.pack(
    fill="x",
    padx=25,
    pady=5
)

barre_commandes.pack_propagate(False)


# ============================================================
# BOUTONS
# ============================================================

def creer_bouton_verre(
    parent,
    texte,
    commande,
    largeur=170
):

    bouton = tk.Canvas(
        parent,
        width=largeur,
        height=44,
        bg=theme["panneau"],
        highlightthickness=0,
        bd=0,
        cursor="hand2"
    )

    bouton.pack(
        side="left",
        padx=6
    )

    bouton.est_survole = False

    def dessiner():

        bouton.delete("all")

        if bouton.est_survole:

            couleur = theme["verre_hover"]
            bordure = theme["accent2"]

        else:

            couleur = theme["verre"]
            bordure = theme["bordure"]

        bouton.configure(
            bg=theme["panneau"]
        )

        bouton.create_rectangle(
            2,
            2,
            largeur - 2,
            42,
            fill=couleur,
            outline=bordure
        )

        bouton.create_text(
            largeur / 2,
            22,
            text=texte(),
            fill=theme["texte"],
            font=("Segoe UI", 11, "bold")
        )

    def survol(event=None):

        bouton.est_survole = True

        dessiner()

    def normal(event=None):

        bouton.est_survole = False

        dessiner()

    bouton.bind(
        "<Enter>",
        survol
    )

    bouton.bind(
        "<Leave>",
        normal
    )

    bouton.bind(
        "<Button-1>",
        lambda event: commande()
    )

    bouton.dessiner = dessiner

    dessiner()

    return bouton


# ============================================================
# ZONE PRINCIPALE
# ============================================================

zone_principale = tk.Frame(
    conteneur,
    bg=theme["panneau"]
)

zone_principale.pack(
    fill="both",
    expand=True,
    padx=25,
    pady=(10, 20)
)


# ============================================================
# SIDEBAR
# ============================================================

sidebar = tk.Frame(
    zone_principale,
    bg=theme["panneau"],
    width=320
)

sidebar.pack(
    side="left",
    fill="y",
    padx=(0, 15)
)

sidebar.pack_propagate(False)


label_selection = tk.Label(
    sidebar,
    text="Actions sélectionnées",
    font=("Segoe UI", 14, "bold"),
    fg=theme["texte"],
    bg=theme["panneau"]
)

label_selection.pack(
    anchor="w",
    pady=(5, 15)
)


# ============================================================
# SCROLL ACTIONS
# ============================================================

cadre_scroll_actions = tk.Frame(
    sidebar,
    bg=theme["panneau"]
)

cadre_scroll_actions.pack(
    fill="both",
    expand=True
)


canvas_actions = tk.Canvas(
    cadre_scroll_actions,
    bg=theme["panneau"],
    highlightthickness=0,
    bd=0
)

scrollbar_actions = tk.Scrollbar(
    cadre_scroll_actions,
    orient="vertical",
    command=canvas_actions.yview
)

canvas_actions.configure(
    yscrollcommand=scrollbar_actions.set
)

scrollbar_actions.pack(
    side="right",
    fill="y"
)

canvas_actions.pack(
    side="left",
    fill="both",
    expand=True
)


cadre_actions = tk.Frame(
    canvas_actions,
    bg=theme["panneau"]
)

fenetre_actions_canvas = canvas_actions.create_window(
    (0, 0),
    window=cadre_actions,
    anchor="nw"
)


def mettre_a_jour_scroll_actions(event=None):

    canvas_actions.configure(
        scrollregion=canvas_actions.bbox("all")
    )


cadre_actions.bind(
    "<Configure>",
    mettre_a_jour_scroll_actions
)


def adapter_largeur_actions(event):

    canvas_actions.itemconfigure(
        fenetre_actions_canvas,
        width=event.width
    )


canvas_actions.bind(
    "<Configure>",
    adapter_largeur_actions
)


def molette_actions(event):

    canvas_actions.yview_scroll(
        int(-1 * (event.delta / 120)),
        "units"
    )


def activer_molette(widget):

    widget.bind(
        "<MouseWheel>",
        molette_actions
    )

    for enfant in widget.winfo_children():

        activer_molette(enfant)


canvas_actions.bind(
    "<MouseWheel>",
    molette_actions
)

cadre_actions.bind(
    "<MouseWheel>",
    molette_actions
)


# ============================================================
# GRAPHIQUE
# ============================================================

graph_frame = tk.Frame(
    zone_principale,
    bg=theme["graphique"],
    highlightthickness=1,
    highlightbackground=theme["bordure"]
)

graph_frame.pack(
    side="left",
    fill="both",
    expand=True
)


fig = plt.Figure(
    figsize=(10, 6),
    dpi=100,
    facecolor=theme["graphique"]
)

ax = fig.add_subplot(111)

ax.set_facecolor(
    theme["graphique"]
)

ax.grid(False)


canvas_graphique = FigureCanvasTkAgg(
    fig,
    master=graph_frame
)

canvas_graphique.get_tk_widget().pack(
    fill="both",
    expand=True,
    padx=10,
    pady=10
)


# ============================================================
# STATUT
# ============================================================

statut_label = tk.Label(
    conteneur,
    text="Prêt",
    font=("Segoe UI", 9),
    fg=theme["texte_secondaire"],
    bg=theme["panneau"]
)

statut_label.pack(
    pady=(0, 10)
)


# ============================================================
# SIDEBAR
# ============================================================

def afficher_actions_sidebar():

    for widget in cadre_actions.winfo_children():
        widget.destroy()

    for nom in sorted(actions_selectionnees):

        ticker = actions_cac40[nom]

        carte = tk.Frame(
            cadre_actions,
            bg=theme["verre"],
            highlightthickness=1,
            highlightbackground=theme["bordure"]
        )

        carte.pack(
            fill="x",
            pady=5,
            padx=2
        )

        nom_label = tk.Label(
            carte,
            text=nom,
            font=("Segoe UI", 11, "bold"),
            fg=theme["texte"],
            bg=theme["verre"]
        )

        nom_label.pack(
            anchor="w",
            padx=12,
            pady=(9, 0)
        )

        ticker_label = tk.Label(
            carte,
            text=ticker,
            font=("Segoe UI", 8),
            fg=theme["texte_secondaire"],
            bg=theme["verre"]
        )

        ticker_label.pack(
            anchor="w",
            padx=12,
            pady=(0, 5)
        )

        if nom in donnees_actuelles:

            try:

                df = donnees_actuelles[nom]

                valeurs_prix = pd.to_numeric(
                    df["Close"],
                    errors="coerce"
                ).dropna()

                if not valeurs_prix.empty:

                    prix = float(
                        valeurs_prix.iloc[-1]
                    )

                    prix_label = tk.Label(
                        carte,
                        text=f"{prix:.2f} €",
                        font=("Segoe UI", 13, "bold"),
                        fg=theme["accent"],
                        bg=theme["verre"]
                    )

                    prix_label.pack(
                        anchor="w",
                        padx=12,
                        pady=(0, 9)
                    )

            except Exception:
                pass

        activer_molette(carte)

    cadre_actions.update_idletasks()

    canvas_actions.configure(
        scrollregion=canvas_actions.bbox("all")
    )


# ============================================================
# PRÉPARATION DES DONNÉES
# ============================================================

def preparer_dataframe(df):

    if df is None or df.empty:
        return None

    df = df.copy()

    if isinstance(df.columns, pd.MultiIndex):

        try:
            df.columns = df.columns.get_level_values(0)

        except Exception:
            pass

    if "Close" not in df.columns:
        return None

    df["Close"] = pd.to_numeric(
        df["Close"],
        errors="coerce"
    )

    df = df.dropna(
        subset=["Close"]
    )

    if df.empty:
        return None

    try:

        if df.index.tz is not None:

            df.index = df.index.tz_convert(
                PARIS
            )

    except Exception:
        pass

    df = df[
        df.index.weekday < 5
    ]

    if df.empty:
        return None

    return df


# ============================================================
# COURBE
# ============================================================

def construire_courbe_continue(dates, valeurs):

    if len(dates) == 0:
        return [], []

    dates = list(dates)
    valeurs = list(valeurs)

    courbe_dates = []
    courbe_valeurs = []

    derniere_valeur = None

    for i, date_actuelle in enumerate(dates):

        valeur_actuelle = valeurs[i]

        courbe_dates.append(
            date_actuelle
        )

        courbe_valeurs.append(
            valeur_actuelle
        )

        derniere_valeur = valeur_actuelle

        if i < len(dates) - 1:

            prochaine_date = dates[i + 1]

            try:

                if (
                    prochaine_date - date_actuelle
                    > timedelta(hours=8)
                ):

                    courbe_dates.append(
                        prochaine_date - timedelta(seconds=1)
                    )

                    courbe_valeurs.append(
                        derniere_valeur
                    )

            except Exception:
                pass

    return courbe_dates, courbe_valeurs


# ============================================================
# DERNIER JOUR DE BOURSE
# ============================================================

def dernier_jour_de_bourse(date):

    jour = date

    while jour.weekday() >= 5:

        jour -= timedelta(days=1)

    return jour


# ============================================================
# DATES
# ============================================================

def obtenir_dates_periode():

    maintenant = datetime.now(PARIS)

    if periode_actuelle == "24 h":

        aujourd_hui = maintenant.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )

        ouverture = aujourd_hui.replace(
            hour=9,
            minute=0
        )

        fermeture = aujourd_hui.replace(
            hour=17,
            minute=30
        )

        if maintenant < ouverture:

            jour = dernier_jour_de_bourse(
                aujourd_hui - timedelta(days=1)
            )

            ouverture = jour.replace(
                hour=9,
                minute=0
            )

            fermeture = jour.replace(
                hour=17,
                minute=30
            )

        elif maintenant <= fermeture:

            fermeture = maintenant

        return ouverture, fermeture

    elif periode_actuelle == "1 semaine":

        lundi = maintenant - timedelta(
            days=maintenant.weekday()
        )

        debut = lundi.replace(
            hour=9,
            minute=0,
            second=0,
            microsecond=0
        )

        return debut, maintenant

    elif periode_actuelle == "1 mois":

        debut = maintenant.replace(
            day=1,
            hour=9,
            minute=0,
            second=0,
            microsecond=0
        )

        return debut, maintenant

    elif periode_actuelle == "1 an":

        debut = maintenant.replace(
            month=1,
            day=1,
            hour=9,
            minute=0,
            second=0,
            microsecond=0
        )

        return debut, maintenant

    return None, maintenant


# ============================================================
# DATES DU GRAPHIQUE
# ============================================================

def configurer_dates_graphique():

    debut, fin = obtenir_dates_periode()

    if periode_actuelle == "24 h":

        ax.xaxis.set_major_locator(
            mdates.HourLocator(interval=1)
        )

        ax.xaxis.set_major_formatter(
            mdates.DateFormatter("%H:%M")
        )

    elif periode_actuelle == "1 semaine":

        ax.xaxis.set_major_locator(
            mdates.DayLocator(interval=1)
        )

        ax.xaxis.set_major_formatter(
            mdates.DateFormatter("%d/%m")
        )

    elif periode_actuelle == "1 mois":

        ax.xaxis.set_major_locator(
            mdates.DayLocator(interval=5)
        )

        ax.xaxis.set_major_formatter(
            mdates.DateFormatter("%d/%m")
        )

    elif periode_actuelle == "1 an":

        ax.xaxis.set_major_locator(
            mdates.MonthLocator()
        )

        ax.xaxis.set_major_formatter(
            mdates.DateFormatter("%m/%Y")
        )

    else:

        ax.xaxis.set_major_locator(
            mdates.AutoDateLocator()
        )

        ax.xaxis.set_major_formatter(
            mdates.DateFormatter("%m/%Y")
        )

    if debut is not None:

        ax.set_xlim(
            debut,
            fin
        )


# ============================================================
# GRAPHIQUE
# ============================================================

def actualiser_graphique():

    ax.clear()

    ax.set_facecolor(
        theme["graphique"]
    )

    fig.patch.set_facecolor(
        theme["graphique"]
    )

    lignes.clear()

    for index, nom in enumerate(
        actions_selectionnees
    ):

        if nom not in donnees_actuelles:
            continue

        df = donnees_actuelles[nom]

        try:

            valeurs = pd.to_numeric(
                df["Close"],
                errors="coerce"
            )

            masque = valeurs.notna()

            valeurs = valeurs[masque]

            dates = df.index[masque]

            if valeurs.empty:
                continue

            dates_courbe, valeurs_courbe = (
                construire_courbe_continue(
                    dates,
                    valeurs
                )
            )

            if not dates_courbe:
                continue

            couleur = COULEURS_COURBES[
                index % len(COULEURS_COURBES)
            ]

            ligne, = ax.plot(
                dates_courbe,
                valeurs_courbe,
                color=couleur,
                linewidth=2.0,
                label=nom
            )

            lignes[nom] = ligne

            dernier_prix = float(
                valeurs.iloc[-1]
            )

            derniere_date = dates[-1]

            ax.scatter(
                [derniere_date],
                [dernier_prix],
                color=couleur,
                s=30,
                zorder=5
            )

        except Exception as erreur:

            print(
                f"Erreur graphique {nom}:",
                erreur
            )

    ax.set_title(
        "Évolution des actions",
        color=theme["texte"],
        fontsize=17,
        fontweight="bold",
        pad=15
    )

    ax.set_ylabel(
        "Prix (€)",
        color=theme["texte_secondaire"]
    )

    ax.tick_params(
        colors=theme["texte_secondaire"]
    )

    for bordure in ax.spines.values():

        bordure.set_color(
            theme["bordure"]
        )

    if lignes:

        ax.grid(
            True,
            alpha=0.15
        )

    else:

        ax.grid(False)

    if lignes:

        ax.legend(
            loc="upper left",
            bbox_to_anchor=(1.01, 1),
            facecolor=theme["panneau"],
            edgecolor=theme["bordure"],
            labelcolor=theme["texte"],
            fontsize=9,
            framealpha=1
        )

        fig.subplots_adjust(
            left=0.07,
            right=0.78,
            top=0.91,
            bottom=0.12
        )

    else:

        fig.subplots_adjust(
            left=0.07,
            right=0.95,
            top=0.91,
            bottom=0.12
        )

    configurer_dates_graphique()

    fig.autofmt_xdate()

    canvas_graphique.draw_idle()

    afficher_actions_sidebar()


# ============================================================
# TÉLÉCHARGEMENT OPTIMISÉ
# ============================================================

def telecharger_donnees():

    configuration = periodes[
        periode_actuelle
    ]

    interval = configuration["interval"]

    debut, fin = obtenir_dates_periode()

    noms = list(actions_selectionnees)

    tickers = [
        actions_cac40[nom]
        for nom in noms
    ]

    nouvelles_donnees = {}

    try:

        print(
            "Téléchargement groupé:",
            ", ".join(tickers)
        )

        if periode_actuelle == "1 an":

            df = yf.download(
                tickers,
                period="1y",
                interval="1d",
                auto_adjust=False,
                progress=False,
                threads=True,
                group_by="column"
            )

        elif periode_actuelle == "Depuis toujours":

            df = yf.download(
                tickers,
                period="max",
                interval=interval,
                auto_adjust=False,
                progress=False,
                threads=True,
                group_by="column"
            )

        else:

            fin_telechargement = (
                fin + timedelta(minutes=5)
            )

            df = yf.download(
                tickers,
                start=debut,
                end=fin_telechargement,
                interval=interval,
                auto_adjust=False,
                progress=False,
                threads=True,
                group_by="column"
            )

        if df is None or df.empty:

            return {}

        if isinstance(df.columns, pd.MultiIndex):

            niveaux = df.columns.get_level_values

            if "Close" in niveaux(0):

                for nom, ticker in zip(
                    noms,
                    tickers
                ):

                    try:

                        action_df = pd.DataFrame({
                            "Close": df[
                                ("Close", ticker)
                            ]
                        })

                        action_df = preparer_dataframe(
                            action_df
                        )

                        if action_df is not None:

                            if periode_actuelle not in [
                                "Depuis toujours",
                                "1 an"
                            ]:

                                action_df = action_df[
                                    (action_df.index >= debut)
                                    &
                                    (action_df.index <= fin)
                                ]

                            if not action_df.empty:

                                nouvelles_donnees[nom] = action_df

                    except Exception as erreur:

                        print(
                            f"Erreur {nom}:",
                            erreur
                        )

            else:

                for nom, ticker in zip(
                    noms,
                    tickers
                ):

                    try:

                        action_df = pd.DataFrame({
                            "Close": df[
                                (ticker, "Close")
                            ]
                        })

                        action_df = preparer_dataframe(
                            action_df
                        )

                        if action_df is not None:

                            if periode_actuelle not in [
                                "Depuis toujours",
                                "1 an"
                            ]:

                                action_df = action_df[
                                    (action_df.index >= debut)
                                    &
                                    (action_df.index <= fin)
                                ]

                            if not action_df.empty:

                                nouvelles_donnees[nom] = action_df

                    except Exception as erreur:

                        print(
                            f"Erreur {nom}:",
                            erreur
                        )

        else:

            if len(noms) == 1:

                nom = noms[0]

                df = preparer_dataframe(df)

                if df is not None:

                    if periode_actuelle not in [
                        "Depuis toujours",
                        "1 an"
                    ]:

                        df = df[
                            (df.index >= debut)
                            &
                            (df.index <= fin)
                        ]

                    if not df.empty:

                        nouvelles_donnees[nom] = df

    except Exception as erreur:

        print(
            "Erreur téléchargement groupé:",
            erreur
        )

    return nouvelles_donnees


# ============================================================
# ACTUALISATION
# ============================================================

def actualiser_donnees():

    global actualisation_en_cours

    if actualisation_en_cours:

        return

    actualisation_en_cours = True

    statut_label.config(
        text="Téléchargement...",
        fg=theme["accent2"]
    )

    threading.Thread(
        target=telecharger_en_arriere_plan,
        daemon=True
    ).start()


# ============================================================
# ARRIÈRE-PLAN
# ============================================================

def telecharger_en_arriere_plan():

    global donnees_actuelles
    global actualisation_en_cours

    try:

        nouvelles_donnees = (
            telecharger_donnees()
        )

        def terminer():

            global donnees_actuelles
            global actualisation_en_cours

            if nouvelles_donnees:

                donnees_actuelles = (
                    nouvelles_donnees
                )

                actualiser_graphique()

                maintenant = datetime.now(
                    PARIS
                )

                statut_label.config(
                    text=(
                        "Données mises à jour • "
                        + maintenant.strftime("%H:%M:%S")
                    ),
                    fg=theme["accent"]
                )

            else:

                statut_label.config(
                    text="Impossible de récupérer les données",
                    fg=theme["danger"]
                )

            actualisation_en_cours = False

        fenetre.after(
            0,
            terminer
        )

    except Exception as erreur:

        print(
            "Erreur générale:",
            erreur
        )

        def afficher_erreur():

            global actualisation_en_cours

            statut_label.config(
                text="Erreur lors de l'actualisation",
                fg=theme["danger"]
            )

            actualisation_en_cours = False

        fenetre.after(
            0,
            afficher_erreur
        )


# ============================================================
# ACTUALISATION AUTOMATIQUE
# ============================================================

def actualisation_automatique():

    actualiser_donnees()

    fenetre.after(
        INTERVALLE_ACTUALISATION,
        actualisation_automatique
    )


# ============================================================
# ÉTAT DU MARCHÉ
# ============================================================

def verifier_marche():

    maintenant = datetime.now(
        PARIS
    )

    heure = (
        maintenant.hour * 60
        + maintenant.minute
    )

    ouverture = 9 * 60
    fermeture = 17 * 60 + 30

    if maintenant.weekday() >= 5:

        live_point.config(
            fg=theme["texte_secondaire"]
        )

        live_label.config(
            text=" Week-end",
            fg=theme["texte_secondaire"]
        )

    elif heure < ouverture or heure >= fermeture:

        live_point.config(
            fg=theme["danger"]
        )

        live_label.config(
            text=" Marché fermé",
            fg=theme["texte_secondaire"]
        )

    else:

        live_point.config(
            fg=theme["accent"]
        )

        live_label.config(
            text=" Marché ouvert",
            fg=theme["texte"]
        )

    fenetre.after(
        INTERVALLE_MARCHE,
        verifier_marche
    )


# ============================================================
# MENU PÉRIODE
# ============================================================

def choisir_periode(nom):

    global periode_actuelle
    global menu_periode

    periode_actuelle = nom

    if menu_periode is not None:

        try:
            menu_periode.destroy()
        except Exception:
            pass

        menu_periode = None

    actualiser_donnees()


def ouvrir_menu_periode():

    global menu_periode

    if menu_periode is not None:

        try:
            menu_periode.destroy()
        except Exception:
            pass

    menu_periode = tk.Toplevel(
        fenetre
    )

    menu_periode.overrideredirect(
        True
    )

    x = bouton_periode.winfo_rootx()
    y = bouton_periode.winfo_rooty()

    hauteur = (
        len(periodes) * 42 + 10
    )

    menu_periode.geometry(
        f"190x{hauteur}+{x}+{y + 48}"
    )

    menu_periode.configure(
        bg=theme["panneau"]
    )

    for nom in periodes:

        bouton = tk.Button(
            menu_periode,
            text=nom,
            command=lambda n=nom: choisir_periode(n),
            bg=theme["verre"],
            fg=theme["texte"],
            activebackground=theme["verre_hover"],
            activeforeground=theme["texte"],
            relief="flat",
            bd=0,
            anchor="w",
            padx=15,
            cursor="hand2"
        )

        bouton.pack(
            fill="x",
            padx=5,
            pady=2
        )


# ============================================================
# SÉLECTION DES ACTIONS
# ============================================================

def ouvrir_selection():

    global fenetre_selection

    if fenetre_selection is not None:

        try:

            if fenetre_selection.winfo_exists():

                fenetre_selection.lift()

                return

        except Exception:
            pass

    fenetre_selection = tk.Toplevel(
        fenetre
    )

    fenetre_selection.title(
        "Sélectionner les actions"
    )

    fenetre_selection.geometry(
        "700x600"
    )

    fenetre_selection.minsize(
        600,
        500
    )

    fenetre_selection.configure(
        bg=theme["panneau"]
    )

    titre_selection = tk.Label(
        fenetre_selection,
        text="Actions du CAC 40",
        font=("Segoe UI", 22, "bold"),
        fg=theme["texte"],
        bg=theme["panneau"]
    )

    titre_selection.pack(
        pady=(20, 5)
    )

    info = tk.Label(
        fenetre_selection,
        text="Sélectionne les actions à afficher",
        font=("Segoe UI", 10),
        fg=theme["texte_secondaire"],
        bg=theme["panneau"]
    )

    info.pack(
        pady=(0, 15)
    )

    cadre_scroll = tk.Frame(
        fenetre_selection,
        bg=theme["panneau"]
    )

    cadre_scroll.pack(
        fill="both",
        expand=True,
        padx=25
    )

    canvas_scroll = tk.Canvas(
        cadre_scroll,
        bg=theme["panneau"],
        highlightthickness=0
    )

    scrollbar = tk.Scrollbar(
        cadre_scroll,
        orient="vertical",
        command=canvas_scroll.yview
    )

    canvas_scroll.configure(
        yscrollcommand=scrollbar.set
    )

    scrollbar.pack(
        side="right",
        fill="y"
    )

    canvas_scroll.pack(
        side="left",
        fill="both",
        expand=True
    )

    cadre_interieur = tk.Frame(
        canvas_scroll,
        bg=theme["panneau"]
    )

    canvas_scroll.create_window(
        (0, 0),
        window=cadre_interieur,
        anchor="nw",
        width=610
    )

    def mettre_a_jour_scroll(event=None):

        canvas_scroll.configure(
            scrollregion=canvas_scroll.bbox("all")
        )

    cadre_interieur.bind(
        "<Configure>",
        mettre_a_jour_scroll
    )

    boutons_actions = {}

    def mettre_a_jour_bouton(nom):

        bouton = boutons_actions[nom]

        bouton.delete("all")

        if nom in actions_selectionnees:

            bouton.create_rectangle(
                2,
                2,
                283,
                38,
                fill=theme["accent"],
                outline=theme["accent"]
            )

            bouton.create_text(
                142,
                20,
                text="✓   " + nom,
                fill="#FFFFFF",
                font=("Segoe UI", 10, "bold")
            )

        else:

            bouton.create_rectangle(
                2,
                2,
                283,
                38,
                fill=theme["verre"],
                outline=theme["bordure"]
            )

            bouton.create_text(
                142,
                20,
                text=nom,
                fill=theme["texte"],
                font=("Segoe UI", 10, "bold")
            )

    def cliquer_action(nom):

        if nom in actions_selectionnees:

            if len(actions_selectionnees) > 1:

                actions_selectionnees.remove(
                    nom
                )

        else:

            actions_selectionnees.add(
                nom
            )

        mettre_a_jour_bouton(
            nom
        )

    noms = list(
        actions_cac40.keys()
    )

    for i, nom in enumerate(noms):

        colonne = i % 2
        ligne = i // 2

        bouton = tk.Canvas(
            cadre_interieur,
            width=285,
            height=40,
            bg=theme["panneau"],
            highlightthickness=0,
            bd=0,
            cursor="hand2"
        )

        bouton.grid(
            row=ligne,
            column=colonne,
            padx=8,
            pady=4
        )

        boutons_actions[nom] = bouton

        mettre_a_jour_bouton(
            nom
        )

        bouton.bind(
            "<Button-1>",
            lambda event, n=nom:
            cliquer_action(n)
        )

    bas = tk.Frame(
        fenetre_selection,
        bg=theme["panneau"]
    )

    bas.pack(
        fill="x",
        pady=15
    )

    def tout_selectionner():

        actions_selectionnees.clear()

        actions_selectionnees.update(
            actions_cac40.keys()
        )

        for nom in boutons_actions:

            mettre_a_jour_bouton(nom)

    def tout_deselectionner():

        premier = list(
            actions_cac40.keys()
        )[0]

        actions_selectionnees.clear()

        actions_selectionnees.add(
            premier
        )

        for nom in boutons_actions:

            mettre_a_jour_bouton(nom)

    bouton_tout = tk.Button(
        bas,
        text="Tout sélectionner",
        command=tout_selectionner,
        bg=theme["verre"],
        fg=theme["texte"],
        activebackground=theme["verre_hover"],
        activeforeground=theme["texte"],
        relief="flat",
        padx=15,
        pady=7,
        cursor="hand2"
    )

    bouton_tout.pack(
        side="left",
        padx=5
    )

    bouton_aucun = tk.Button(
        bas,
        text="Tout désélectionner",
        command=tout_deselectionner,
        bg=theme["verre"],
        fg=theme["texte"],
        activebackground=theme["verre_hover"],
        activeforeground=theme["texte"],
        relief="flat",
        padx=15,
        pady=7,
        cursor="hand2"
    )

    bouton_aucun.pack(
        side="left",
        padx=5
    )

    def valider():

        global fenetre_selection

        fenetre_selection.destroy()

        fenetre_selection = None

        actualiser_donnees()

    bouton_valider = tk.Button(
        bas,
        text="✓   Valider",
        command=valider,
        bg=theme["accent"],
        fg="#FFFFFF",
        activebackground=theme["accent"],
        activeforeground="#FFFFFF",
        relief="flat",
        padx=20,
        pady=7,
        cursor="hand2",
        font=("Segoe UI", 10, "bold")
    )

    bouton_valider.pack(
        side="right",
        padx=10
    )


# ============================================================
# THÈME
# ============================================================

def changer_theme():

    global theme

    if theme == THEME_SOMBRE:

        theme = THEME_CLAIR

    else:

        theme = THEME_SOMBRE

    appliquer_theme()


def appliquer_theme():

    fenetre.configure(
        bg=theme["fond_bas"]
    )

    conteneur.configure(
        bg=theme["panneau"],
        highlightbackground=theme["bordure"]
    )

    header.configure(
        bg=theme["panneau"]
    )

    titre.configure(
        bg=theme["panneau"],
        fg=theme["texte"]
    )

    sous_titre.configure(
        bg=theme["panneau"],
        fg=theme["texte_secondaire"]
    )

    live_frame.configure(
        bg=theme["panneau"]
    )

    live_point.configure(
        bg=theme["panneau"],
        fg=theme["accent"]
    )

    live_label.configure(
        bg=theme["panneau"],
        fg=theme["texte"]
    )

    barre_commandes.configure(
        bg=theme["panneau"]
    )

    zone_principale.configure(
        bg=theme["panneau"]
    )

    sidebar.configure(
        bg=theme["panneau"]
    )

    label_selection.configure(
        bg=theme["panneau"],
        fg=theme["texte"]
    )

    cadre_scroll_actions.configure(
        bg=theme["panneau"]
    )

    canvas_actions.configure(
        bg=theme["panneau"]
    )

    cadre_actions.configure(
        bg=theme["panneau"]
    )

    graph_frame.configure(
        bg=theme["graphique"],
        highlightbackground=theme["bordure"]
    )

    statut_label.configure(
        bg=theme["panneau"],
        fg=theme["texte_secondaire"]
    )

    if bouton_actions is not None:

        bouton_actions.configure(
            bg=theme["panneau"]
        )

        bouton_actions.dessiner()

    if bouton_periode is not None:

        bouton_periode.configure(
            bg=theme["panneau"]
        )

        bouton_periode.dessiner()

    if bouton_theme is not None:

        bouton_theme.configure(
            bg=theme["panneau"]
        )

        bouton_theme.dessiner()

    if bouton_actualiser is not None:

        bouton_actualiser.configure(
            bg=theme["panneau"]
        )

        bouton_actualiser.dessiner()

    dessiner_fond()

    actualiser_graphique()


# ============================================================
# BOUTONS PRINCIPAUX
# ============================================================

bouton_actions = creer_bouton_verre(
    barre_commandes,
    lambda: "☰   Actions",
    ouvrir_selection,
    175
)

bouton_periode = creer_bouton_verre(
    barre_commandes,
    lambda: periode_actuelle + "   ▾",
    ouvrir_menu_periode,
    150
)

bouton_theme = creer_bouton_verre(
    barre_commandes,
    lambda: "☼   Thème",
    changer_theme,
    130
)

bouton_actualiser = creer_bouton_verre(
    barre_commandes,
    lambda: "↻   Actualiser",
    actualiser_donnees,
    160
)


# ============================================================
# LANCEMENT
# ============================================================

afficher_actions_sidebar()

fenetre.after(
    500,
    actualiser_donnees
)

fenetre.after(
    2000,
    verifier_marche
)

fenetre.after(
    INTERVALLE_ACTUALISATION,
    actualisation_automatique
)


# ============================================================
# DÉMARRAGE
# ============================================================

fenetre.mainloop()


