# Holistic Game Changer - Open-Source Bildungs-Prototyp (English-version below)

Dieses Repository enthält den Quellcode für eine lokale Tracking-Anwendung, die im Zuge eines YouTube-Tutorials als Anschauungsmaterial für die App-Entwicklung mit Python und Kivy dient.

## ⚠️ WICHTIGER RECHTLICHER HINWEIS & DISCLAIMER

### 1. Kein Medizinprodukt / Keine therapeutische Beratung
Die hier dargestellte Anwendung und die damit verbundenen Inhalte (Videos, Texte, Code-Beispiele) dienen **ausschließlich Bildungs-, Lehr- und Demonstrationszwecken**. Es handelt sich ausdrücklich **nicht** um ein Medizinprodukt, eine gesundheitliche Beratung oder ein therapeutisches Werkzeug. 

Die Erfassung von Daten wie Wohlbefinden, Stress oder Gewohnheiten (z. B. Kälteanwendungen, Meditation) dient rein der programmtechnischen Demonstration von Datenflüssen in Kivy. Die Nutzung des Codes und das eigenständige Kompilieren zu einer App erfolgen zu 100 % auf eigene Verantwortung und eigenes Risiko des Nutzers. Bei gesundheitlichen Beschwerden ist stets qualifizierter ärztlicher Rat einzuholen.

### 2. Haftungsausschluss (Software)
Der Code wird "wie besehen" (as is) und ohne jegliche Gewährleistung oder Funktionsgarantie zur Verfügung gestellt. Der Autor übernimmt keine Haftung für Schäden an Hardware, Datenverlust oder Fehlfunktionen, die durch das eigenständige Kompilieren oder Modifizieren des Codes entstehen.

### 3. Datenschutz-Hinweis (100% Lokal)
Dieser Prototyp verfügt über keinerlei Server-Anbindung, Tracking-Skripte oder Cloud-Schnittstellen. Alle eingegebenen Daten werden über das Kivy-Modul `JsonStore` ausschließlich **lokal im isolierten Speicherbereich des jeweiligen Endgeräts** in einer JSON-Datei gesichert. Es findet keine Datenübertragung an den Autor oder Dritte statt.

---

## Technische Voraussetzungen für Bastler

Wer den Code experimentell auf dem eigenen Smartphone unter Android ausführen möchte, benötigt:
* Python 3.x
* Kivy Framework
* Buildozer (zum Kompilieren für Android)

### Schnellstart (Lokaler PC-Test)
1. Code kopieren
2. Kivy installieren: `pip install kivy`
3. Skript starten: `python main.py`

## English-version:

# Holistic Game Changer – Open-Source Educational Prototype

This repository contains the source code for a local tracking application, created as a demonstration project for an app development tutorial using Python and Kivy.

## ⚠️ IMPORTANT LEGAL NOTICE & DISCLAIMER

### 1. Not a Medical Device / No Therapeutic Advice
The application presented here and its associated content (videos, text, code examples) are intended **exclusively for educational, instructional, and demonstration purposes**. It is expressly **not** a medical device, a source of health advice, or a therapeutic tool.

The tracking of data such as well-being, stress, or habits (e.g., cold exposure, meditation) serves purely to demonstrate data flow within the Kivy framework. Users utilize the code and compile the app entirely at their own risk and responsibility. Always seek qualified medical advice regarding any health concerns.

### 2. Liability Disclaimer (Software)
The code is provided "as is," without any warranty or guarantee of functionality. The author assumes no liability for hardware damage, data loss, or malfunctions resulting from the independent compilation or modification of the code.

### 3. Data Privacy Notice (100% Local)
This prototype has no server connections, tracking scripts, or cloud interfaces. All data entered is saved exclusively **locally within the device's isolated storage area** in a JSON file, using the Kivy `JsonStore` module. No data is transmitted to the author or any third parties. ---

## Technical Requirements for Hobbyists

If you want to run the code experimentally on your own Android smartphone, you will need:
* Python 3.x
* Kivy framework
* Buildozer (for compiling for Android)

### Quick Start (Local PC Test)
1. Copy the code
2. Install Kivy: `pip install kivy`
3. Run the script: `python main.py`
