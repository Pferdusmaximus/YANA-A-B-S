from getpass import getpass
from html.parser import HTMLParser

from dotenv import load_dotenv
from fastapi.testclient import TestClient
from psycopg.rows import dict_row

load_dotenv('.env')
from database import get_connection
from main import app

PARTNER_EMAIL = 'yana-partner-test@example.invalid'

class TokenParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.token = None

    def handle_starttag(self, tag, attrs):
        if tag == 'input':
            attributes = dict(attrs)
            if attributes.get('name') == 'csrf_token':
                self.token = attributes.get('value')

def token_from(html):
    parser = TokenParser()
    parser.feed(html)
    if not parser.token:
        raise RuntimeError('CSRF-Token fehlt')
    return parser.token

def page_token(client, url):
    response = client.get(url)
    assert response.status_code == 200, f'GET {url}: {response.status_code}, {response.text[:200]}'
    return token_from(response.text)

def login(client, email, password):
    csrf = page_token(client, '/portal/login')
    response = client.post('/portal/login', data={
        'email': email, 'password': password, 'csrf_token': csrf
    })
    assert response.status_code == 303, f'Login fehlgeschlagen: HTTP {response.status_code}'

def query_one(sql, params=()):
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(sql, params)
            return cur.fetchone()

def facility_row(facility_id):
    return query_one('''
        SELECT facility_id, name, phone, email, opening_hours, publication_status
        FROM public.hilfestelle WHERE facility_id = %s
    ''', (facility_id,))

def public_row(client, facility_id):
    response = client.get('/hilfestellen')
    assert response.status_code == 200
    return next((row for row in response.json()
                 if row['facility_id'] == facility_id), None)

def active_proposal(facility_id):
    return query_one('''
        SELECT change_id, status, proposed_data
        FROM public.portal_facility_change
        WHERE facility_id = %s AND status IN ('draft', 'pending_review')
    ''', (facility_id,))

def send_proposal(client, facility_id, original, phone, mode):
    path = f'/portal/hilfestellen/{facility_id}/aenderung'
    csrf = page_token(client, path)
    response = client.post(path, data={
        'csrf_token': csrf, 'mode': mode,
        'name': original['name'], 'phone': phone or '',
        'email': original['email'] or '',
        'opening_hours': original['opening_hours'] or ''
    })
    assert response.status_code == 303, f'POST {mode}: HTTP {response.status_code}: {response.text[:300]}'

def approve(client, change_id):
    csrf = page_token(client, '/portal/aenderungen')
    response = client.post(f'/portal/aenderungen/{change_id}/approve',
                           data={'csrf_token': csrf})
    assert response.status_code == 303, f'Freigabe HTTP {response.status_code}: {response.text[:300]}'

admin_email = input('Admin-E-Mail: ').strip().lower()
admin_password = getpass('Admin-Passwort: ')
partner_password = getpass('Testpartner-Passwort: ')

with get_connection() as conn:
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute('''
            SELECT h.facility_id, h.name, h.phone, h.email, h.opening_hours
            FROM public.portal_facility_assignment pfa
            JOIN public.portal_account a ON a.account_id = pfa.account_id
            JOIN public.hilfestelle h ON h.facility_id = pfa.facility_id
            WHERE a.email = %s AND a.role = 'partner'
              AND h.publication_status = 'published'
              AND h.name LIKE 'YANA Test%%'
        ''', (PARTNER_EMAIL,))
        matches = cur.fetchall()

assert len(matches) == 1, (
    f'Genau eine veröffentlichte, zugewiesene YANA-Test-Hilfestelle erwartet; gefunden: {len(matches)}'
)
original = matches[0]
facility_id = original['facility_id']
assert active_proposal(facility_id) is None, 'Für die Hilfestelle existiert bereits ein aktiver Änderungsantrag.'
new_phone = '000001' if original['phone'] != '000001' else '000002'
print(f'Prüfung: Testeintrag-ID {facility_id}; ursprüngliche Nummer: {original["phone"]!r}')
print('Neue Testnummer:', new_phone)

try:
    with TestClient(app, base_url='https://testserver', follow_redirects=False) as partner, \
         TestClient(app, base_url='https://testserver', follow_redirects=False) as admin:
        login(partner, PARTNER_EMAIL, partner_password)
        login(admin, admin_email, admin_password)
        assert partner.get('/portal/aenderungen').status_code == 403
        assert public_row(partner, facility_id)['phone'] == original['phone']
        print('1. Partner-/Admin-Anmeldung und Rechte: OK')

        send_proposal(partner, facility_id, original, new_phone, 'save')
        draft = active_proposal(facility_id)
        assert draft and draft['status'] == 'draft'
        assert facility_row(facility_id)['phone'] == original['phone']
        assert public_row(partner, facility_id)['phone'] == original['phone']
        print('2. Entwurf gespeichert; öffentliche Daten unverändert: OK')

        send_proposal(partner, facility_id, original, new_phone, 'submit')
        pending = active_proposal(facility_id)
        assert pending and pending['status'] == 'pending_review'
        assert public_row(partner, facility_id)['phone'] == original['phone']
        print('3. Zur Prüfung eingereicht; öffentliche Daten unverändert: OK')

        approve(admin, pending['change_id'])
        assert active_proposal(facility_id) is None
        assert facility_row(facility_id)['phone'] == new_phone
        assert public_row(partner, facility_id)['phone'] == new_phone
        print('4. Admin-Freigabe; öffentliche Daten aktualisiert: OK')

        send_proposal(partner, facility_id, original, original['phone'], 'submit')
        reversal = active_proposal(facility_id)
        assert reversal and reversal['status'] == 'pending_review'
        approve(admin, reversal['change_id'])
        assert facility_row(facility_id)['phone'] == original['phone']
        assert public_row(partner, facility_id)['phone'] == original['phone']
        assert active_proposal(facility_id) is None
        print('5. Ursprüngliche Telefonnummer über Freigabe wiederhergestellt: OK')

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute('''
                    SELECT event_type FROM public.portal_facility_audit
                    WHERE facility_id = %s
                      AND event_type IN ('change_submitted', 'change_approved')
                    ORDER BY audit_id DESC LIMIT 4
                ''', (facility_id,))
                recent_events = [row[0] for row in cur.fetchall()]
        assert recent_events == [
            'change_approved', 'change_submitted',
            'change_approved', 'change_submitted'
        ], f'Unerwartete Audit-Einträge: {recent_events}'
        print('6. Vier erwartete Audit-Ereignisse: OK')
        print('\nALLE ÄNDERUNGSFREIGABE-TESTS BESTANDEN!')
finally:
    row = facility_row(facility_id)
    print(f'Abschlussstatus Hilfestelle {facility_id}: {row["publication_status"]}; '
          f'aktuelle Telefonnummer: {row["phone"]!r}')
    if row['phone'] != original['phone']:
        print('ACHTUNG: Ursprüngliche Telefonnummer noch nicht wiederhergestellt.')
