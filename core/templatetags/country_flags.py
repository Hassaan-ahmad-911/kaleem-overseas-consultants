import re

from django import template

register = template.Library()

# Country name (lowercase) -> ISO 3166-1 alpha-2 code used by the flag-icons CSS library.
COUNTRY_CODES = {
    "afghanistan": "af", "albania": "al", "algeria": "dz", "argentina": "ar", "armenia": "am",
    "australia": "au", "austria": "at", "azerbaijan": "az", "bahrain": "bh", "bangladesh": "bd",
    "belarus": "by", "belgium": "be", "bosnia and herzegovina": "ba", "brazil": "br", "brunei": "bn",
    "bulgaria": "bg", "cambodia": "kh", "canada": "ca", "chile": "cl", "china": "cn", "colombia": "co",
    "croatia": "hr", "cyprus": "cy", "czech republic": "cz", "czechia": "cz", "denmark": "dk",
    "egypt": "eg", "estonia": "ee", "fiji": "fj", "finland": "fi", "france": "fr", "georgia": "ge",
    "germany": "de", "greece": "gr", "hong kong": "hk", "hungary": "hu", "iceland": "is", "india": "in",
    "indonesia": "id", "iran": "ir", "iraq": "iq", "ireland": "ie", "italy": "it", "japan": "jp",
    "jordan": "jo", "kazakhstan": "kz", "kenya": "ke", "kosovo": "xk", "kuwait": "kw", "kyrgyzstan": "kg",
    "laos": "la", "latvia": "lv", "lebanon": "lb", "lithuania": "lt", "luxembourg": "lu",
    "malaysia": "my", "maldives": "mv", "malta": "mt", "mexico": "mx", "mongolia": "mn",
    "montenegro": "me", "morocco": "ma", "myanmar": "mm", "nepal": "np", "netherlands": "nl",
    "new zealand": "nz", "north macedonia": "mk", "norway": "no", "oman": "om", "pakistan": "pk",
    "philippines": "ph", "poland": "pl", "portugal": "pt", "qatar": "qa", "romania": "ro",
    "russia": "ru", "saudi arabia": "sa", "serbia": "rs", "singapore": "sg", "slovakia": "sk",
    "slovenia": "si", "south africa": "za", "south korea": "kr", "korea": "kr", "spain": "es",
    "sri lanka": "lk", "sweden": "se", "switzerland": "ch", "taiwan": "tw", "tajikistan": "tj",
    "tanzania": "tz", "thailand": "th", "turkey": "tr", "turkiye": "tr", "türkiye": "tr",
    "turkmenistan": "tm", "ukraine": "ua", "united arab emirates": "ae", "uae": "ae", "dubai": "ae",
    "united kingdom": "gb", "uk": "gb", "england": "gb", "great britain": "gb",
    "united states": "us", "united states of america": "us", "usa": "us", "us": "us", "america": "us",
    "uzbekistan": "uz", "vietnam": "vn", "schengen": "eu", "europe": "eu",
}


@register.filter
def flag_code(country_name):
    """Return the flag-icons code for a country name, or "" when it is unknown."""
    name = re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", str(country_name or "").lower())).strip()
    if name.startswith("the "):
        name = name[4:]
    return COUNTRY_CODES.get(name, "")
