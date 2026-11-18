"""Nur lesende/ungeprüfte Anfragen; speichert keine Daten.
Auf VPS in ~/yana-portal-test ausführen.
"""
from fastapi.testclient import TestClient
from main import app
from database import get_connection

with get_connection() as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM public.portal_facility_change")
        print('Anträge in Datenbank:', cur.fetchone()[0])

with TestClient(app, base_url='https://testserver', follow_redirects=False) as client:
    tests = [
        ('GET', '/portal/aenderungen', None, 401),
        ('GET', '/portal/hilfestellen/1/aenderung', None, 401),
        ('POST', '/portal/aenderungen/123/approve', {'csrf_token': 'FAKE'}, 401),
        ('POST', '/portal/aenderungen/123/reject', {'csrf_token': 'FAKE'}, 401),
        ('POST', '/portal/hilfestellen/1/aenderung', {
            'csrf_token': 'FAKE', 'mode': 'submit', 'name': 'YANA Test X',
            'phone': '', 'email': '', 'opening_hours': ''
        }, 401),
        ('GET', '/hilfestellen', None, 200),
    ]
    for method, path, data, expected in tests:
        r = client.request(method, path, data=data)
        print(method, path, r.status_code)
        assert r.status_code == expected, f'Erwartet {expected}, erhalten {r.status_code}: {r.text[:200]}'

print('Alle sechs schreibfreien Prüfungen bestanden.')
