"""
Rendu de la carte diplomatique via Leaflet.js.
Génère un HTML autonome injecté dans Streamlit via st.components.v1.html.
Leaflet CSS + JS sont téléchargés une fois et inlinés — contourne le blocage
CDN des iframes Streamlit (origine nulle du srcdoc empêche le chargement
de scripts externes).
"""
import json
import math

import requests
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# ---------------------------------------------------------------------------
# Coordonnées géographiques (latitude, longitude) par code ISO alpha-3.
# ---------------------------------------------------------------------------
_COUNTRY_COORDS: dict[str, tuple[float, float]] = {
    "AFG": (33.93, 67.71),   "ALB": (41.15, 20.17),   "DZA": (28.03, 1.66),
    "AGO": (-11.20, 17.87),  "ARG": (-38.42, -63.62), "ARM": (40.07, 45.04),
    "AUS": (-25.27, 133.78), "AUT": (47.52, 14.55),   "AZE": (40.14, 47.58),
    "BGD": (23.68, 90.36),   "BLR": (53.71, 27.95),   "BEL": (50.50, 4.47),
    "BEN": (9.31, 2.32),     "BTN": (27.51, 90.43),   "BOL": (-16.29, -63.59),
    "BIH": (43.92, 17.68),   "BWA": (-22.33, 24.68),  "BRA": (-14.24, -51.93),
    "BRN": (4.54, 114.73),   "BGR": (42.73, 25.49),   "BFA": (12.36, -1.56),
    "BDI": (-3.37, 29.92),   "KHM": (12.57, 104.99),  "CMR": (7.37, 12.35),
    "CAN": (56.13, -106.35), "CAF": (6.61, 20.94),    "TCD": (15.45, 18.73),
    "CHL": (-35.68, -71.54), "CHN": (35.86, 104.20),  "COL": (4.57, -74.30),
    "COD": (-4.04, 21.76),   "COG": (-0.23, 15.83),   "CRI": (9.75, -83.75),
    "CIV": (7.54, -5.55),    "HRV": (45.10, 15.20),   "CUB": (21.52, -77.78),
    "CYP": (35.13, 33.43),   "CZE": (49.82, 15.47),   "DNK": (56.26, 9.50),
    "DJI": (11.83, 42.59),   "DOM": (18.74, -70.16),  "ECU": (-1.83, -78.18),
    "EGY": (26.82, 30.80),   "SLV": (13.79, -88.90),  "GNQ": (1.65, 10.27),
    "ERI": (15.18, 39.78),   "EST": (58.60, 25.01),   "ETH": (9.15, 40.49),
    "FJI": (-16.58, 179.41), "FIN": (61.92, 25.75),   "FRA": (46.23, 2.21),
    "GAB": (-0.80, 11.61),   "GMB": (13.44, -15.31),  "GEO": (42.32, 43.36),
    "DEU": (51.17, 10.45),   "GHA": (7.95, -1.02),    "GRC": (39.07, 21.82),
    "GTM": (15.78, -90.23),  "GIN": (9.95, -9.70),    "GNB": (11.80, -15.18),
    "HTI": (18.97, -72.29),  "HND": (15.20, -86.24),  "HUN": (47.16, 19.50),
    "ISL": (64.96, -19.02),  "IND": (20.59, 78.96),   "IDN": (-0.79, 113.92),
    "IRN": (32.43, 53.69),   "IRQ": (33.22, 43.68),   "IRL": (53.41, -8.24),
    "ISR": (31.05, 34.85),   "ITA": (41.87, 12.57),   "JAM": (18.11, -77.30),
    "JPN": (36.20, 138.25),  "JOR": (30.59, 36.24),   "KAZ": (48.02, 66.92),
    "KEN": (-0.02, 37.91),   "PRK": (40.34, 127.51),  "KOR": (35.91, 127.77),
    "KWT": (29.31, 47.48),   "KGZ": (41.20, 74.77),   "LAO": (19.86, 102.50),
    "LVA": (56.88, 24.60),   "LBN": (33.85, 35.86),   "LBY": (26.34, 17.23),
    "LTU": (55.17, 23.88),   "LUX": (49.82, 6.13),    "MDG": (-18.77, 46.87),
    "MWI": (-13.25, 34.30),  "MYS": (4.21, 108.10),   "MLI": (17.57, -3.00),
    "MLT": (35.94, 14.38),   "MRT": (21.01, -10.94),  "MEX": (23.63, -102.55),
    "MDA": (47.41, 28.37),   "MNG": (46.86, 103.85),  "MNE": (42.71, 19.37),
    "MAR": (31.79, -7.09),   "MOZ": (-18.67, 35.53),  "MMR": (21.91, 95.96),
    "NAM": (-22.96, 18.49),  "NPL": (28.39, 84.12),   "NLD": (52.13, 5.29),
    "NZL": (-40.90, 174.89), "NIC": (12.87, -85.21),  "NER": (17.61, 8.08),
    "NGA": (9.08, 8.68),     "MKD": (41.61, 21.75),   "NOR": (60.47, 8.47),
    "OMN": (21.51, 55.92),   "PAK": (30.38, 69.35),   "PAN": (8.54, -80.78),
    "PNG": (-6.31, 143.96),  "PRY": (-23.44, -58.44), "PER": (-9.19, -75.02),
    "PHL": (12.88, 121.77),  "POL": (51.92, 19.15),   "PRT": (39.40, -8.22),
    "QAT": (25.35, 51.18),   "ROU": (45.94, 24.97),   "RUS": (61.52, 105.32),
    "RWA": (-1.94, 29.87),   "SAU": (23.89, 45.08),   "SEN": (14.50, -14.45),
    "SRB": (44.02, 21.01),   "SLE": (8.46, -11.78),   "SGP": (1.35, 103.82),
    "SVK": (48.67, 19.70),   "SVN": (46.15, 14.99),   "SOM": (5.15, 46.20),
    "ZAF": (-30.56, 22.94),  "SSD": (6.88, 31.31),    "ESP": (40.46, -3.75),
    "LKA": (7.87, 80.77),    "SDN": (12.86, 30.22),   "SWE": (60.13, 18.64),
    "CHE": (46.82, 8.23),    "SYR": (34.80, 38.00),   "TWN": (23.70, 120.96),
    "TJK": (38.86, 71.28),   "TZA": (-6.37, 34.89),   "THA": (15.87, 100.99),
    "TLS": (-8.87, 125.73),  "TGO": (8.62, 0.82),     "TTO": (10.69, -61.22),
    "TUN": (33.89, 9.54),    "TUR": (38.96, 35.24),   "TKM": (38.97, 59.56),
    "UGA": (1.37, 32.29),    "UKR": (48.38, 31.17),   "ARE": (23.42, 53.85),
    "GBR": (55.38, -3.44),   "USA": (37.09, -95.71),  "URY": (-32.52, -55.77),
    "UZB": (41.38, 64.59),   "VEN": (6.42, -66.59),   "VNM": (14.06, 108.28),
    "YEM": (15.55, 48.52),   "ZMB": (-13.13, 27.85),  "ZWE": (-19.02, 29.15),
    "PSE": (31.95, 35.23),   "XKX": (42.60, 20.90),   "GUY": (4.86, -58.93),
    "SUR": (3.92, -56.03),   "BHS": (25.03, -77.40),  "BHR": (26.07, 50.56),
    "COM": (-11.88, 43.87),  "CPV": (16.00, -24.01),  "MDV": (3.20, 73.22),
    "MUS": (-20.35, 57.55),  "SWZ": (-26.52, 31.47),
    "LSO": (-29.61, 28.23),  "LBR": (6.43, -9.43),
}

