# Standortfreigaben im YANA-Teamportal bedienen

**Stand: 24. November 2026 · Administratorfunktion produktiv geprüft**

## Zugang und Übersicht

1. Über die öffentliche YANA-Seite im **Teamportal** anmelden.
2. Im Administrator-Dashboard die Kachel **Standortfreigaben** wählen; alternativ die geschützte Route `/portal/standorte` öffnen.
3. In der **kompakten Tabelle** eine Hilfestelle suchen oder nach Freigabestatus filtern.
4. Bei der betreffenden Einrichtung **Details** aufklappen. Dort stehen die intern hinterlegte Adresse, Koordinaten und die passende Aktion.

Nur Administratoren dürfen Standorte freigeben oder sperren. Partner dürfen die Seite nicht nutzen.

## Standort öffentlich freigeben

Eine Freigabe ist nur möglich, wenn die Hilfestelle **veröffentlicht** ist, der Einrichtungstyp auf der Positivliste steht und der Standort inhaltlich geprüft wurde. Im Projektstand ist ausschließlich **`Beratungsstelle`** als potenziell freigabefähig hinterlegt.

1. Prüfen, dass Name, Einrichtungstyp und Anschrift korrekt sind und tatsächlich **öffentlich genannt werden dürfen**.
2. Unter **Details** auf **Standort freigeben** klicken und die Rückfrage bestätigen.
3. Danach in der öffentlichen API kontrollieren, dass Adresse und Koordinaten nur bei ausdrücklich zulässigen Einträgen sichtbar sind.

Die Einrichtungsart allein ist **keine Freigabe**. Eine Schutzunterkunft darf selbst bei einer Veröffentlichung **keinen vertraulichen Standort** preisgeben.

## Freigabe zurücknehmen

Über **Details → Freigabe zurücknehmen** setzt der Administrator `is_location_public` auf `FALSE`. Danach liefert `GET /hilfestellen` für `address`, `latitude` und `longitude` wieder `null`.

Auch wenn Adresse, Koordinaten oder Einrichtungsart nachträglich geändert werden, setzt ein PostgreSQL-Trigger die frühere Standortfreigabe automatisch zurück.

## Neue Hilfestelle mit Adresse anlegen

Die neue Eingabemaske für Straße, Hausnummer, PLZ und Ort wurde am **24.11.2026 in der Testumgebung erfolgreich geprüft**. Das anschließende produktive Deployment der Geoapify-Erweiterung ist zu diesem Dokumentationsstand **noch nicht bestätigt**. Daher ist die neue Eingabemaske hier bewusst **noch nicht als produktiv verfügbar** beschrieben.

Geplanter Ablauf nach dem Deployment: Adresse eingeben → für nicht vertrauliche Einrichtung ausdrücklich der externen Prüfung zustimmen → **Standort ermitteln** → Treffer überprüfen → Entwurf speichern. Die Koordinaten werden intern übernommen und bleiben bis zur separaten Freigabe vertraulich. Ohne erfolgreiche Ermittlung kann ein Entwurf ohne Koordinaten gespeichert werden.

Mehr zum [Standort-Datenschutz](../technik/standort-datenschutz.md), [Geocoding](../technik/geocoding.md) und [Wiedereinstieg](../technik/weiterarbeit.md).
