import math


def get_si_prefix(value):
    PREFIXES = {24:'Y', 21:'Z', 18:'E', 15:'P', 12:'T', 9:'G', 6:'M', 3:'k', 0:'', -3:'m', -6:'µ', -9:'n', -12:'p', -15:'f', -18:'a', -21: 'z', -24:'y'}
    exponent, prefix = 0, ''
    if math.isfinite(value) and value != 0:
        for exp, pref in PREFIXES.items():
            if math.log10(abs(value)) >= exp:
                exponent = exp
                prefix = pref
                break
    return exponent, prefix


def si_prefixed(value, unit='', fmt_str='.3g'):
    exponent, prefix = get_si_prefix(value)
    number_str = ('{:' + fmt_str + '}').format(value/pow(10,exponent))
    suffix = prefix + unit
    if len(suffix) > 0:
        suffix = ' ' + suffix
    return number_str + suffix
