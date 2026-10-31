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
