/* YANA: Externe Geocodierung nur nach ausdrücklichem Klick des Administrators. */
(() => {
    "use strict";
    const form = document.getElementById("new-facility-form");
    if (!form) return;

    const button = document.getElementById("geocode-button");
    const tokenInput = document.getElementById("geocode_token");
    const feedback = document.getElementById("geocode-feedback");
    const result = document.getElementById("geocode-result");
    const formatted = document.getElementById("geocode-formatted");
    const coordinates = document.getElementById("geocode-coordinates");
    const mapLink = document.getElementById("geocode-map-link");
    const relatedFields = ["facility_type", "street", "housenumber", "postcode", "city", "non_confidential"];

    function resetConfirmation() {
        tokenInput.value = "";
        result.hidden = true;
        feedback.textContent = "Standort nicht bestätigt. Du kannst die Hilfestelle auch ohne Koordinaten als Entwurf speichern.";
        feedback.dataset.state = "neutral";
    }

    for (const id of relatedFields) {
        const element = document.getElementById(id);
        element.addEventListener("input", resetConfirmation);
        element.addEventListener("change", resetConfirmation);
    }

    button.addEventListener("click", async () => {
        resetConfirmation();
        const required = ["facility_type", "street", "housenumber", "postcode", "city"];
        for (const field of required) {
            const input = document.getElementById(field);
            if (!input.reportValidity() || !input.value.trim()) {
                input.focus();
                return;
            }
        }
        if (!document.getElementById("non_confidential").checked) {
            feedback.dataset.state = "error";
            feedback.textContent = "Bitte zuerst bestätigen, dass es sich um eine öffentliche, nicht vertrauliche Adresse handelt.";
            return;
        }

        const data = new FormData(form);
        button.disabled = true;
        feedback.dataset.state = "neutral";
        feedback.textContent = "Adresse wird geprüft …";
        try {
            const response = await fetch("/portal/hilfestellen/neu/standort-pruefen", {
                method: "POST", credentials: "same-origin", body: data, cache: "no-store",
                headers: { "Accept": "application/json" }
            });
            const payload = await response.json();
            if (!response.ok) {
                throw new Error(typeof payload.detail === "string" ? payload.detail : "Adressprüfung fehlgeschlagen.");
            }
            tokenInput.value = payload.confirmation_token;
            formatted.textContent = payload.formatted;
            coordinates.textContent = `Breitengrad: ${payload.latitude} · Längengrad: ${payload.longitude}`;
            const lat = Number(payload.latitude);
            const lon = Number(payload.longitude);
            const osm = new URL("https://www.openstreetmap.org/");
            osm.searchParams.set("mlat", String(lat));
            osm.searchParams.set("mlon", String(lon));
            osm.hash = `map=17/${lat}/${lon}`;
            mapLink.href = osm.toString();
            result.hidden = false;
            feedback.dataset.state = "success";
            feedback.textContent = "Standort ermittelt. Bitte den Treffer prüfen und anschließend speichern.";
        } catch (error) {
            feedback.dataset.state = "error";
            feedback.textContent = error instanceof Error ? error.message : "Standortprüfung derzeit nicht möglich.";
        } finally {
            button.disabled = false;
        }
    });
})();
