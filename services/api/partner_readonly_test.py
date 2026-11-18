"""Lesende Sicherheitstests mit simuliertem Partner; keine Schreibtests."""
from html.parser import HTMLParser
from unittest.mock import patch

from fastapi.testclient import TestClient
from main import app
from database import get_connection


class TokenParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.token = None

    def handle_starttag(self, tag, attrs):
        if tag == 'input':
            d = dict(attrs)
            if d.get('name') == 'csrf_token':
                self.token = d.get('value')


fake_partner_id = -2147483647
fake_partner = {
    'account_id': fake_partner_id,
    'email': 'unreal-partner@example.invalid',
    'role': 'partner',
}

with get_connection() as conn:
    with conn.cursor() as cur:
        cur.execute('SELECT COUNT(*) FROM public.portal_account WHERE account_id = %s', (fake_partner_id,))
        assert cur.fetchone()[0] == 0, 'Test-ID ist bereits vergeben'
        cur.execute('SELECT COUNT(*) FROM public.portal_facility_assignment WHERE account_id = %s', (fake_partner_id,))
        assert cur.fetchone()[0] == 0, 'Test-Account hat Zuweisungen'

with TestClient(app, base_url='https://testserver', follow_redirects=False) as client:
    # Login-Seite erzeugt das CSRF-Token, ohne dass sich jemand anmelden muss.
    login = client.get('/portal/login')
    assert login.status_code == 200
    parser = TokenParser()
    parser.feed(login.text)
    assert parser.token, 'Kein CSRF-Token gefunden'

    # Fake-Account wird ausschließlich in diesem Python-Prozess simuliert.
    with (
        patch('portal_facilities.session_account', return_value=fake_partner),
        patch('portal_facilities_create.session_account', return_value=fake_partner),
        patch('portal_access.session_account', return_value=fake_partner),
        patch('portal_facilities_status.require_account', return_value=fake_partner),
    ):
        def expect(method, path, code, data=None):
            response = client.request(method, path, data=data)
            print(method, path, response.status_code)
            assert response.status_code == code, response.text[:400]

        expect('GET', '/portal/hilfestellen', 200)
        expect('GET', '/portal/hilfestellen/1/edit', 404)
        expect('GET', '/portal/hilfestellen/neu', 403)
        expect('POST', '/portal/hilfestellen/1/status/approve', 403,
               {'csrf_token': parser.token})
        expect('POST', '/portal/hilfestellen/1/status/submit', 404,
               {'csrf_token': parser.token})
        expect('POST', '/portal/hilfestellen/1/edit', 404, {
            'csrf_token': parser.token,
            'name': 'Unzulaessiger Test',
            'phone': '', 'email': '', 'opening_hours': ''
        })
        expect('POST', '/portal/hilfestellen/neu', 403, {
            'csrf_token': parser.token,
            'name': 'YANA Test Nicht Speichern',
            'facility_type': 'Beratungsstelle',
            'address': 'Keine', 'latitude': '0', 'longitude': '0',
            'capacity': '0',
        })

print('Alle sieben simulierten Partner-Sicherheitspruefungen bestanden.')
print('Es wurden keine neuen Accounts oder Hilfestellen angelegt.')
