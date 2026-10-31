import math

import pytest

from src import analisis


def test_tabel_lebar_menghitung_rasio_dasar(apbd_mini, penduduk_mini):
    lebar = analisis.tabel_lebar(apbd_mini, penduduk_mini)
    a = lebar[lebar["kode_bps"] == "11"].iloc[0]
    assert a["pendapatan"] == 100 and a["belanja"] == 80
    assert a["kemandirian"] == pytest.approx(40.0)
    assert a["ketergantungan"] == pytest.approx(50.0)
    assert a["porsi_modal"] == pytest.approx(20.0)
    assert a["porsi_pegawai"] == pytest.approx(50.0)
    assert a["serapan_belanja"] == pytest.approx(80.0)
    assert a["capaian_pendapatan"] == pytest.approx(100 / 110 * 100)
    assert a["belanja_per_kapita"] == pytest.approx(80 / 1_000_000)
    assert a["surplus"] == 20


def test_pembagi_nol_menghasilkan_nan_bukan_error(apbd_mini, penduduk_mini):
    lebar = analisis.tabel_lebar(apbd_mini, penduduk_mini)
    b = lebar[lebar["kode_bps"] == "12"].iloc[0]
    assert math.isnan(b["belanja_per_kapita"])
    assert b["kemandirian"] == 0.0  # PAD tidak ada -> 0, bukan NaN
    assert b["porsi_modal"] == pytest.approx(100.0)


def test_basis_anggaran_memakai_kolom_anggaran(apbd_mini, penduduk_mini):
    lebar = analisis.tabel_lebar(apbd_mini, penduduk_mini, basis="anggaran")
    a = lebar[lebar["kode_bps"] == "11"].iloc[0]
    assert a["pendapatan"] == 110 and a["belanja"] == 100
    with pytest.raises(ValueError):
        analisis.tabel_lebar(apbd_mini, penduduk_mini, basis="perkiraan")


def test_ringkasan_nasional_menjumlahkan_semua_provinsi(apbd_mini, penduduk_mini):
    lebar = analisis.tabel_lebar(apbd_mini, penduduk_mini)
    r = analisis.ringkasan_nasional(lebar)
    assert r["pendapatan"] == 150 and r["belanja"] == 130
    assert r["ketergantungan"] == pytest.approx(100 / 150 * 100)
    assert r["porsi_modal"] == pytest.approx(66 / 130 * 100)


def test_peringkat_mengurutkan_dan_menomori(apbd_mini, penduduk_mini):
    lebar = analisis.tabel_lebar(apbd_mini, penduduk_mini)
    teratas = analisis.peringkat(lebar, "belanja", n=1)
    assert list(teratas["provinsi"]) == ["A"] and list(teratas["peringkat"]) == [1]
    terbawah = analisis.peringkat(lebar, "belanja", terbesar=False)
    assert list(terbawah["provinsi"]) == ["B", "A"]


def test_sankey_seimbang_dan_tanpa_tautan_nol(apbd_mini):
    s = analisis.aliran_sankey(apbd_mini, "11", 2024)
    assert "Kas Daerah" in s["label"]
    assert all(v > 0 for v in s["nilai"])
    kas = s["label"].index("Kas Daerah")
    masuk = sum(v for t, v in zip(s["tujuan"], s["nilai"]) if t == kas)
    keluar = sum(v for t, v in zip(s["sumber"], s["nilai"]) if t == kas)
    assert masuk == 100 and keluar == 80
    # rincian PAD mengalir ke simpul PAD
    pad = s["label"].index("Pendapatan Asli Daerah")
    ke_pad = sum(v for t, v in zip(s["tujuan"], s["nilai"]) if t == pad)
    assert ke_pad == 40


def test_pertumbuhan_tahunan():
    import pandas as pd

    df = pd.DataFrame({"kode_bps": ["11", "11", "11"], "tahun": [2022, 2023, 2024], "belanja": [100.0, 110.0, 99.0]})
    hasil = analisis.tambah_pertumbuhan(df)
    nilai = hasil["pertumbuhan_belanja"].tolist()
    assert math.isnan(nilai[0])
    assert nilai[1] == pytest.approx(10.0)
    assert nilai[2] == pytest.approx(-10.0)


def test_komposisi_belanja_berjumlah_100_persen(apbd_mini, penduduk_mini):
    lebar = analisis.tabel_lebar(apbd_mini, penduduk_mini)
    panjang = analisis.komposisi_belanja(lebar)
    total = panjang.groupby("provinsi")["porsi"].sum()
    assert total["A"] == pytest.approx(100.0)
    assert total["B"] == pytest.approx(100.0)


def test_agregat_pulau_menjumlahkan_dan_menghitung_rasio(apbd, penduduk):
    lebar = analisis.tabel_lebar(apbd, penduduk)
    th = lebar[lebar["tahun"] == 2024]
    pulau = analisis.agregat_pulau(th).set_index("pulau")
    assert len(pulau) == 7
    assert pulau["belanja"].sum() == pytest.approx(th["belanja"].sum())
    jawa = pulau.loc["Jawa"]
    assert jawa["porsi_modal"] + jawa["porsi_pegawai"] + jawa["porsi_barang"] + jawa["porsi_lainnya"] == pytest.approx(100.0)
    assert jawa["kemandirian"] > pulau.loc["Papua", "kemandirian"]


def test_metrik_terdaftar_ada_di_tabel(apbd, penduduk):
    lebar = analisis.tabel_lebar(apbd, penduduk)
    for kunci in analisis.METRIK:
        assert kunci in lebar.columns, kunci


def test_data_nyata_masuk_akal(apbd, penduduk):
    lebar = analisis.tabel_lebar(apbd, penduduk)
    th = lebar[lebar["tahun"] == 2024]
    assert len(th) == 38
    assert th["kemandirian"].between(0, 100).all()
    assert th["ketergantungan"].between(0, 100).all()
    assert (th["porsi_modal"] + th["porsi_pegawai"] + th["porsi_barang"] + th["porsi_lainnya"]).round(3).eq(100).all()
    # total pendapatan daerah seluruh Indonesia 2024 berada di kisaran 1,2-1,6 kuadriliun rupiah
    assert 1.2e15 < th["pendapatan"].sum() < 1.6e15
    # DKI Jakarta adalah provinsi paling mandiri secara fiskal
    assert analisis.peringkat(th, "kemandirian", n=1)["provinsi"].iloc[0] == "DKI Jakarta"
