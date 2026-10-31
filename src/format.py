"""Pemformatan angka ala Indonesia: titik untuk ribuan, koma untuk desimal."""
from __future__ import annotations

import math


def angka_id(nilai: float, desimal: int = 1) -> str:
    """Memformat angka dengan pemisah ribuan '.' dan desimal ','."""
    if nilai is None or (isinstance(nilai, float) and math.isnan(nilai)):
        return "-"
    teks = f"{nilai:,.{desimal}f}"
    return teks.replace(",", "\u0000").replace(".", ",").replace("\u0000", ".")


def rupiah(nilai: float, desimal: int = 1) -> str:
    """Rupiah dalam satuan ringkas: T (triliun), M (miliar), jt (juta), rb (ribu).

    >>> rupiah(1_367_800_000_000_000)
    'Rp 1.367,8 T'
    >>> rupiah(45_200_000_000)
    'Rp 45,2 M'
    """
    if nilai is None or (isinstance(nilai, float) and math.isnan(nilai)):
        return "-"
    tanda = "-" if nilai < 0 else ""
    n = abs(nilai)
    for batas, satuan in ((1e12, "T"), (1e9, "M"), (1e6, "jt"), (1e3, "rb")):
        if n >= batas:
            return f"{tanda}Rp {angka_id(n / batas, desimal)} {satuan}"
    return f"{tanda}Rp {angka_id(n, 0)}"


def persen(nilai: float, desimal: int = 1) -> str:
    """Persentase dengan koma desimal, misal 37,4 %."""
    if nilai is None or (isinstance(nilai, float) and math.isnan(nilai)):
        return "-"
    return f"{angka_id(nilai, desimal)} %"


def orang(nilai: float) -> str:
    """Jumlah penduduk dalam juta atau ribu jiwa."""
    if nilai is None or (isinstance(nilai, float) and math.isnan(nilai)):
        return "-"
    if nilai >= 1e6:
        return f"{angka_id(nilai / 1e6, 2)} juta jiwa"
    return f"{angka_id(nilai / 1e3, 0)} ribu jiwa"
