"""YANA – datensparsame Adressprüfung für öffentlich bekannte Einrichtungen.

Nur serverseitige Geoapify-Anfragen; nie für vertrauliche Schutzadressen nutzen.
Das Ergebnis wird an einen zeitlich begrenzten, signierten Formularbeleg gebunden.
"""

import math
import os
import re
from decimal import Decimal, InvalidOperation

import httpx
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer


GEOAPIFY_URL = "https://api.geoapify.com/v1/geocode/search"
COUNTRY = "Deutschland"
CONFIRMATION_MAX_AGE = 600  # Sekunden


class GeocodingError(Exception):
    """Öffentlich anzeigbarer Fehlertext (keine Schlüssel/URLs enthalten)."""


def normalize_address(street, housenumber, postcode, city):
    street = " ".join(street.strip().split())
    housenumber = " ".join(housenumber.strip().split())
    postcode = postcode.strip()
    city = " ".join(city.strip().split())

    if not 2 <= len(street) <= 100:
        raise ValueError("Straße muss 2 bis 100 Zeichen enthalten.")
    if not 1 <= len(housenumber) <= 12:
        raise ValueError("Hausnummer muss 1 bis 12 Zeichen enthalten.")
    if not re.fullmatch(r"\d{5}", postcode):
        raise ValueError("Bitte eine fünfstellige deutsche Postleitzahl eingeben.")
    if not 2 <= len(city) <= 90:
        raise ValueError("Ort muss 2 bis 90 Zeichen enthalten.")
    if any(any(ord(ch) < 32 for ch in value) for value in (street, housenumber, city)):
        raise ValueError("Ungültige Steuerzeichen in der Adresse.")

    address = f"{street} {housenumber}, {postcode} {city}, {COUNTRY}"
    if len(address) > 255:
        raise ValueError("Die vollständige Anschrift ist zu lang.")
    return {
        "street": street,
        "housenumber": housenumber,
        "postcode": postcode,
        "city": city,
        "address": address,
    }


def _serializer():
    # Eigener Salt: Ein Geocoding-Beleg kann nicht als anderer Session-Token dienen.
    secret = os.getenv("PORTAL_SESSION_SECRET", "")
    if len(secret) < 32:
        raise RuntimeError("PORTAL_SESSION_SECRET fehlt oder ist zu kurz.")
    return URLSafeTimedSerializer(secret, salt="yana-geocoding-v1")


def issue_confirmation(fields, facility_type, account_id, lat, lon):
    data = {
        "fields": {k: fields[k] for k in ("street", "housenumber", "postcode", "city")},
        "facility_type": facility_type.strip(),
        "account_id": int(account_id),
        "lat": str(lat),
        "lon": str(lon),
    }
    return _serializer().dumps(data)


def verify_confirmation(token, fields, facility_type, account_id):
    if not token:
        return None, None
    if len(token) > 5000:
        raise ValueError("Ungültige Standortbestätigung.")
    try:
        data = _serializer().loads(token, max_age=CONFIRMATION_MAX_AGE)
    except (BadSignature, SignatureExpired) as exc:
        raise ValueError("Standortbestätigung abgelaufen oder ungültig. Bitte neu prüfen.") from exc

    expected = {k: fields[k] for k in ("street", "housenumber", "postcode", "city")}
    if (data.get("fields") != expected
            or data.get("facility_type") != facility_type.strip()
            or data.get("account_id") != int(account_id)):
        raise ValueError("Adresse oder Einrichtungsart wurde geändert. Bitte Standort erneut prüfen.")

    try:
        latitude = Decimal(data["lat"])
        longitude = Decimal(data["lon"])
    except (InvalidOperation, KeyError, ValueError, TypeError) as exc:
        raise ValueError("Ungültige Standortbestätigung.") from exc
    if (not latitude.is_finite() or not longitude.is_finite()
            or not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180)):
        raise ValueError("Ungültige Koordinaten in der Standortbestätigung.")
    return latitude, longitude


def geocode_public_address(fields):
    """Eine gezielte Serveranfrage, kein Autocomplete. Nur nach fachlicher Freigabe aufrufen."""
    api_key = os.getenv("GEOAPIFY_API_KEY", "").strip()
    if not api_key:
        raise GeocodingError("Geoapify ist auf dem Server noch nicht konfiguriert.")

    params = {
        "street": fields["street"],
        "housenumber": fields["housenumber"],
        "postcode": fields["postcode"],
        "city": fields["city"],
        "country": COUNTRY,
        "filter": "countrycode:de",
        "lang": "de",
        "limit": 5,
        "format": "json",
        "apiKey": api_key,
    }
    try:
        with httpx.Client(timeout=5.0, follow_redirects=False) as client:
            response = client.get(GEOAPIFY_URL, params=params, headers={"Accept": "application/json"})
        if response.status_code == 429:
            raise GeocodingError("Geoapify-Limit erreicht. Bitte später erneut versuchen.")
        if response.status_code != 200:
            raise GeocodingError("Geoapify konnte die Adresse derzeit nicht prüfen.")
        result = response.json()
    except (httpx.TimeoutException, httpx.RequestError, ValueError) as exc:
        raise GeocodingError("Geocoding-Dienst nicht erreichbar oder Antwort ungültig.") from exc

    # Strenger Hausnummernabgleich verhindert die Übernahme eines bloßen Stadtmittelpunkts.
    if not isinstance(result, dict) or not isinstance(result.get("results"), list):
        raise GeocodingError("Ungültige Antwort des Geocoding-Dienstes.")
    for candidate in result["results"]:
        if not isinstance(candidate, dict):
            continue
        if (str(candidate.get("country_code", "")).lower() != "de"
                or str(candidate.get("postcode", "")).strip() != fields["postcode"]
                or str(candidate.get("housenumber", "")).strip().casefold() != fields["housenumber"].casefold()
                or candidate.get("result_type") not in ("building", "amenity")):
            continue
        confidence = (candidate.get("rank") or {}).get("confidence", 0)
        try:
            confidence = float(confidence)
            lat = float(candidate["lat"])
            lon = float(candidate["lon"])
        except (TypeError, ValueError, KeyError):
            continue
        if (not math.isfinite(confidence) or confidence < 0.75
                or not math.isfinite(lat) or not math.isfinite(lon)
                or not -90 <= lat <= 90 or not -180 <= lon <= 180):
            continue
        return {
            "latitude": Decimal(str(round(lat, 7))),
            "longitude": Decimal(str(round(lon, 7))),
            "formatted": str(candidate.get("formatted") or fields["address"])[:255],
            "confidence": round(confidence, 2),
        }

    raise GeocodingError(
        "Keine ausreichend genaue Hausnummer gefunden. "
        "Bitte die Adresse prüfen; ein Entwurf ist auch ohne Koordinaten möglich."
    )
