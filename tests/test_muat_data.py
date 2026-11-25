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


def test_penduduk_kosong_tidak_menggagalkan_pemuatan(tmp_path):
    path = tmp_path / "penduduk.csv"
    path.write_text("kode_bps,provinsi,penduduk_2025,luas_km2\n 11,A,,10\n12,B,2000,5\n", encoding="utf-8")
    df = muat_data.muat_penduduk(path)
    assert list(df["kode_bps"]) == ["11", "12"]
    assert df["penduduk_2025"].isna().iloc[0]
    assert df["penduduk_2025"].iloc[1] == 2000


def test_kode_apbd_berspasi_tetap_dapat_pulau(tmp_path):
    path = tmp_path / "apbd.csv"
    path.write_text(
        "kode_bps,provinsi,tahun,akun,induk,tingkat,anggaran,realisasi\n"
        " 11 ,Aceh,2024,Pendapatan Daerah,,1,10,9\n",
        encoding="utf-8",
    )
    df = muat_data.muat_apbd(path)
    assert df["kode_bps"].iloc[0] == "11"
    assert df["pulau"].iloc[0] == "Sumatera"


def test_nama_akun_berspasi_dan_ejaan_lain_dirapikan(tmp_path):
    path = tmp_path / "apbd.csv"
    path.write_text(
        "kode_bps,provinsi,tahun,akun,induk,tingkat,anggaran,realisasi\n"
        "11,Aceh,2024, Belanja Daerah ,,1,10,9\n"
        "11,Aceh,2024,Belanja Barang Jasa,Belanja Daerah ,2,4,3\n",
        encoding="utf-8",
    )
    df = muat_data.muat_apbd(path)
    assert df["akun"].tolist() == ["Belanja Daerah", "Belanja Barang dan Jasa"]
    assert df["induk"].tolist() == ["", "Belanja Daerah"]


def test_periksa_konsistensi_kode_kosong_dilaporkan(apbd, penduduk, geojson):
    rusak = apbd.copy()
    rusak.loc[rusak.index[0], "kode_bps"] = None
    masalah = muat_data.periksa_konsistensi(rusak, penduduk, geojson)
    assert any("tanpa kode_bps" in m for m in masalah)


def test_muat_apbd_baris_tanpa_tahun_dibuang(tmp_path):
    asli = muat_data.FOLDER_DATA / "apbd_provinsi.csv"
    baris = asli.read_text(encoding="utf-8").splitlines()
    kolom = baris[0].split(",")
    rusak = baris[1].split(",")
    rusak[kolom.index("tahun")] = ""
    path = tmp_path / "apbd.csv"
    path.write_text("\n".join([baris[0], baris[1], ",".join(rusak)]) + "\n", encoding="utf-8")
    df = muat_data.muat_apbd(path)
    assert len(df) == 1
    assert df["tahun"].dtype.kind == "i"


def test_nilai_rupiah_teks_jadi_angka(tmp_path):
    path = tmp_path / "apbd.csv"
    path.write_text(
        "kode_bps,provinsi,tahun,akun,induk,tingkat,anggaran,realisasi\n"
        "11,Aceh,2024,Belanja Daerah,,1,10,-\n"
        "11,Aceh,2024,Pendapatan Daerah,,1,12,11\n",
        encoding="utf-8",
    )
    df = muat_data.muat_apbd(path)
    assert df["realisasi"].dtype.kind == "f"
    assert df["realisasi"].isna().iloc[0]
    assert df["realisasi"].iloc[1] == 11


def test_penduduk_inf_dianggap_kosong(tmp_path):
    path = tmp_path / "penduduk.csv"
    path.write_text("kode_bps,provinsi,penduduk_2025,luas_km2\n11,A,inf,10\n12,B,2000,5\n", encoding="utf-8")
    df = muat_data.muat_penduduk(path)
    assert df["penduduk_2025"].isna().iloc[0]
    assert df["penduduk_2025"].iloc[1] == 2000


def test_periksa_konsistensi_fitur_geojson_tanpa_kode(apbd, penduduk, geojson):
    rusak = {**geojson, "features": [*geojson["features"], {"type": "Feature", "properties": {"provinsi": "X"}, "geometry": None}]}
    masalah = muat_data.periksa_konsistensi(apbd, penduduk, rusak)
    assert masalah == ["geojson: 1 fitur tanpa kode_bps"]