# ---------------------------------------------------------------------------
# Couleurs par code continent (pycountry_convert)
# ---------------------------------------------------------------------------
_CONTINENT_COLORS: dict[str, str] = {
    "AF": "#E67E22",  # Afrique
    "EU": "#3498DB",  # Europe
    "AS": "#E74C3C",  # Asie
    "NA": "#2ECC71",  # Amériques du Nord
    "SA": "#2ECC71",  # Amériques du Sud
    "OC": "#9B59B6",  # Océanie
}

try:
    import pycountry as _pycountry
    import pycountry_convert as _pc_convert

    def _country_name(code: str) -> str:
        """Retourne le nom complet d'un pays depuis son code ISO alpha-3."""
        c = _pycountry.countries.get(alpha_3=code)
        return c.name if c else code

    def _continent_color(code: str) -> str:
        """Retourne la couleur hex du marqueur selon le continent du pays."""
        try:
            c = _pycountry.countries.get(alpha_3=code)
            if c is None:
                return "#95A5A6"
            continent = _pc_convert.country_alpha2_to_continent_code(c.alpha_2)
            return _CONTINENT_COLORS.get(continent, "#95A5A6")
        except (KeyError, LookupError):
            return "#95A5A6"

except ImportError:
    def _country_name(code: str) -> str:
        """Retourne le code tel quel si pycountry est indisponible."""
        return code

    def _continent_color(code: str) -> str:
        """Retourne le gris fallback si pycountry_convert est indisponible."""
        return "#95A5A6"


