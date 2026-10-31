from src import skema


def test_38_provinsi_dengan_kode_unik():
    assert len(skema.NAMA_PROVINSI) == 38
    assert len(set(skema.NAMA_PROVINSI.values())) == 38


def test_pemetaan_djpk_menutup_semua_provinsi():
    assert len(skema.KODE_DJPK_KE_BPS) == 38
    assert set(skema.KODE_DJPK_KE_BPS.values()) == set(skema.NAMA_PROVINSI)


def test_setiap_provinsi_punya_pulau():
    assert set(skema.PULAU) == set(skema.NAMA_PROVINSI)
    assert set(skema.PULAU.values()) == {
        "Sumatera", "Jawa", "Bali & Nusa Tenggara", "Kalimantan", "Sulawesi", "Maluku", "Papua",
    }


def test_induk_akun_ada_dan_tingkatnya_naik_satu():
    for akun, (tingkat, induk) in skema.STRUKTUR_AKUN.items():
        if tingkat == 1:
            assert induk is None, akun
        else:
            assert induk in skema.STRUKTUR_AKUN, f"{akun} merujuk induk tak dikenal {induk}"
            assert skema.STRUKTUR_AKUN[induk][0] == tingkat - 1, akun


def test_alias_mengarah_ke_akun_baku():
    for alias, baku in skema.ALIAS_AKUN.items():
        assert alias not in skema.STRUKTUR_AKUN
        assert baku in skema.STRUKTUR_AKUN


def test_label_mengembalikan_nama_ramah_atau_apa_adanya():
    assert skema.label("PAD") == "Pendapatan Asli Daerah"
    assert skema.label("Pajak Daerah") == "Pajak Daerah"
