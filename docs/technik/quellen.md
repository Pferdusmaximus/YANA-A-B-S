# Technische Quellen und weiterführende Dokumentation

Diese Quellen wurden für die Überprüfung von Installationsverfahren, Schnittstellen und Dokumentationsformat herangezogen. Als Grundlage der **tatsächlich ausgeführten Schritte** dienen zusätzlich die protokollierten Tests während der Einrichtung.

| Fachgebiet | Offizielle Quelle |
|---|---|
| Ubuntu Server | [Ubuntu Server Documentation](https://documentation.ubuntu.com/server/) |
| PostgreSQL 16 | [PostgreSQL 16 Documentation](https://www.postgresql.org/docs/16/) |
| pgAdmin unter Ubuntu | [pgAdmin 4 – APT Installation](https://www.pgadmin.org/download/pgadmin-4-apt/) |
| FastAPI | [FastAPI – Deployment](https://fastapi.tiangolo.com/deployment/) |
| Psycopg 3 | [Psycopg 3 – Basic Usage](https://www.psycopg.org/psycopg3/docs/basic/usage.html) |
| Nginx | [NGINX – ngx_http_proxy_module](https://nginx.org/en/docs/http/ngx_http_proxy_module.html) |
| Let's Encrypt IP-Zertifikate | [6-day and IP Address Certificates – GA (2026)](https://letsencrypt.org/2026/01/15/6day-and-ip-general-availability) |
| Certbot für IP-Zertifikate | [Six-Day and IP Address Certificates Available in Certbot (2026)](https://letsencrypt.org/2026/03/11/shorter-certs-certbot) |
| Certbot-Dokumentation | [Certbot – User Guide](https://eff-certbot.readthedocs.io/en/stable/using.html) |
| MkDocs | [MkDocs – Documentation](https://www.mkdocs.org/user-guide/) |
| Material for MkDocs | [Mermaid-Diagramme](https://squidfunk.github.io/mkdocs-material/reference/diagrams/) |
| GitHub Pages | [GitHub Pages Documentation](https://docs.github.com/en/pages) |

## Dokumentationsprinzipien

- **Ist-Zustand vor Soll-Zustand:** Abgeschlossene Installations- und Testschritte sind ausdrücklich von geplanten Funktionen getrennt.
- **Reproduzierbarkeit:** Pfade, Dienste, Ports, SQL und Konfigurationsdateien sind angegeben.
- **Sicherheit:** Echte Zugangsdaten und nicht öffentliche Schlüssel sind ausgeschlossen.
- **Änderbarkeit:** Änderungen an Code, Schema, Ressourcen und Laufzeit sollten künftig mit Datum ergänzt werden.
