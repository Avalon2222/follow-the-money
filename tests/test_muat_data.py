from src import muat_data, skema


def test_apbd_memuat_38_provinsi_pada_2023_dan_2024(apbd):
    per_tahun = apbd.groupby("tahun")["kode_bps"].nunique()
    assert per_tahun[2023] == 38
    assert per_tahun[2024] == 38
    # empat provinsi baru di Papua belum punya APBD pada 2022
    assert per_tahun[2022] == 34


def test_semua_akun_dikenal_skema(apbd):
    assert set(apbd["akun"]) <= set(skema.STRUKTUR_AKUN)


def test_tidak_ada_baris_ganda(apbd):
    assert not apbd.duplicated(subset=["kode_bps", "tahun", "akun"]).any()


def test_jumlah_tingkat_2_sama_dengan_tingkat_1(apbd):
    for akun1 in ("Pendapatan Daerah", "Belanja Daerah"):
        for basis in ("anggaran", "realisasi"):
            induk = apbd[apbd["akun"] == akun1].set_index(["kode_bps", "tahun"])[basis]
            anak = apbd[apbd["induk"] == akun1].groupby(["kode_bps", "tahun"])[basis].sum()
            selisih = (anak - induk).abs() / induk.where(induk != 0)
            assert selisih.max() < 1e-6, (akun1, basis, selisih.max())


def test_penduduk_dan_geojson_cocok_dengan_skema(apbd, penduduk, geojson):
    assert muat_data.periksa_konsistensi(apbd, penduduk, geojson) == []
    assert len(geojson["features"]) == 38
    assert penduduk["penduduk_2025"].sum() > 280_000_000


def test_nama_provinsi_konsisten_antar_tabel(apbd, penduduk, geojson):
    nama_geo = {f["properties"]["kode_bps"]: f["properties"]["provinsi"] for f in geojson["features"]}
    nama_pend = dict(zip(penduduk["kode_bps"], penduduk["provinsi"]))
    nama_apbd = dict(zip(apbd["kode_bps"], apbd["provinsi"]))
    assert nama_geo == skema.NAMA_PROVINSI
    assert nama_pend == skema.NAMA_PROVINSI
    assert nama_apbd == skema.NAMA_PROVINSI
