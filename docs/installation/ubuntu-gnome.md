# Ubuntu 24.04 LTS und GNOME

## Ausgangssituation und Systementscheidung

Der erste Installationsversuch erfolgte mit Ubuntu 26.04.1 LTS. Der IONOS/Acronis-Installer brach mit einer Paketprüfungsfehlermeldung für `dkms-3.10.16.1-99.noarch` ab (`does not verify: no digest`). Der Agent wurde nicht in der Backup-Konsole registriert und der Dienst `acronis_mms` konnte nicht gefunden werden. Ein Zusammenhang mit der Ubuntu-Version wurde vermutet, aber **nicht endgültig diagnostiziert**.

Da der Server zu diesem Zeitpunkt keine relevanten Nutzdaten enthielt, wurde er über das IONOS Cloud Panel mit **Ubuntu 24.04 LTS (ohne Plesk, ohne n8n)** neu installiert. Nach einer anfangs fehlgeschlagenen Browser-Konsolenverbindung wurde die Installation wiederholt; anschließend funktionierten Anmeldung und Konsole.

## 1. Installation im IONOS Cloud Panel

1. Im Cloud Panel den VPS öffnen.
2. **Betriebssystem neu installieren** auswählen.
3. **Ubuntu 24.04** (nicht „24.04 + Plesk“ oder „24.04 + n8n“) wählen.
4. Neuinstallation bestätigen. **Vorsicht: Dabei können vorhandene Daten gelöscht werden.**
5. Nach Abschluss einige Minuten warten und die IONOS Browser-Konsole öffnen.
6. Mit dem neu zugewiesenen Betriebssystemkonto anmelden.

Die **IONOS-Konsole** greift auf die virtuelle Konsolenausgabe des Servers zu; ein zusätzlicher RDP-Dienst war für den gewählten Nutzungsweg **nicht erforderlich**.

## 2. System aktualisieren

```bash
sudo apt update && sudo apt upgrade -y
```

`apt update` aktualisiert Paketmetadaten und `apt upgrade` installiert Updates **innerhalb** von Ubuntu 24.04. Ein Versionswechsel auf Ubuntu 26.04 wird damit nicht durchgeführt.

## 3. Grafische Oberfläche installieren

Auf dem VPS wurde die minimale Ubuntu-GNOME-Oberfläche installiert:

```bash
sudo apt install ubuntu-desktop-minimal -y
sudo systemctl set-default graphical.target
sudo systemctl enable gdm3
sudo reboot
```

Falls die Paketinstallation nach einem Displaymanager fragt: `gdm3` auswählen. Nach dem Neustart wurde die GNOME-Ersteinrichtung in der IONOS-Browser-Konsole abgeschlossen. Die grafische Oberfläche wurde dort erfolgreich angezeigt.

## 4. Prüfung

```bash
cat /etc/os-release
systemctl get-default
systemctl status gdm3
free -h
```

Erwartung: Ubuntu 24.04, `graphical.target`, laufender Displaymanager. Die 4 GB RAM reichen für den dokumentierten Entwicklungsbetrieb; GNOME ist jedoch speicherintensiver als eine reine Serverinstallation.

## Verweise

- [Nächster Schritt: Backup-Agent](backup-agent.md)
- [Fehlerbehebung: Konsole und Installer](../technik/troubleshooting.md)
