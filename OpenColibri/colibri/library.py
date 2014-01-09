def array_unique(list):
    seen = set()
    seen_add = seen.add
    return [x for x in list if x not in seen and not seen_add(x)]


def array_diff(list1, list2):
    return list(set(list1).difference(list2))


def array_explode(separator, string):
    return string.split(separator)


def get_slug(string):
    return string.replace(' ', '-').lower()


def safe_convert_float(s):
    try:
        x = float(s)
        return x
    except ValueError:
        return 0