def _tone_to_color(tone: float) -> str:
    """Interpole rouge → jaune → vert selon AvgTone (plage -5 à +5)."""
    t = max(-5.0, min(5.0, float(tone)))
    ratio = (t + 5.0) / 10.0  # 0 = rouge, 1 = vert
    r = int(231 * (1 - ratio) + 39 * ratio)
    g = int(76 * (1 - ratio) + 174 * ratio)
    b = int(60 * (1 - ratio) + 96 * ratio)
    return f"#{r:02x}{g:02x}{b:02x}"


def _polyline_weight(nb: int, max_nb: int) -> float:
    """Normalise l'épaisseur de polyline (1–8 px) par log sur nb_interactions."""
    if max_nb <= 1:
        return 1.0
    return 1.0 + 7.0 * math.log1p(nb) / math.log1p(max_nb)


@st.cache_resource
def _get_leaflet_bundle() -> tuple[str, str]:
    """Télécharge et met en cache Leaflet CSS + JS depuis unpkg.

    Returns:
        Tuple (leaflet_css, leaflet_js) en tant que strings.

    Raises:
        requests.RequestException: si le téléchargement échoue.
    """
    base = "https://unpkg.com/leaflet@1.9.4/dist/leaflet"
    css_resp = requests.get(f"{base}.css", timeout=15)
    css_resp.raise_for_status()
    js_resp = requests.get(f"{base}.js", timeout=15)
    js_resp.raise_for_status()
    return css_resp.text, js_resp.text


