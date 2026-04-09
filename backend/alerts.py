"""
email.py
Sends alert emails via SendGrid.

Farmer alert  – general quarantine / disease-spread advisory.
Vet alert     – heat-map link (Google Maps JS API) showing:
                  • red   zone: 0–5 km
                  • orange zone: 5–15 km
                  • blue  zone: 15–25 km
"""

import os
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

load_dotenv()

log = logging.getLogger(__name__)

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
FROM_EMAIL       = os.getenv("ALERT_FROM_EMAIL", "alert@ducktrack.com")
MAPS_API_KEY     = os.getenv("GOOGLE_MAPS_API_KEY", "YOUR_MAPS_KEY")


# ── Internal sender ──────────────────────────────────────────────────────────

def _send(to_email: str, subject: str, html_body: str) -> bool:
    """Send a single email. Returns True on success, False on failure."""
    if not SENDGRID_API_KEY:
        log.warning("SENDGRID_API_KEY not configured – skipping email send.")
        return False
    try:
        message = Mail(
            from_email    = FROM_EMAIL,
            to_emails     = to_email,
            subject       = subject,
            html_content  = html_body,
        )
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        log.info("Email sent to %s | status %s", to_email, response.status_code)
        return response.status_code in (200, 201, 202)
    except Exception as exc:
        log.error("SendGrid error for %s: %s", to_email, exc)
        return False


# ── Farmer alert ─────────────────────────────────────────────────────────────

FARMER_SUBJECT = "🚨 DuckTrack Disease Alert – Immediate Action Required"

FARMER_HTML_TEMPLATE = """\
<html><body style="font-family:Arial,sans-serif;color:#333;">
  <h2 style="color:#c0392b;">⚠️ Duck Disease Alert</h2>
  <p>Dear <strong>{name}</strong>,</p>
  <p>
    A duck disease has been detected near your registered area
    (<strong>PIN: {pin_code}</strong>). This alert is being sent to all farmers
    in the surrounding region.
  </p>

  <h3>What you should do immediately:</h3>
  <ul>
    <li>🔒 <strong>Quarantine</strong> your flock – restrict movement in and out of the farm.</li>
    <li>🩺 Contact your nearest veterinary officer.</li>
    <li>🚫 Do not sell or transport ducks until further notice.</li>
    <li>🧼 Disinfect all equipment and water sources.</li>
    <li>📋 Monitor birds for symptoms: lethargy, reduced appetite, unusual mortality.</li>
  </ul>

  <p>
    Detection location: <strong>Lat {latitude}, Lon {longitude}</strong>
    (approx. PIN {pin_code})
  </p>

  <p style="color:#888;font-size:12px;">
    This is an automated alert from DuckTrack. Please do not reply to this email.
  </p>
</body></html>
"""


def send_farmer_alert(
    farmer_email: str,
    farmer_name:  str,
    latitude:     float,
    longitude:    float,
    pin_code:     str,
) -> bool:
    html = FARMER_HTML_TEMPLATE.format(
        name      = farmer_name,
        pin_code  = pin_code,
        latitude  = latitude,
        longitude = longitude,
    )
    return _send(farmer_email, FARMER_SUBJECT, html)


# ── Veterinary alert ─────────────────────────────────────────────────────────

VET_SUBJECT = "🗺️ DuckTrack Vet Alert – Disease Heat Map for Your Area"

