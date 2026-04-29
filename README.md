# Claude Correcteur — v3

Petit outil Windows qui corrige, traduit et améliore **n'importe quel texte sélectionné** via un raccourci clavier — propulsé par l'API Claude.

Design inspiré de [LocalSend](https://localsend.org/) : sombre, arrondi, accent menthe, sans fioritures.

---

## Nouveautés v3

- 🎨 **Nouveau design** sombre et arrondi (CustomTkinter), inspiré de LocalSend
- 🪟 **Popup flottante** sans bordure, qui se ferme automatiquement quand on clique en dehors
- 📍 **Position intelligente** : la popup se place sous votre curseur sans recouvrir la zone d'édition
- 🗂️ **3 onglets dans la même popup** : Corriger, Traduire, Améliorer
- ⌨️ **Raccourcis** : `Alt+K` (corriger), `Alt+L` (traduire), `Alt+M` (améliorer)
- 📦 **Installateur Inno Setup** avec raccourci bureau, démarrage Windows et désinstallateur

---

## Utilisation

1. Sélectionnez du texte n'importe où (navigateur, Word, Discord, mail…)
2. Appuyez sur :
   - **`Alt+K`** pour corriger l'orthographe
   - **`Alt+L`** pour traduire (langue cible configurable)
   - **`Alt+M`** pour améliorer / reformuler
3. La popup apparaît à côté de votre curseur :
   - À gauche : 3 onglets pour basculer entre les actions
   - En haut : votre texte original
   - En bas : le résultat (modifiable avant application)
4. **Appliquer** → remplace dans le champ d'origine, ou **Copier** → met dans le presse-papier
5. Cliquez en dehors ou appuyez sur **Échap** pour fermer

---

## Installation

### Pour un utilisateur final (recommandé)

Récupérez **`ClaudeCorrecteur-Setup-1.0.0.exe`** (généré par `build.bat`) et double-cliquez. L'installateur :

- Installe l'app dans `C:\Program Files\ClaudeCorrecteur`
- Propose un raccourci sur le bureau
- Propose le lancement automatique au démarrage de Windows
- Ajoute un désinstallateur dans **Panneau de configuration > Programmes**

### Pour générer l'installateur (vous, dev)

**Pré-requis** :

1. [Python 3.10+](https://www.python.org/downloads/) (cochez "Add Python to PATH")
2. [Inno Setup 6](https://jrsoftware.org/isdl.php) (installez avec les options par défaut)

**Étapes** :

1. Décompressez `claude-correcteur-v3`
2. Double-cliquez sur **`build.bat`**
3. ~3 minutes plus tard, vous avez :
   - `dist\ClaudeCorrecteur.exe` — l'EXE autonome
   - `installer_output\ClaudeCorrecteur-Setup-1.0.0.exe` — l'installateur à distribuer

> ℹ️ Si Inno Setup n'est pas installé, le build s'arrête après la génération de l'EXE et vous indique où télécharger Inno Setup. Vous pouvez aussi distribuer juste `ClaudeCorrecteur.exe` sans installateur.

### Pour modifier le code (mode dev)

```bat
build.bat                  REM première fois (installe les dépendances)
lancer-dev.bat             REM lance avec console pour voir les erreurs
```

---

## Configuration

Au premier lancement, la fenêtre Paramètres s'ouvre. Plus tard : clic droit sur l'icône de la barre des tâches → **Paramètres**.

### Connexion

- **Clé API Anthropic** : à récupérer sur [console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys)
- **Modèle** :
  - `claude-haiku-4-5` (recommandé — rapide, ~0,001 € par usage)
  - `claude-sonnet-4-6` (plus précis, plus cher)
  - `claude-opus-4-7` (qualité max)

### Raccourcis clavier

Par défaut :
- Corriger : `alt+k`
- Traduire : `alt+l`
- Améliorer : `alt+m`

Format accepté : `alt+k`, `ctrl+shift+espace`, `f9`, `ctrl+alt+c`, etc. Modification appliquée immédiatement.

### Préférences

- **Langue cible (traduction)** : english, french, japanese, spanish, german, italian, chinese, korean
- **Style d'amélioration** : neutral, formal, casual, shorter, longer

La config est stockée dans `%APPDATA%\ClaudeCorrecteur\config.json`.

---

## Comportement de la popup

- **Ferme au clic extérieur** : pas besoin de cliquer sur Fermer
- **Échap** ferme aussi
- **Position intelligente** : sous le curseur si possible, au-dessus sinon, jamais sous les bords
- **Sans bordure** : look flottant, pas de barre de titre Windows
- **Toujours au premier plan** quand affichée

### Astuce pour le bouton "Appliquer"

Quand vous cliquez "Appliquer", la popup se cache et Windows redonne automatiquement le focus à la fenêtre précédente, puis le texte est remplacé. **Ne cliquez pas dans une autre app entre le raccourci et "Appliquer"** — sinon le focus ira dans la mauvaise fenêtre.

Si jamais le remplacement rate, le résultat est de toute façon dans le presse-papier (Ctrl+V manuel possible).

---

## Architecture

```
claude-correcteur-v3/
├── build.bat                # Build EXE + Installateur
├── lancer-dev.bat           # Mode dev avec console
├── installer.iss            # Script Inno Setup
├── make_icon.py             # Génération de l'icône
├── requirements.txt
├── README.md
├── assets/
│   ├── icon.ico             # Icône Windows multi-résolution
│   └── icon.png             # Icône tray
└── src/
    ├── main.py              # Point d'entrée + hotkeys
    ├── popup.py             # Popup flottante 3 onglets
    ├── settings_window.py   # Fenêtre paramètres
    ├── theme.py             # Palette + polices
    ├── tray.py              # Icône barre des tâches
    ├── claude_client.py     # API Claude
    ├── text_handler.py      # Capture sélection
    ├── config.py            # Config %APPDATA%
    └── notifier.py          # Toasts Windows
```

**Un seul process Python** :
- Thread principal → boucle CustomTkinter (popup + paramètres)
- Thread tray → icône système (pystray)
- Thread hotkeys → raccourcis globaux (keyboard)
- Thread API → appels Claude non bloquants

---

## Désinstallation

**Si installé via l'installateur** : Panneau de configuration → Programmes et fonctionnalités → Claude Correcteur → Désinstaller.

**Si lancé en mode dev / EXE simple** : supprimez le dossier. Pour aussi enlever la config : supprimez `%APPDATA%\ClaudeCorrecteur\`.

---

## Coût

Avec Claude Haiku 4.5 (1 $ / 5 $ par million de tokens) :
- Une action sur 200 mots ≈ **0,001 €**
- 1000 utilisations / mois ≈ **1 €**

Suivi : [console.anthropic.com](https://console.anthropic.com/)