def _build_map_data(
    relations: pd.DataFrame,
    degree: dict[str, int],
) -> tuple[list[dict], list[dict]]:
    """Construit les listes JSON de nœuds et d'arêtes pour le template Leaflet.

    Args:
        relations: DataFrame filtré avec colonnes Actor1/2CountryCode,
                   nb_interactions, avg_tone, avg_goldstein.
        degree: mapping code ISO alpha-3 → nombre d'arêtes connectées.

    Returns:
        Tuple (nodes, edges) de listes de dicts sérialisables en JSON.
    """
    countries = set(relations["Actor1CountryCode"]) | set(relations["Actor2CountryCode"])
    country_names = {code: _country_name(code) for code in countries}
    max_nb = int(relations["nb_interactions"].max())

    nodes: list[dict] = []
    for code in countries:
        coords = _COUNTRY_COORDS.get(code)
        if coords is None:
            continue
        lat, lon = coords
        nodes.append({
            "code": code,
            "name": country_names[code],
            "lat": lat,
            "lon": lon,
            "color": _continent_color(code),
            "radius": 5 + min(degree.get(code, 1), 15),
            "connections": degree.get(code, 0),
        })

    edge_weights = relations["nb_interactions"].map(
        lambda n: _polyline_weight(int(n), max_nb)
    ).tolist()
    edges: list[dict] = []
    for a1, a2, nb, tone, ew in zip(
        relations["Actor1CountryCode"],
        relations["Actor2CountryCode"],
        relations["nb_interactions"].astype(int),
        relations["avg_tone"],
        edge_weights,
    ):
        if _COUNTRY_COORDS.get(a1) is None or _COUNTRY_COORDS.get(a2) is None:
            continue
        edges.append({
            "a1": a1,
            "a2": a2,
            "name1": country_names.get(a1, a1),
            "name2": country_names.get(a2, a2),
            "nb": int(nb),
            "tone": round(float(tone), 2),
            "color": _tone_to_color(float(tone)),
            "weight": round(ew, 2),
        })

    return nodes, edges


# Template JS Leaflet — __NODES__ et __EDGES__ sont remplacés par json.dumps()
# avant injection. Pas de f-string : les accolades JS ne sont pas échappées.
_LEAFLET_JS_TEMPLATE = """\
var NODES = __NODES__;
var EDGES = __EDGES__;

var map = L.map('map');
L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> \
contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    subdomains: 'abcd',
    maxZoom: 19
}).addTo(map);

var markerMap = {};
var polylineList = [];
var originalPositions = {};

function createMarkerIcon(color, radius) {
    var size = radius * 2;
    return L.divIcon({
        className: '',
        html: '<div style="width:' + size + 'px;height:' + size + 'px;' +
              'background:' + color + ';border-radius:50%;' +
              'border:1.5px solid rgba(255,255,255,0.7);' +
              'box-shadow:0 0 6px rgba(0,0,0,0.5);cursor:grab;"></div>',
        iconSize: [size, size],
        iconAnchor: [radius, radius],
        tooltipAnchor: [radius + 2, -radius]
    });
}

function updatePolylines(code) {
    polylineList.forEach(function(p) {
        if (p.a1 === code || p.a2 === code) {
            var ll1 = markerMap[p.a1].getLatLng();
            var ll2 = markerMap[p.a2].getLatLng();
            p.polyline.setLatLngs([[ll1.lat, ll1.lng], [ll2.lat, ll2.lng]]);
        }
    });
}

NODES.forEach(function(n) {
    originalPositions[n.code] = [n.lat, n.lon];
    var marker = L.marker([n.lat, n.lon], {
        icon: createMarkerIcon(n.color, n.radius),
        draggable: true
    });
    marker.bindTooltip(
        '<b>' + n.name + '</b><br>Connexions : ' + n.connections,
        {sticky: true, direction: 'top', offset: [0, -n.radius - 4]}
    );
    markerMap[n.code] = marker;
    marker.addTo(map);
    marker.on('drag', (function(code) {
        return function() { updatePolylines(code); };
    })(n.code));
});

EDGES.forEach(function(e) {
    var m1 = markerMap[e.a1];
    var m2 = markerMap[e.a2];
    if (!m1 || !m2) return;
    var ll1 = m1.getLatLng();
    var ll2 = m2.getLatLng();
    var polyline = L.polyline([[ll1.lat, ll1.lng], [ll2.lat, ll2.lng]], {
        color: e.color,
        weight: e.weight,
        opacity: 0.6
    });
    polyline.bindTooltip(
        '<b>' + e.name1 + ' ⇔ ' + e.name2 + '</b>' +
        '<br>Interactions : ' + e.nb +
        '<br>AvgTone : ' + e.tone.toFixed(2),
        {sticky: true}
    );
    polylineList.push({polyline: polyline, a1: e.a1, a2: e.a2});
    polyline.addTo(map);
});

var allLatLngs = NODES.map(function(n) { return [n.lat, n.lon]; });
if (allLatLngs.length > 0) {
    map.fitBounds(L.latLngBounds(allLatLngs), {padding: [30, 30]});
}

document.getElementById('reset-btn').addEventListener('click', function() {
    Object.keys(markerMap).forEach(function(code) {
        markerMap[code].setLatLng(originalPositions[code]);
        updatePolylines(code);
    });
    if (allLatLngs.length > 0) {
        map.fitBounds(L.latLngBounds(allLatLngs), {padding: [30, 30]});
    }
});

setTimeout(function() { map.invalidateSize(); }, 200);
"""


