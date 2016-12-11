def safeget(dct, *keys):
    for key in keys:
        try:
            dct = dct[key] if dct[key] else {}
        except KeyError:
            return None
    return dct