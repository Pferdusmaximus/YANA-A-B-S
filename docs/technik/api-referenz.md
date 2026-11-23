# HTTP-Schnittstellen: öffentliche API und Verwaltungsportal

**Stand: 23. November 2026 · Partner- und Accountverwaltung ergänzt**

## Zugriffswege

| Umgebung | Adresse | Zweck |
|---|---|---|
| Interne FastAPI | `http://127.0.0.1:8000` | Dienst auf dem VPS |
| Interner Nginx-Test | `http://127.0.0.1:8080` | Lokaler Reverse Proxy |
| Öffentlicher HTTPS-Zugang | `https://SERVER_IP` | Website, API und Portal |

`SERVER_IP` bezeichnet die tatsächlich konfigurierte Serveradresse. Datenbankport 5432 und internen FastAPI-Port 8000 nicht offen ins Internet stellen.

## 1. Öffentliche Endpunkte

| Methode | Pfad | Antwort / Bedeutung |
|---|---|---|
| `GET` | `/` | HTML-Website |
| `GET` | `/health` | HTTP-Status und JSON-Health-Antwort |
| `GET` | `/hilfestellen` | Nur Hilfestellen mit `publication_status = 'published'` |
| `GET` | `/kategorien` | Liste verfügbarer Kategorien |
| `GET` | `/notfallnummern` | Liste der Notfallnummern; in bisherigen Tests leer |
| `GET` | `/static/css/style.css` | Website-/Portal-CSS |
| `GET` | `/docs` | FastAPI-Swagger-Ansicht der sichtbaren API-Routen |

Einträge in `draft` oder `pending_review` werden bei `GET /hilfestellen` **nicht** ausgegeben. Für veröffentlichte Einträge gehören Adresse und Koordinaten weiterhin zum öffentlichen Datensatz; dies ist für echte Schutzstandorte **nicht geeignet**. Die Portal-Routen sind in Swagger ausgeblendet (`include_in_schema=False`), aber dadurch nicht sicherheitsgeschützt.

## 2. Anmeldung und Portal

| Methode | Pfad | Aktion |
|---|---|---|
| `GET` / `POST` | `/portal/login` | Loginformular / Anmeldung |
| `GET` | `/portal/dashboard` | Gemeinsames Dashboard (Admin/Partner) |
| `POST` | `/portal/logout` | Session beenden, CSRF |
| `GET` | `/portal/hilfestellen` | Rollenabhängige Hilfestellenübersicht |
| `GET` / `POST` | `/portal/passwort-aendern` | Eigenes Passwort ändern; bei Startpasswort zwingend |

Partner sehen im selben Portal nur zugewiesene Einrichtungen. Fremde IDs sind auch über direkte URLs nicht zugänglich. Für POST-Aktionen werden Login, Rolle, Zuordnung, CSRF und Eingaben geprüft.

## 3. Neue Einträge und Statusfreigabe

| Methode | Pfad | Erlaubter Nutzer / Funktion |
|---|---|---|
| `GET` / `POST` | `/portal/hilfestellen/neu` | Nur Admin; fiktiven Entwurf anlegen |
| `GET` / `POST` | `/portal/hilfestellen/{id}/edit` | Admin / zugeordneter Partner; nur bei `draft` |
| `POST` | `/portal/hilfestellen/{id}/status/submit` | Admin / zugeordneter Partner; Entwurf einreichen |
| `POST` | `/portal/hilfestellen/{id}/status/approve` | Nur Admin; `pending_review → published` |
| `POST` | `/portal/hilfestellen/{id}/status/reject` | Nur Admin; `pending_review → draft` |
| `POST` | `/portal/hilfestellen/{id}/status/unpublish` | Nur Admin; `published → draft` |

Die Statusaktionen validieren Übergänge und protokollieren Entscheidungen. Neue Einträge beginnen als `draft` und erscheinen erst nach Freigabe öffentlich.

## 4. Änderungsvorschläge für veröffentlichte Einträge

