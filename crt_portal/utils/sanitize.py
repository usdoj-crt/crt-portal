CITY_PREFIXES = [
    ('ST', 'SAINT'),
    ('FT', 'FORT'),
]


def sanitize_city(city: str) -> str:
    city = city.upper().strip()
    for prefix, replacement in CITY_PREFIXES:
        if city.startswith(f'{prefix}.'):
            return replacement + city.removeprefix(f'{prefix}.')
        if city.startswith(f'{prefix} '):
            return replacement + city.removeprefix(f'{prefix}')
    return city
