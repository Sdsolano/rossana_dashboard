"""
Países y zonas horarias (IANA) para el formulario de terapeutas.
Orden: países de uso común primero (España, Latinoamérica, etc.).
"""

COUNTRIES_WITH_TIMEZONES = [
    {"code": "ES", "name": "España", "timezones": ["Europe/Madrid", "Atlantic/Canary"]},
    {"code": "AR", "name": "Argentina", "timezones": ["America/Argentina/Buenos_Aires", "America/Argentina/Cordoba", "America/Argentina/Mendoza"]},
    {"code": "MX", "name": "México", "timezones": ["America/Mexico_City", "America/Tijuana", "America/Cancun", "America/Merida", "America/Monterrey"]},
    {"code": "CO", "name": "Colombia", "timezones": ["America/Bogota"]},
    {"code": "CL", "name": "Chile", "timezones": ["America/Santiago", "America/Punta_Arenas"]},
    {"code": "PE", "name": "Perú", "timezones": ["America/Lima"]},
    {"code": "EC", "name": "Ecuador", "timezones": ["America/Guayaquil"]},
    {"code": "VE", "name": "Venezuela", "timezones": ["America/Caracas"]},
    {"code": "UY", "name": "Uruguay", "timezones": ["America/Montevideo"]},
    {"code": "PY", "name": "Paraguay", "timezones": ["America/Asuncion"]},
    {"code": "BO", "name": "Bolivia", "timezones": ["America/La_Paz"]},
    {"code": "BR", "name": "Brasil", "timezones": ["America/Sao_Paulo", "America/Rio_Branco", "America/Manaus", "America/Fortaleza", "America/Recife"]},
    {"code": "CR", "name": "Costa Rica", "timezones": ["America/Costa_Rica"]},
    {"code": "PA", "name": "Panamá", "timezones": ["America/Panama"]},
    {"code": "CU", "name": "Cuba", "timezones": ["America/Havana"]},
    {"code": "DO", "name": "República Dominicana", "timezones": ["America/Santo_Domingo"]},
    {"code": "PR", "name": "Puerto Rico", "timezones": ["America/Puerto_Rico"]},
    {"code": "GT", "name": "Guatemala", "timezones": ["America/Guatemala"]},
    {"code": "HN", "name": "Honduras", "timezones": ["America/Tegucigalpa"]},
    {"code": "SV", "name": "El Salvador", "timezones": ["America/El_Salvador"]},
    {"code": "NI", "name": "Nicaragua", "timezones": ["America/Managua"]},
    {"code": "US", "name": "Estados Unidos", "timezones": ["America/New_York", "America/Chicago", "America/Denver", "America/Los_Angeles", "America/Phoenix"]},
    {"code": "CA", "name": "Canadá", "timezones": ["America/Toronto", "America/Vancouver", "America/Montreal"]},
    {"code": "GB", "name": "Reino Unido", "timezones": ["Europe/London"]},
    {"code": "FR", "name": "Francia", "timezones": ["Europe/Paris"]},
    {"code": "DE", "name": "Alemania", "timezones": ["Europe/Berlin"]},
    {"code": "IT", "name": "Italia", "timezones": ["Europe/Rome"]},
    {"code": "PT", "name": "Portugal", "timezones": ["Europe/Lisbon", "Atlantic/Azores", "Atlantic/Madeira"]},
    {"code": "NL", "name": "Países Bajos", "timezones": ["Europe/Amsterdam"]},
    {"code": "BE", "name": "Bélgica", "timezones": ["Europe/Brussels"]},
    {"code": "CH", "name": "Suiza", "timezones": ["Europe/Zurich"]},
    {"code": "AT", "name": "Austria", "timezones": ["Europe/Vienna"]},
    {"code": "PL", "name": "Polonia", "timezones": ["Europe/Warsaw"]},
    {"code": "SE", "name": "Suecia", "timezones": ["Europe/Stockholm"]},
    {"code": "NO", "name": "Noruega", "timezones": ["Europe/Oslo"]},
    {"code": "DK", "name": "Dinamarca", "timezones": ["Europe/Copenhagen"]},
    {"code": "FI", "name": "Finlandia", "timezones": ["Europe/Helsinki"]},
    {"code": "GR", "name": "Grecia", "timezones": ["Europe/Athens"]},
    {"code": "RU", "name": "Rusia", "timezones": ["Europe/Moscow", "Asia/Yekaterinburg", "Asia/Novosibirsk"]},
    {"code": "AU", "name": "Australia", "timezones": ["Australia/Sydney", "Australia/Melbourne", "Australia/Perth", "Australia/Adelaide", "Australia/Brisbane"]},
    {"code": "NZ", "name": "Nueva Zelanda", "timezones": ["Pacific/Auckland"]},
    {"code": "JP", "name": "Japón", "timezones": ["Asia/Tokyo"]},
    {"code": "CN", "name": "China", "timezones": ["Asia/Shanghai", "Asia/Hong_Kong"]},
    {"code": "IN", "name": "India", "timezones": ["Asia/Kolkata"]},
    {"code": "ZA", "name": "Sudáfrica", "timezones": ["Africa/Johannesburg"]},
    {"code": "EG", "name": "Egipto", "timezones": ["Africa/Cairo"]},
    {"code": "IL", "name": "Israel", "timezones": ["Asia/Jerusalem"]},
    {"code": "TR", "name": "Turquía", "timezones": ["Europe/Istanbul"]},
]


def get_countries_for_api():
    """Lista para la API: cada país con timezones como { value, label }."""
    result = []
    for c in COUNTRIES_WITH_TIMEZONES:
        tz_list = []
        for tz in c["timezones"]:
            # label: nombre legible (última parte de la zona, ej. "Buenos_Aires" -> "Buenos Aires")
            label = tz.split("/")[-1].replace("_", " ")
            tz_list.append({"value": tz, "label": label})
        result.append({
            "code": c["code"],
            "name": c["name"],
            "timezones": tz_list,
        })
    return result


def timezone_verbose_to_minutes(timezone_verbose):
    """Convierte IANA timezone (ej. America/Argentina/Buenos_Aires) o legacy UTC±HH:MM a offset en minutos (UTC)."""
    if not timezone_verbose:
        return 0
    # Formato legacy guardado en BD: "UTC-03:00", "UTC+01:00"
    import re
    m = re.match(r"^UTC([+-])(\d{1,2}):(\d{2})$", timezone_verbose.strip())
    if m:
        sign = 1 if m.group(1) == "+" else -1
        hours = int(m.group(2))
        minutes = int(m.group(3))
        return sign * (hours * 60 + minutes)
    try:
        from zoneinfo import ZoneInfo
        from datetime import datetime
        z = ZoneInfo(timezone_verbose)
        now = datetime.now(z)
        offset = z.utcoffset(now)
        if offset is None:
            return 0
        return int(offset.total_seconds() / 60)
    except Exception:
        return 0