VET_HTML_TEMPLATE = """\
<html>
<head>
  <style>
    body {{ font-family: Arial, sans-serif; color: #333; }}
    .legend {{ display:flex; gap:12px; margin:12px 0; }}
    .legend-item {{ display:flex; align-items:center; gap:6px; }}
    .dot {{ width:14px; height:14px; border-radius:50%; }}
  </style>
</head>
<body>
  <h2 style="color:#c0392b;">🗺️ Duck Disease Heat Map Alert</h2>
  <p>Dear Dr. <strong>{name}</strong>,</p>
  <p>
    A duck disease has been detected at the coordinates below.
    The interactive heat map shows the risk zones around the infection site.
  </p>

  <p>
    <strong>Infection site:</strong> Lat <code>{latitude}</code>,
    Lon <code>{longitude}</code> &nbsp;|&nbsp; PIN: {pin_code}
  </p>

  <div class="legend">
    <div class="legend-item"><div class="dot" style="background:red;"></div> 0–5 km (high risk)</div>
    <div class="legend-item"><div class="dot" style="background:orange;"></div> 5–15 km (moderate risk)</div>
    <div class="legend-item"><div class="dot" style="background:blue;"></div> 15–25 km (low risk)</div>
  </div>

  <!-- Google Maps embed with coloured circles -->
  <div id="map" style="height:480px;width:100%;border-radius:8px;overflow:hidden;">
    <iframe
      width="100%" height="480" style="border:0;" loading="lazy" allowfullscreen
      src="https://www.google.com/maps/embed/v1/view?key={maps_api_key}&center={latitude},{longitude}&zoom=11">
    </iframe>
  </div>

  <!-- Fallback static link -->
  <p>
    <a href="https://www.google.com/maps/search/?api=1&query={latitude},{longitude}"
       target="_blank">
      Open location in Google Maps
    </a>
  </p>

  <!-- Interactive heat-map script (rendered in email clients that allow JS;
       for production use a pre-rendered image or a dedicated map link page) -->
  <script>
    function initMap() {{
      const center = {{ lat: {latitude}, lng: {longitude} }};
      const map = new google.maps.Map(document.getElementById('map'), {{
        center, zoom: 11
      }});
      const zones = [
        {{ radius: 5000,  color: '#ff0000', label: '0–5 km'   }},
        {{ radius: 15000, color: '#ff8c00', label: '5–15 km'  }},
        {{ radius: 25000, color: '#0000ff', label: '15–25 km' }},
      ];
      zones.forEach(z => new google.maps.Circle({{
        map, center,
        radius:      z.radius,
        strokeColor: z.color,
        strokeOpacity: 0.8,
        strokeWeight: 2,
        fillColor:   z.color,
        fillOpacity: 0.15,
      }}));
    }}
  </script>
  <script async defer
    src="https://maps.googleapis.com/maps/api/js?key={maps_api_key}&callback=initMap">
  </script>

  <p style="color:#888;font-size:12px;">
    This is an automated alert from DuckTrack. Please do not reply to this email.
  </p>
</body>
</html>
"""


def send_vet_alert(
    vet_email:  str,
    vet_name:   str,
    latitude:   float,
    longitude:  float,
    pin_code:   str,
) -> bool:
    html = VET_HTML_TEMPLATE.format(
        name         = vet_name,
        latitude     = latitude,
        longitude    = longitude,
        pin_code     = pin_code,
        maps_api_key = MAPS_API_KEY,
    )
    return _send(vet_email, VET_SUBJECT, html)


# ── Broadcast helpers ─────────────────────────────────────────────────────────

def broadcast_farmer_alerts(db, latitude: float, longitude: float, pin_code: str) -> list[str]:
    """
    Send alerts to ALL registered farmers in the same pin_code.
    Returns a list of emails that were successfully notified.
    """
    from database import Farmer
    farmers = db.query(Farmer).filter(Farmer.pin_code == pin_code).all()
    notified = []
    for f in farmers:
        ok = send_farmer_alert(f.email, f.name, latitude, longitude, pin_code)
        if ok:
            notified.append(f.email)
    return notified


def broadcast_vet_alerts(db, latitude: float, longitude: float, pin_code: str) -> list[str]:
    """
    Send alerts to ALL registered vets in the same pin_code.
    Returns a list of emails that were successfully notified.
    """
    from database import Veterinary
    vets = db.query(Veterinary).filter(Veterinary.pin_code == pin_code).all()
    notified = []
    for v in vets:
        ok = send_vet_alert(v.email, v.name, latitude, longitude, pin_code)
        if ok:
            notified.append(v.email)
    return notified