| Methode | Pfad | Beschreibung |
|---|---|---|
| `GET` | `/portal/hilfestellen/{id}/aenderung` | Formular für zugeordnete veröffentlichte Einrichtung |
| `POST` | `/portal/hilfestellen/{id}/aenderung` | `mode=save` oder `mode=submit`; getrennt speichern |
| `POST` | `/portal/hilfestellen/{id}/aenderung/discard` | Eigenen aktiven Entwurf verwerfen |
| `GET` | `/portal/aenderungen` | Admin-Warteschlange offener Anträge |
| `POST` | `/portal/aenderungen/{change_id}/approve` | Admin übernimmt gültige Änderung und protokolliert sie |
| `POST` | `/portal/aenderungen/{change_id}/reject` | Admin lehnt Antrag ab; veröffentlichten Datensatz nicht verändern |

Nur die vier Kontaktfelder `name`, `phone`, `email`, `opening_hours` gehören zum Änderungsantrag. Die Transaktion prüft, dass die ursprünglich veröffentlichten Werte zwischenzeitlich nicht verändert wurden.

## 5. Partner- und Accountverwaltung (23.11.2026)

| Methode | Pfad | Zugriff / Aktion |
|---|---|---|
| `GET` | `/portal/partner` | Admin: Partnerliste, Zuordnung und Accountverwaltung |
| `POST` | `/portal/partner/create` | Admin: Partner anlegen, zufälliges Startpasswort einmalig anzeigen |
| `POST` | `/portal/partner/{account_id}/assign` | Admin: Hilfestelle zuweisen |
| `POST` | `/portal/partner/{account_id}/unassign` | Admin: Zuordnung entfernen |
| `POST` | `/portal/partner/{account_id}/deactivate` | Admin: Account deaktivieren, Sessions beenden |
| `POST` | `/portal/partner/{account_id}/reactivate` | Admin: reaktivieren und neues Startpasswort ausgeben |
| `POST` | `/portal/partner/{account_id}/reset-password` | Admin: Passwort-Reset und Pflichtwechsel erzwingen |

Alle zustandsändernden Formulare prüfen CSRF. Ein Partner erhält für Administratoraktionen HTTP `403`. Die Startpasswortseite wird unmittelbar durch den POST gerendert und nicht als dauerhaft abrufbare GET-Ressource angelegt. Ein Passwortwechsel des betroffenen Accounts endet mit `303` zum Login.

Siehe [technische Benutzerverwaltung](teamportal-benutzerverwaltung.md).

## 6. HTTP-Verhalten

| Status | Typischer Fall |
|---|---|
| `200` | Webseite oder erlaubter GET-Endpunkt |
| `303` | Weiterleitung nach Formularaktion oder zum Login |
| `401` | Fehlende Anmeldung auf geschützter API-/POST-Route |
| `403` | Ungültiger CSRF-Token oder unzulässige Rolle |
| `404` | Nicht vorhandene bzw. für Partner nicht zugängliche Einrichtung |
| `409` | Konflikt mit aktuellem Veröffentlichungs- oder Antragsstatus |
| `422` | Ungültige Formulardaten oder Testdateneinschränkung |

Die konkreten Codes hängen von der Route und der Art des Aufrufs ab. Die Browseransicht nutzt Formulare, Cookies und Redirects, die Flutter-API ist davon getrennt.

## 7. Flutter Web und CORS

`main.py` erlaubt für die lokale Flutter-Web-Entwicklung GET-Anfragen von `http://localhost` bzw. `http://127.0.0.1` mit wechselnden Ports. Die CORS-Regel ist **keine** Authentifizierung und erlaubt keinen Portalzugang.

## 8. Smoke-Tests

```bash
curl -i https://SERVER_IP/
curl -i https://SERVER_IP/health
curl -i https://SERVER_IP/hilfestellen
curl -i https://SERVER_IP/kategorien
curl -i https://SERVER_IP/notfallnummern
```

Authentifizierte Portalabläufe testet man über Browser oder FastAPI `TestClient` mit HTTPS-Basisadresse und gültiger Session. Informationen zum verifizierten Teststand: [Portal-Tests](teamportal-tests.md).

## 9. Noch nicht umgesetzt

Eine Verwaltungsseite für Accounts/Zuweisungen und ein **Administrator-Passwort-Reset** sind implementiert. Es gibt weiterhin **keine öffentliche Selbstregistrierung**, keinen selbstständigen Passwort-vergessen-Prozess, keine MFA und keinen vollständigen Datenschutzfilter für reale Schutzstandorte. Chat-/Beratungs-API, Standortsuche, Push sowie die veröffentlichte App-Version gehören ebenfalls nicht zu diesem Stand.
