# Partner-Accounts verwalten

**Stand: 23. November 2026 · Anleitung für YANA-Administratoren und externe Partner**

Die Kontoverwaltung ist Bestandteil des bestehenden YANA-Portals. Alle Accounts nutzen den gemeinsamen Login unter **`/portal/login`**. **Neue Partner können sich nicht selbst registrieren.** Die Verwaltung unter **`/portal/partner`** ist ausschließlich für die Rolle `admin` erreichbar.

## 1. Neuen Partner anlegen

1. Als Administrator anmelden und im Dashboard **Partnerverwaltung** öffnen.
2. Unter **Neuen Partner erstellen** die E-Mail-Adresse des Partners eingeben.
3. **Partner erstellen** auswählen. Das Portal erzeugt automatisch ein sicheres Startpasswort und zeigt es **einmalig** an.
4. Das Startpasswort jetzt notieren bzw. auf einem geeigneten, geschützten Weg an den vorgesehenen Partner übergeben. **Nicht** im öffentlichen GitHub-Repository, in MkDocs, in Screenshots oder in ungeschützten Nachrichten hinterlegen.
5. Zurück zur Partnerverwaltung wechseln und die gewünschten Hilfestellen zuweisen.

Die neue Rolle ist automatisch `partner`. Es gibt keine frei auswählbare Administratorrolle im Formular. Ein bereits bestehender Account mit derselben E-Mail-Adresse wird nicht nochmals angelegt.

## 2. Erster Login und eigenes Passwort

1. Partner öffnet `/portal/login` und meldet sich mit E-Mail-Adresse und dem erhaltenen Startpasswort an.
2. Das Portal leitet zur Seite **`/portal/passwort-aendern`** weiter. Bis zum Passwortwechsel sind die regulären Verwaltungsfunktionen gesperrt.
3. Das bisherige Startpasswort sowie das neue Passwort zweimal eingeben. Das neue Passwort muss **14–128 Zeichen** lang und anders als das bisherige sein.
4. Nach dem Speichern meldet das Portal den Benutzer ab. Mit dem **neuen** Passwort erneut einloggen.
5. Im Dashboard **Hilfestellen verwalten** auswählen. Partner sehen nur ausdrücklich zugewiesene Einträge.

Die Seite **Eigenes Passwort ändern** kann später auch freiwillig über das Dashboard aufgerufen werden.

## 3. Einrichtungen zuweisen und entfernen

In der Partnerverwaltung steht unter jedem aktiven Partner die Liste **Zugewiesene Hilfestellen**.

- **Zuweisen:** Eine Einrichtung im Dropdown wählen und **Zuweisen** auswählen. Danach erscheint sie in der Liste des Partners.
- **Entfernen:** Bei einer bereits zugewiesenen Einrichtung **Entfernen** wählen und die Sicherheitsabfrage bestätigen. Der Partner verliert dadurch die Berechtigung für diese Einrichtung; der Datensatz selbst wird **nicht gelöscht**.
- **Deaktivierte Partner:** Die vorhandenen Zuordnungen bleiben gespeichert, die Formulare für neue Zuweisungen oder Entfernungen sind jedoch ausgeblendet. Zunächst ist eine Reaktivierung erforderlich.

## 4. Account deaktivieren

Unter dem aktiven Partner **Account deaktivieren** auswählen und bestätigen. Danach kann sich der Partner nicht mehr anmelden; bereits bestehende Sitzungen werden beendet. Die zugeordneten Hilfestellen bleiben erhalten.

## 5. Account reaktivieren

Bei einem deaktivierten Partner **Account reaktivieren** auswählen. Das System aktiviert den Account, generiert **ein neues Startpasswort** und zeigt es einmalig an. Das bisherige Passwort ist ungültig. Nach manueller Übergabe muss der Partner erneut ein eigenes Passwort festlegen.

## 6. Vergessenes Passwort zurücksetzen

Bei einem **aktiven** Partner **Passwort zurücksetzen** auswählen und bestätigen. YANA erzeugt ein neues Startpasswort, beendet bestehende Sitzungen und erzwingt beim nächsten Login wieder die Passwortänderung. Bei einem deaktivierten Account zuerst **reaktivieren** (dabei wird bereits automatisch ein neues Startpasswort erzeugt).

Es gibt **keine automatische E-Mail**, keine Funktion „Passwort vergessen“ zur Selbstbedienung und keine Möglichkeit, ein altes Passwort einzusehen.

## 7. Hinweise für die Schulprojekt-Nutzung

- Nur fiktive Testpartner und Testeinrichtungen verwenden; keine echten, vertraulichen Standorte in die öffentliche Hilfestellen-API stellen.
- Startpasswörter nur an berechtigte Empfänger weitergeben. Bei Verlust kann der Admin ein **neues** Startpasswort erstellen.
- Account erstellen, deaktivieren, reaktivieren und zurücksetzen darf nur ein Administrator. Partner können ausschließlich ihr eigenes Passwort ändern.
- Die Funktionen sind technisch getestet, ersetzen aber keine unabhängige Sicherheits- und Datenschutzprüfung für den Realbetrieb.

Für Hintergrund und verwendete Dateien siehe [technische Benutzerverwaltung](../technik/teamportal-benutzerverwaltung.md) und [Portal-Login](../technik/teamportal-login.md).

## Designstand 24.11.2026

Die Partnerverwaltung wird inzwischen im einheitlichen [weiß-lila YANA-Design](../technik/designsystem.md) als kompakte Liste/Tabelle mit Suche, Statusfilter und aufklappbaren Detailaktionen dargestellt. Account-Erstellung, Zuordnung, Sperren/Reaktivieren und Passwort-Reset bleiben serverseitig und mit CSRF abgesichert. Die optische Änderung führt **keine** neuen Rollenrechte ein.
