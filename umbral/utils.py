import math

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.asymmetric import ec
from umbral import openssl

def lambda_coeff(id_i, selected_ids):
    ids = [x for x in selected_ids if x != id_i]

    if not ids:
        return None

    div_0 = ~(ids[0] - id_i)
    result = ids[0] * div_0
    for id_j in ids[1:]:
        div_j = ~(id_j - id_i)
        result = result * (id_j * div_j)

    return result


def poly_eval(coeff, x):
    result = coeff[-1]
    for i in range(-2, -len(coeff) - 1, -1):
        result = ((result * x) + coeff[i])

    return result


def kdf(ecpoint, key_length):
    data = ecpoint.to_bytes(is_compressed=True)

    return HKDF(
        algorithm=hashes.BLAKE2b(64),
        length=key_length,
        salt=None,
        info=None,
        backend=default_backend()
    ).derive(data)


def get_curve_keysize_bytes(curve):
    return (curve.key_size + 7) // 8

def get_field_order_size_in_bytes(curve):

    backend = default_backend()
    try:
        curve_nid = backend._elliptic_curve_to_nid(curve)
    except AttributeError:
        # Presume that the user passed in the curve_nid
        curve_nid = curve

    group = openssl._get_ec_group_by_curve_nid(curve_nid)
    size_in_bits = openssl._get_ec_group_degree(group)
    return (size_in_bits + 7) // 8
