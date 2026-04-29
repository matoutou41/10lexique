# 10lex — v1.3.0

Petit outil Windows qui corrige, traduit et améliore **n'importe quel texte sélectionné** via un raccourci clavier — propulsé par l'API Anthropic (Claude) ou Google (Gemini).

Site officiel : [10lexique.pplx.app](https://10lexique.pplx.app)

---

## Nouveautés v1.3

- 🦖 **Nouvelle identité visuelle** : palette violet/lavande cartoon, polices Comic Sans / Bahnschrift, dino mascotte
- 🏷️ **Renommage** : l'app s'appelle désormais **10lex** (icône + nom Windows + tray)
- ✨ **Cohérence visuelle 100 %** avec la landing 10lexique.pplx.app

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

Récupérez **`10lex-Setup-1.3.0.exe`** depuis [la page de releases GitHub](https://github.com/matoutou41/10lexique/releases/latest) et double-cliquez. L'installateur :

- Installe l'app dans `C:\Program Files\10lex`
- Propose un raccourci sur le bureau
- Propose le lancement automatique au démarrage de Windows
- Ajoute un désinstallateur dans **Panneau de configuration > Programmes**

### Pour générer l'installateur (vous, dev)

**Pré-requis** :

1. [Python 3.10+](https://www.python.org/downloads/) (cochez "Add Python to PATH")
2. [Inno Setup 6](https://jrsoftware.org/isdl.php) (installez avec les options par défaut)

**Étapes** :

1. Clonez le repo
2. Double-cliquez sur **`build.bat`**
3. ~3 minutes plus tard, vous avez :
   - `dist\10lex.exe` — l'EXE autonome
   - `installer_output\10lex-Setup-1.3.0.exe` — l'installateur à distribuer

---

## Configuration

Au premier lancement, la fenêtre Paramètres s'ouvre. Plus tard : clic droit sur l'icône de la barre des tâches → **Paramètres**.

### Connexion

- **Provider** : Anthropic (Claude) ou Google (Gemini)
- **Clé API** :
  - Anthropic : [console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys)
  - Google : [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
- **Modèle** :
  - Anthropic : `claude-haiku-4-5` (recommandé, économique), `claude-sonnet-4-6`, `claude-opus-4-7`
  - Google : `gemini-2.0-flash` (rapide), `gemini-2.5-pro` (qualité)

### Raccourcis clavier

Par défaut :
- Corriger : `alt+k`
- Traduire : `alt+l`
- Améliorer : `alt+m`

Format accepté : `alt+k`, `ctrl+shift+espace`, `f9`, `ctrl+alt+c`, etc.

### Préférences

- **Langue cible (traduction)** : english, french, japanese, spanish, german, italian, chinese, korean
- **Style d'amélioration** : neutral, formal, casual, shorter, longer

La config est stockée dans `%APPDATA%\10lex\config.json`.

---

## Désinstallation

**Si installé via l'installateur** : Panneau de configuration → Programmes et fonctionnalités → **10lex** → Désinstaller.

**Si lancé en mode dev / EXE simple** : supprimez le dossier. Pour aussi enlever la config : supprimez `%APPDATA%\10lex\`.

---

## Coût

Avec Claude Haiku 4.5 (1 $ / 5 $ par million de tokens) :
- Une action sur 200 mots ≈ **0,001 €**
- 1000 utilisations / mois ≈ **1 €**
