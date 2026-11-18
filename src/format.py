"""Pemformatan angka ala Indonesia: titik untuk ribuan, koma untuk desimal."""
from __future__ import annotations

import pandas as pd


def _kosong(nilai) -> bool:
    """True untuk None, NaN, NaT, dan pd.NA."""
    try:
        return bool(pd.isna(nilai))
    except (TypeError, ValueError):
        return False


def angka_id(nilai: float, desimal: int = 1) -> str:
    """Memformat angka dengan pemisah ribuan '.' dan desimal ','."""
    if _kosong(nilai):
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
    if _kosong(nilai):
        return "-"
    n = abs(nilai)
    satuan_ringkas = ((1e12, "T"), (1e9, "M"), (1e6, "jt"), (1e3, "rb"), (1.0, ""))
    for i, (batas, satuan) in enumerate(satuan_ringkas):
        if n >= batas or batas == 1.0:
            angka = desimal if satuan else 0
            # 999,96 M dibulatkan jadi "1.000,0 M"; naikkan ke satuan berikutnya.
            if i > 0 and round(n / batas, angka) >= 1000:
                batas, satuan = satuan_ringkas[i - 1]
                angka = desimal
            teks = angka_id(n / batas, angka)
            # Minus kecil yang dibulatkan jadi nol tidak perlu tanda "-".
            tanda = "-" if nilai < 0 and round(n / batas, angka) != 0 else ""
            return f"{tanda}Rp {teks}{' ' + satuan if satuan else ''}"


def persen(nilai: float, desimal: int = 1) -> str:
    """Persentase dengan koma desimal, misal 37,4 %."""
    if _kosong(nilai):
        return "-"
    return f"{angka_id(nilai, desimal)} %"


def orang(nilai: float) -> str:
    """Jumlah penduduk dalam juta atau ribu jiwa."""
    if _kosong(nilai):
        return "-"
    if nilai >= 1e6:
        return f"{angka_id(nilai / 1e6, 2)} juta jiwa"
    if nilai >= 1e3:
        return f"{angka_id(nilai / 1e3, 0)} ribu jiwa"
    return f"{angka_id(nilai, 0)} jiwa"
