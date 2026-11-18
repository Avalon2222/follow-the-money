import math

from src import format as fmt


def test_angka_id_memakai_titik_ribuan_dan_koma_desimal():
    assert fmt.angka_id(1234567.891, 2) == "1.234.567,89"
    assert fmt.angka_id(0.5, 1) == "0,5"


def test_rupiah_memilih_satuan_yang_tepat():
    assert fmt.rupiah(1_367_800_000_000_000) == "Rp 1.367,8 T"
    assert fmt.rupiah(45_200_000_000) == "Rp 45,2 M"
    assert fmt.rupiah(3_100_000) == "Rp 3,1 jt"
    assert fmt.rupiah(2_500) == "Rp 2,5 rb"
    assert fmt.rupiah(999) == "Rp 999"
    assert fmt.rupiah(-7_000_000_000) == "-Rp 7,0 M"


def test_nilai_kosong_menjadi_strip():
    assert fmt.rupiah(math.nan) == "-"
    assert fmt.persen(None) == "-"
    assert fmt.orang(math.nan) == "-"


def test_persen_dan_orang():
    assert fmt.persen(37.456) == "37,5 %"
    assert fmt.orang(50_759_000) == "50,76 juta jiwa"
    assert fmt.orang(549_700) == "550 ribu jiwa"


def test_nilai_pd_na_juga_menjadi_strip():
    import pandas as pd

    assert fmt.angka_id(pd.NA) == "-"
    assert fmt.rupiah(pd.NA) == "-"
    assert fmt.persen(pd.NA) == "-"
    assert fmt.orang(pd.NA) == "-"


def test_orang_di_bawah_seribu_tetap_terbaca():
    assert fmt.orang(450) == "450 jiwa"
    assert fmt.orang(1_000) == "1 ribu jiwa"


def test_rupiah_naik_satuan_saat_pembulatan_mencapai_seribu():
    assert fmt.rupiah(999_960_000_000) == "Rp 1,0 T"
    assert fmt.rupiah(999_960_000) == "Rp 1,0 M"
    assert fmt.rupiah(999.6) == "Rp 1,0 rb"
    assert fmt.rupiah(999_940_000) == "Rp 999,9 jt"


def test_rupiah_minus_kecil_tidak_jadi_minus_nol():
    assert fmt.rupiah(-0.4) == "Rp 0"
    assert fmt.rupiah(-0.6) == "-Rp 1"


def test_orang_hampir_sejuta_ditulis_dalam_juta():
    assert fmt.orang(999_600) == "1,00 juta jiwa"
    assert fmt.orang(999_400) == "999 ribu jiwa"
    assert fmt.orang(999.7) == "1 ribu jiwa"


def test_tak_hingga_menjadi_strip():
    assert fmt.rupiah(math.inf) == "-"
    assert fmt.persen(-math.inf) == "-"
    assert fmt.orang(math.inf) == "-"
    assert fmt.angka_id(math.inf) == "-"