def _build_leaflet_html(
    nodes: list[dict],
    edges: list[dict],
    leaflet_css: str,
    leaflet_js: str,
    height: int,
) -> str:
    """Génère le HTML autonome avec carte Leaflet embarquée.

    Args:
        nodes: liste de dicts nœuds produite par _build_map_data.
        edges: liste de dicts arêtes produite par _build_map_data.
        leaflet_css: contenu du fichier leaflet.css (inliné).
        leaflet_js: contenu du fichier leaflet.js (inliné).
        height: hauteur du div carte en pixels.

    Returns:
        String HTML complète prête pour st.components.v1.html.
    """
    nodes_json = json.dumps(nodes, ensure_ascii=False)
    edges_json = json.dumps(edges, ensure_ascii=False)

    js_code = (
        _LEAFLET_JS_TEMPLATE
        .replace("__NODES__", nodes_json)
        .replace("__EDGES__", edges_json)
    )

    css_overrides = (
        "* { margin:0; padding:0; box-sizing:border-box; }"
        "body { background:#0E1117; overflow:hidden; }"
        "#map { width:100%; height:" + str(height) + "px; }"
        "#reset-btn {"
        " position:absolute; top:60px; right:10px; z-index:1000;"
        " background:#161B22; color:#FAFAFA; border:1px solid #3498DB;"
        " padding:6px 14px; cursor:pointer; border-radius:4px;"
        " font-size:13px; font-family:sans-serif;"
        "}"
        "#reset-btn:hover { background:#3498DB; }"
    )

    return (
        "<!DOCTYPE html>"
        "<html><head><meta charset='utf-8'/>"
        "<style>" + css_overrides + leaflet_css + "</style>"
        "</head><body>"
        "<button id='reset-btn'>Reset</button>"
        "<div id='map'></div>"
        "<script>" + leaflet_js + "</script>"
        "<script>" + js_code + "</script>"
        "</body></html>"
    )


def render(relations: pd.DataFrame, height: int = 900) -> None:
    """
    Construit et affiche la carte Leaflet à partir des relations filtrées.

    Args:
        relations: DataFrame avec colonnes Actor1CountryCode, Actor2CountryCode,
                   nb_interactions, avg_tone, avg_goldstein.
        height: Hauteur du canvas en pixels.
    """
    if relations.empty:
        st.warning("Aucune relation à afficher avec les filtres actuels.")
        return

    try:
        leaflet_css, leaflet_js = _get_leaflet_bundle()
    except requests.RequestException as exc:
        st.error(f"Impossible de charger Leaflet.js ({exc}). Vérifiez votre connexion.")
        return

    degree: dict = (
        pd.concat([relations["Actor1CountryCode"], relations["Actor2CountryCode"]])
        .value_counts()
        .to_dict()
    )

    nodes, edges = _build_map_data(relations, degree)

    if not nodes:
        st.warning("Aucun pays avec coordonnées GPS disponibles pour les filtres actuels.")
        return

    html = _build_leaflet_html(nodes, edges, leaflet_css, leaflet_js, height)
    components.html(html, height=height + 10, scrolling=False)
