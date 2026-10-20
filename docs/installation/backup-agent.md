# IONOS Cloud Backup-Agent

## Zweck und Status

Der **IONOS Cloud Backup-Agent (Acronis Cyber Protect)** wurde auf Ubuntu 24.04 installiert. Der Installer meldete ausdrücklich **„Cyber Protection Agent has been successfully installed in the system“**. Im Anschluss erschien der Server in der IONOS Backup-Konsole; die Registrierung wurde somit bestätigt.

> **Abgrenzung:** Eine erfolgreiche Agent-Installation und Registrierung beweist **nicht**, dass bereits ein vollständiger Sicherungslauf erfolgreich abgeschlossen oder eine Wiederherstellung getestet wurde. Diese beiden Nachweise sind separat zu dokumentieren.

## 1. Voraussetzungen

- Aktiver IONOS-VPS und freigeschaltetes Backup-Paket.
- Zugriff auf IONOS Cloud Panel und Ubuntu-Terminal.
- Ausreichender Speicherplatz im gebuchten Backup-Paket.
- Ausgehende Netzwerkverbindungen für den Backup-Dienst; laut zugrunde liegender IONOS-Anleitung ggf. TCP-Ports **443, 8443, 7770–7800 und 44445** erlauben, sofern eine eigene ausgehende Firewall diese blockiert. Nur für die IONOS-Konto-Firewall war laut Anleitung keine zusätzliche Freigabe notwendig.

## 2. Installer beschaffen

Im **IONOS Cloud Panel → Backup → Backup-Paket → Verwaltung → Backup-Agent für Server → Linux → Download-Agent** die Region **Europa** wählen. Die Datei `backup-agent-installer-Europe-Linux.sh` wurde in `~/Downloads` auf den Server geladen.

## 3. Installation

```bash
cd ~/Downloads
chmod +x backup-agent-installer-Europe-Linux.sh
sudo ./backup-agent-installer-Europe-Linux.sh
```

`sudo` ist erforderlich: Der Agent installiert Systempakete und schreibt in geschützte Verzeichnisse wie `/var/lib` und `/var/log`. Ohne Root-Rechte erschienen zuvor Meldungen wie `Permission denied`, `Unable to lock directory` und `You should run this program as root`.

Während der erfolgreichen Installation erschien die Meldung `The UTF8 kernel module is missing`. Die Installation lief dennoch weiter und endete erfolgreich. Diese Zwischenmeldung wurde im vorliegenden Fall **nicht** als endgültiger Installationsfehler bewertet.

## 4. Registrierung prüfen

1. Die Abschlussmeldung des Installers kontrollieren.
2. IONOS **Backup-Konsole** öffnen.
3. Unter **Geräte** prüfen, ob der Server sichtbar ist.
4. Falls er fehlt: Logs kontrollieren und die IONOS-/Acronis-Registrierung gezielt prüfen; die bloße Installation reicht nicht als Nachweis.

Die konkrete systemd-Dienstbezeichnung des installierten Agenten kann je nach Acronis-Version abweichen. Daher nicht blind von `acronis_mms.service` ausgehen. Alternativ zuerst Dienste suchen:

```bash
systemctl list-unit-files | grep -Ei 'acronis|mms|cyber'
sudo tail -n 50 /var/log/trueimage-setup.log
```

## 5. Datensicherung für den Betrieb planen

Für ein sinnvolles Sicherungskonzept müssen anschließend in der Backup-Konsole Schutzplan, Aufbewahrungsdauer und Ziel bestätigt werden:

1. **Gesamte Maschine** sichern (falls laut IONOS-Produkt/Plan verfügbar).
2. Regelmäßige Sicherung mit angemessener Aufbewahrung konfigurieren.
3. Ersten manuellen Lauf starten und im Bereich **Aktivitäten** auf „erfolgreich“ prüfen.
4. Wiederherstellung oder zumindest einen kontrollierten Restore-Test separat durchführen.
5. Zusätzlich über logische PostgreSQL-Sicherungen nachdenken (`pg_dump`), da ein Maschinenbackup keine anwendungsbezogene Restore-Probe ersetzt.

**Ist-Stand:** Agent installiert und registriert; konkreter Sicherungsplan, ein abgeschlossener Backup-Lauf und Restore-Test sind **hier nicht als bestätigt dokumentiert**.

Siehe auch [Betrieb, Backups und Sicherheitskontrollen](../technik/betrieb-sicherheit.md).
