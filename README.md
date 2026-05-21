# Live Golf Scoreboard and Admin Panel

Een modern, responsive en live-verversend golf scorebord systeem speciaal ontwikkeld voor golftoernooien. Het systeem ondersteunt zowel Strokeplay als Stableford formules, beschikt over automatische speelhandicap-berekeningen (CR/SR), live projected cut-lijnen en een geoptimaliseerde mobiele interface voor scorers in de baan.

---

## Features

### Publiek Scorebord (Frontend)
* **Live Updates:** Ververst automatisch elke 10 seconden op de achtergrond zonder de pagina te herladen.
* **Dynamische Cut-lijn:** Toont een geprojecteerde rode cut-lijn op basis van het ingestelde percentage. Spelers die al aan ronde 2 zijn begonnen, worden automatisch beschermd en zakken nooit meer onder de cut-zone.
* **Live Progressie:** Toont in realtime per speler welke hole ze hebben gespeeld (THRU), inclusief visuele kleurcoderingen voor Birdies (rood), Eagles (oranje), Bogeys (blauw) en Double+ Bogeys (paars).
* **Auto-wissel:** Ingebouwde timer die automatisch elke 10 seconden schakelt tussen het heren- en damesklassement (ideaal voor TV-schermen in het clubhuis).
* **Slimme R1/R2 Weergave:** Toont onder het totale aantal slagen van een ronde in het klein de score ten opzichte van de par van de baan tot dan toe (bijv. E, +3 of -1).

### Admin Panel and Scorer Functionaliteiten
* **Sessie-beveiliging:** Maakt gebruik van sessionStorage in plaats van localStorage. Zodra de scorer of admin de browser volledig afsluit, wordt de token vernietigd en moet er opnieuw ingelogd worden.
* **Mobiele Flight-Invoer:** Scorers in de baan kunnen via een mobiele 'wizard' een flight van maximaal 3 spelers samenstellen. Deze selectie blijft via het browsergeheugen bewaard bij een pagina-refresh of netwerkwegval.
* **Smooth UI Notifications:** Geen storende pop-ups (alert()). Alle acties (baan toevoegen, cut toepassen, etc.) tonen een vloeiende, tijdelijke notificatiebalk bovenin het scherm.
* **Zichtbaarheidsbeheer:** Toernooien staan bij het aanmaken standaard op Verborgen (Invisible). Pas na activatie door de admin verschijnen ze live op de homepage.
* **Cut Beheer:** Bereken een live preview van de cut, pas deze definitief toe (spelers krijgen de status CUT), of draai de cut met één druk op de knop weer volledig terug.
* **CSV Import:** Voeg snel een volledige startlijst toe via een .csv bestand.

---

## Technologie Stack

* **Frontend:** Vue 3 (Composition API / script setup), Vue Router, Bootstrap 5 (voor een strakke, mobielvriendelijke UI).
* **Backend:** FastAPI (Python 3), SQLAlchemy ORM, Pydantic, Uvicorn.
* **Database:** SQLite (golf.db) - lichtgewicht en snel.
* **Productie/Hosting:** Nginx (als reverse proxy op een Raspberry Pi) and Let's Encrypt (voor gratis, automatische SSL/HTTPS).

---

## Snel opstarten met Docker Compose

De snelste manier om de volledige applicatie (frontend en backend) te draaien is via Docker Compose. Dit zorgt ervoor dat alle benodigde services automatisch in containers worden opgestart en met elkaar verbonden worden.

### Vereisten
Zorg ervoor dat Docker en Docker Compose op het systeem (of de Raspberry Pi) geïnstalleerd zijn.

### Installatie en Uitvoering
1. Zorg ervoor dat er een `docker-compose.yml` bestand in de hoofdmap van het project staat.
2. Start de applicatie op de achtergrond met het volgende commando:
   ```bash
   docker-compose up -d --build
