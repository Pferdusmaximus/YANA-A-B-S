# Technische Entscheidungen und Begründungen

## VPS statt ausgelagerter Datenbank-Hostingplattform

Das Projekt verwendet einen bestehenden IONOS-VPS mit **2 vCores und 4 GB RAM**. PostgreSQL und das Python-Backend werden auf demselben Server betrieben. Damit können Infrastruktur und Datenbank selbst verwaltet sowie das Deployment nachvollziehbar dokumentiert werden.

### FastAPI statt selbst gehosteter Supabase-Gesamtumgebung

Zu Beginn wurde Supabase erwogen. Da die Gruppe PostgreSQL bereits auf dem VPS eingerichtet hatte und der verfügbare RAM begrenzt ist, wurde stattdessen ein **leichtgewichtiges FastAPI-Backend** mit direktem PostgreSQL-Zugriff ausgewählt.

| Kriterium | FastAPI + PostgreSQL (gewählt) | Selbst gehosteter Supabase-Stack (erwogen) |
|---|---|---|
| Ressourcen | Wenige erforderliche Dienste | Mehrere Dienste und Abhängigkeiten |
| Geschäftslogik | Frei programmierbare Python-Endpunkte | Kombination aus vorgefertigten Diensten und zusätzlicher Logik |
| Datenbank | Vorhandenes PostgreSQL nutzbar | PostgreSQL ebenfalls Kernkomponente |
| Authentifizierung/Storage/Realtime | Muss bei Bedarf separat implementiert werden | Je nach Deployment Bestandteil des Ökosystems |
| Betriebsverantwortung | Selbst zu tragen | Bei Self-Hosting ebenfalls selbst zu tragen |

**Einordnung:** Der höhere Ressourcenbedarf bezieht sich auf eine **selbst gehostete** umfassende Supabase-Installation und ist keine generelle Aussage gegen den gehosteten Supabase-Dienst. FastAPI ersetzt auch nicht automatisch sämtliche Supabase-Funktionen.

## Ubuntu 24.04 statt Ubuntu 26.04

Auf Ubuntu 26.04.1 LTS schlug der verwendete IONOS/Acronis-Installer mit einem Paketprüfungsfehler fehl. Da der Server noch keine relevanten Nutzdaten enthielt, wurde er mit Ubuntu **24.04 LTS** neu aufgesetzt. Danach konnte der Agent installiert und registriert werden. **Die Ursache des ursprünglichen Fehlers wurde nicht abschließend bewiesen.**

## PostgreSQL statt SQLite/MongoDB

Das relationale ER-Modell (Hilfestellen, Kategorien, Leistungen, Nachrichten) benötigt strukturierte Beziehungen und referenzielle Integrität. PostgreSQL unterstützt die geforderten **Primär-/Fremdschlüssel, Transaktionen, relationale Abfragen und spätere Geodaten-Erweiterungen**. Die Entscheidung ist in [Datenmodell](datenmodell.md) praktisch umgesetzt.

## GNOME und pgAdmin Desktop

Die IONOS-Konsole wurde als grafische Bedienoberfläche genutzt. Daher erfolgte die Installation von `ubuntu-desktop-minimal` und `pgadmin4-desktop`. Ein zusätzlicher RDP-Zugang wurde **nicht** eingerichtet. Für 4 GB RAM ist das grundsätzlich möglich, reduziert aber die Reserven für zusätzliche Serverdienste.

## Nginx, systemd und HTTPS

- **systemd** betreibt die API unabhängig vom Terminal und startet sie bei Fehlern erneut.
- **Nginx** ist ein separater Reverse Proxy für öffentliche HTTPS-Verbindungen; Uvicorn lauscht nur auf Loopback.
- **Let's Encrypt** liefert ein echtes öffentlich vertrauenswürdiges Zertifikat für die IP-Adresse; ein Staging-Zertifikat wurde im Setup erkannt und ersetzt.
- **Certbot-Timer + Deploy Hook** automatisieren die Zertifikatserneuerung und den Nginx-Reload.

## Offene Entscheidungen

- Authentifizierungsmodell (einschließlich anonymer Beratung und Admin-Oberfläche).
- Rollenmodell in PostgreSQL und FastAPI.
- Standortbasierte Suche und Umgang mit potenziell vertraulichen Hilfsstandorten.
- Art und Dauer der Chatdatenspeicherung.
- Getrennte Deployment-/Test-/Produktivumgebungen.
- Ressourcenmonitoring und Lasttests auf 2 vCores / 4 GB RAM.
- App-Integration mit Flutter (nächster Projektabschnitt).
