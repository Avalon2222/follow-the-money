"""Follow the Money: ke mana uang daerah mengalir?

Dasbor Streamlit untuk menelusuri APBD 38 provinsi (agregat pemprov + kabupaten/kota)
dari data publik DJPK Kementerian Keuangan.
"""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit_folium import st_folium

from src import analisis, muat_data, peta
from src.format import angka_id, orang, persen, rupiah
from src.skema import label

st.set_page_config(page_title="Follow the Money", page_icon="💸", layout="wide")

WARNA_PULAU = {
    "Sumatera": "#1b9e77", "Jawa": "#d95f02", "Bali & Nusa Tenggara": "#7570b3", "Kalimantan": "#e7298a",
    "Sulawesi": "#66a61e", "Maluku": "#e6ab02", "Papua": "#a6761d",
}
WARNA_BELANJA = {
    "Pegawai": "#d62728", "Barang & Jasa": "#ff7f0e", "Modal": "#1f77b4",
    "Lainnya (bagi hasil, bankeu, hibah, bansos)": "#7f7f7f",
}


# ---------------------------------------------------------------- data
@st.cache_data(show_spinner=False)
def muat_semua():
    apbd = muat_data.muat_apbd()
    penduduk = muat_data.muat_penduduk()
    geojson = muat_data.muat_geojson()
    return apbd, penduduk, geojson


@st.cache_data(show_spinner=False)
def tabel(basis: str) -> pd.DataFrame:
    apbd, penduduk, _ = muat_semua()
    return analisis.tabel_lebar(apbd, penduduk, basis=basis)


def nilai_terformat(nilai: float, satuan: str) -> str:
    return peta.format_nilai(nilai, satuan)


def grafik_rapi(fig: go.Figure, tinggi: int = 420) -> go.Figure:
    fig.update_layout(height=tinggi, margin=dict(l=10, r=10, t=40, b=10), legend_title_text="",
                      plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    return fig


apbd, penduduk, geojson = muat_semua()
TAHUN_TERSEDIA = sorted(apbd["tahun"].unique())

# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.title("💸 Follow the Money")
    st.caption("Every rupiah has a destination.")
    tahun = st.select_slider("Tahun anggaran", options=TAHUN_TERSEDIA, value=TAHUN_TERSEDIA[-1])
    basis = st.radio("Angka yang dipakai", ["realisasi", "anggaran"], horizontal=True,
                     help="Realisasi = yang benar-benar diterima/dibelanjakan. Anggaran = rencana dalam APBD.")
    mode_belajar = st.toggle("🎓 Mode belajar", value=False,
                             help="Menampilkan penjelasan konsep dan rumus di setiap bagian.")
    st.divider()
    st.markdown(
        "Data: APBD seluruh pemda per provinsi (pemprov + kabupaten/kota) dari "
        "[Portal SIKD DJPK Kemenkeu](https://djpk.kemenkeu.go.id/portal/data/apbd); "
        "penduduk dari BPS. Rincian di tab **Data & Sumber**."
    )

lebar = tabel(basis)
th = lebar[lebar["tahun"] == tahun].copy()
nasional = analisis.ringkasan_nasional(th)

# ---------------------------------------------------------------- header
st.title("💸 Follow the Money")
st.markdown(
    f"**Setiap rupiah punya tujuan.** Pada {tahun}, pemerintah daerah di seluruh Indonesia "
    f"{'membelanjakan' if basis == 'realisasi' else 'merencanakan belanja'} **{rupiah(nasional['belanja'])}**. "
    f"Sekitar **{persen(nasional['ketergantungan'])}** pendapatannya berasal dari kiriman pemerintah pusat. "
    "Dari mana uang itu datang, dan ke mana ia pergi?"
)

k1, k2, k3, k4 = st.columns(4)
k1.metric("Pendapatan daerah", rupiah(nasional["pendapatan"]))
k2.metric("Belanja daerah", rupiah(nasional["belanja"]))
k3.metric("Porsi transfer pusat", persen(nasional["ketergantungan"]), help="TKD / total pendapatan daerah")
k4.metric("Porsi belanja modal", persen(nasional["porsi_modal"]), help="Belanja modal / total belanja daerah")

tab_peta, tab_profil, tab_banding, tab_tren, tab_data, tab_cara = st.tabs(
    ["🗺️ Peta", "🔍 Profil Provinsi", "⚖️ Perbandingan", "📈 Tren", "📋 Data & Sumber", "🧭 Cara Kerja"]
)

# ---------------------------------------------------------------- tab peta
with tab_peta:
    kolom_kiri, kolom_kanan = st.columns([3, 2])
    with kolom_kiri:
        pilihan = st.selectbox(
            "Indikator pada peta",
            options=list(analisis.METRIK),
            format_func=lambda k: analisis.METRIK[k].nama,
            index=list(analisis.METRIK).index("belanja_per_kapita"),
        )
        m = analisis.METRIK[pilihan]
        st.caption(m.keterangan)
        peta_folium = peta.buat_peta(geojson, th, pilihan, tahun)
        st_folium(peta_folium, height=520, use_container_width=True, returned_objects=[])

    with kolom_kanan:
        urut = analisis.peringkat(th, pilihan)
        st.subheader("Peringkat 38 provinsi")
        fig = px.bar(
            urut.sort_values(pilihan), x=pilihan, y="provinsi", orientation="h", color="pulau",
            color_discrete_map=WARNA_PULAU, custom_data=["peringkat"],
        )
        fig.update_traces(hovertemplate="%{y}<br>Peringkat %{customdata[0]}<br>%{x:,.0f}<extra></extra>")
        fig.update_layout(yaxis_title="", xaxis_title=m.nama)
        st.plotly_chart(grafik_rapi(fig, 760), use_container_width=True)

    teratas, terbawah = urut.iloc[0], urut.iloc[-1]
    median = th[pilihan].median()
    st.info(
        f"**{teratas['provinsi']}** tertinggi dengan {nilai_terformat(teratas[pilihan], m.satuan)}, "
        f"**{terbawah['provinsi']}** terendah dengan {nilai_terformat(terbawah[pilihan], m.satuan)}. "
        f"Median 38 provinsi: {nilai_terformat(median, m.satuan)}."
    )
    if mode_belajar:
        with st.expander("🎓 Membaca peta choropleth"):
            st.markdown(
                """
                Peta ini adalah **choropleth**: setiap provinsi diwarnai menurut satu angka. Semakin gelap,
                semakin besar nilainya. Tiga hal yang perlu diingat:

                1. **Total vs per kapita.** Jawa Barat selalu gelap pada total belanja karena penduduknya 50 juta.
                   Ganti ke *Belanja per Penduduk* dan peta berbalik: provinsi di Papua dan Kalimantan Timur
                   menjadi paling gelap.
                2. **Kelas warna** dibentuk dari 7 pembagian rentang nilai (*bins*). Satu provinsi ekstrem
                   (misalnya DKI Jakarta pada kemandirian fiskal) dapat "menyedot" satu kelas sendiri.
                3. **Luas bukan nilai.** Mata cenderung menganggap wilayah luas sebagai wilayah penting.
                   Kalimantan Tengah luasnya 4 kali Jawa Barat, tetapi belanjanya seperempatnya.

                Kode peta ada di `src/peta.py`; data per provinsi digabungkan dengan GeoJSON lewat kunci `kode_bps`.
                """
            )

# ---------------------------------------------------------------- tab profil
with tab_profil:
    daftar = th.sort_values("provinsi")["provinsi"].tolist()
    prov = st.selectbox("Pilih provinsi", daftar, index=daftar.index("Jawa Barat") if "Jawa Barat" in daftar else 0)
    baris = th[th["provinsi"] == prov].iloc[0]
    kode = baris["kode_bps"]
    semua_tahun = lebar[lebar["kode_bps"] == kode].sort_values("tahun")

    def peringkat_dari(metrik: str, terbesar: bool = True) -> int:
        return int(analisis.peringkat(th, metrik, terbesar=terbesar).set_index("kode_bps").loc[kode, "peringkat"])

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Pendapatan", rupiah(baris["pendapatan"]), f"peringkat {peringkat_dari('pendapatan')} dari 38", delta_color="off")
    c2.metric("Belanja", rupiah(baris["belanja"]), f"peringkat {peringkat_dari('belanja')} dari 38", delta_color="off")
    c3.metric("Belanja per penduduk", rupiah(baris["belanja_per_kapita"], 2),
              f"peringkat {peringkat_dari('belanja_per_kapita')} dari 38", delta_color="off")
    c4.metric("Kemandirian fiskal", persen(baris["kemandirian"]),
              f"peringkat {peringkat_dari('kemandirian')} dari 38", delta_color="off")
    c5.metric("Penduduk (jiwa)", f"{angka_id(baris['penduduk'] / 1e6, 2)} juta", f"{baris['pulau']}", delta_color="off")

    st.subheader(f"Aliran uang {prov} {tahun} ({basis})")
    s = analisis.aliran_sankey(apbd, kode, tahun, basis=basis)
    if s["nilai"]:
        warna_simpul = []
        for nama in s["label"]:
            if nama == "Kas Daerah":
                warna_simpul.append("#444444")
            elif nama.startswith("Belanja"):
                warna_simpul.append("#d95f02")
            else:
                warna_simpul.append("#1b9e77")
        sankey = go.Figure(go.Sankey(
            arrangement="snap",
            node=dict(label=s["label"], pad=18, thickness=16, color=warna_simpul),
            link=dict(source=s["sumber"], target=s["tujuan"], value=s["nilai"],
                      customdata=[rupiah(v) for v in s["nilai"]],
                      hovertemplate="%{source.label} → %{target.label}<br>%{customdata}<extra></extra>",
                      color="rgba(150,150,150,0.35)"),
        ))
        st.plotly_chart(grafik_rapi(sankey, 520), use_container_width=True)
        st.caption("Kiri: dari mana uang datang. Tengah: kas daerah. Kanan: untuk apa uang dipakai. "
                   "Lebar pita sebanding dengan jumlah rupiah.")
    else:
        st.warning("Tidak ada data untuk kombinasi provinsi dan tahun ini.")

    kiri, kanan = st.columns(2)
    with kiri:
        st.subheader("Anggaran vs realisasi belanja")
        jenis = apbd[(apbd["kode_bps"] == kode) & (apbd["tahun"] == tahun) & (apbd["induk"] == "Belanja Daerah")]
        panjang = jenis.melt(id_vars="akun", value_vars=["anggaran", "realisasi"], var_name="basis", value_name="nilai")
        fig = px.bar(panjang, x="akun", y="nilai", color="basis", barmode="group",
                     color_discrete_map={"anggaran": "#bbbbbb", "realisasi": "#d95f02"})
        fig.update_layout(xaxis_title="", yaxis_title="Rupiah")
        st.plotly_chart(grafik_rapi(fig, 380), use_container_width=True)
    with kanan:
        st.subheader("Komposisi belanja vs rata-rata nasional")
        banding = pd.DataFrame({
            "jenis": ["Pegawai", "Barang & Jasa", "Modal", "Lainnya"],
            prov: [baris["porsi_pegawai"], baris["porsi_barang"], baris["porsi_modal"], baris["porsi_lainnya"]],
            "Nasional": [nasional["porsi_pegawai"],
                         th["belanja_barang"].sum() / th["belanja"].sum() * 100,
                         nasional["porsi_modal"],
                         th["belanja_lainnya"].sum() / th["belanja"].sum() * 100],
        }).melt(id_vars="jenis", var_name="wilayah", value_name="porsi")
        fig = px.bar(banding, x="jenis", y="porsi", color="wilayah", barmode="group",
                     color_discrete_map={prov: "#1b9e77", "Nasional": "#bbbbbb"})
        fig.update_layout(xaxis_title="", yaxis_title="% dari total belanja")
        st.plotly_chart(grafik_rapi(fig, 380), use_container_width=True)

    if len(semua_tahun) > 1:
        st.subheader(f"Perjalanan {prov} {semua_tahun['tahun'].min()}–{semua_tahun['tahun'].max()}")
        tren = semua_tahun.melt(id_vars="tahun", value_vars=["pendapatan", "belanja", "pad", "tkdd"],
                                var_name="indikator", value_name="nilai")
        nama_ind = {"pendapatan": "Pendapatan", "belanja": "Belanja", "pad": "PAD", "tkdd": "Transfer pusat"}
        tren["indikator"] = tren["indikator"].map(nama_ind)
        fig = px.line(tren, x="tahun", y="nilai", color="indikator", markers=True)
        fig.update_layout(xaxis=dict(tickmode="array", tickvals=TAHUN_TERSEDIA), yaxis_title="Rupiah", xaxis_title="")
        st.plotly_chart(grafik_rapi(fig, 340), use_container_width=True)

    if mode_belajar:
        with st.expander("🎓 Struktur APBD dalam satu halaman"):
            st.markdown(
                """
                APBD selalu punya tiga blok besar:

                | Blok | Isi | Pertanyaan yang dijawab |
                |---|---|---|
                | **Pendapatan** | PAD (pajak, retribusi, BUMD), transfer dari pusat (TKD), pendapatan lainnya | Dari mana uangnya? |
                | **Belanja** | Pegawai, barang & jasa, modal, lainnya (bagi hasil, bantuan keuangan, hibah, bansos) | Untuk apa uangnya? |
                | **Pembiayaan** | SiLPA tahun lalu, pinjaman, penyertaan modal | Bagaimana selisihnya ditutup? |

                Diagram Sankey di atas hanya menggambar dua blok pertama. Jika pita kiri lebih lebar dari pita
                kanan, daerah itu surplus (atau belanjanya belum terserap); jika sebaliknya, kekurangannya ditutup
                dari blok pembiayaan, biasanya SiLPA.

                **Kemandirian fiskal** = PAD ÷ Pendapatan × 100 %. Nilai nasional sekitar 30 %; DKI Jakarta di atas
                70 %, sementara banyak provinsi di luar Jawa di bawah 15 %.
                """
            )

# ---------------------------------------------------------------- tab perbandingan
with tab_banding:
    st.subheader("Siapa mandiri, siapa bergantung, siapa membelanjakan paling banyak per orang?")
    skala_log = st.checkbox("Sumbu belanja per penduduk dalam skala logaritmik", value=True)
    fig = px.scatter(
        th, x="belanja_per_kapita", y="kemandirian", size="penduduk", color="pulau", hover_name="provinsi",
        color_discrete_map=WARNA_PULAU, size_max=55, log_x=skala_log,
        hover_data={"belanja_per_kapita": ":,.0f", "kemandirian": ":.1f", "penduduk": ":,.0f", "pulau": False},
        labels={"belanja_per_kapita": "Belanja per penduduk (Rp)", "kemandirian": "Kemandirian fiskal (%)", "penduduk": "Penduduk"},
    )
    fig.add_hline(y=nasional["kemandirian"], line_dash="dot", line_color="#888",
                  annotation_text=f"Nasional {persen(nasional['kemandirian'])}", annotation_position="top left")
    fig.add_vline(x=nasional["belanja_per_kapita"], line_dash="dot", line_color="#888",
                  annotation_text=f"Nasional {rupiah(nasional['belanja_per_kapita'], 2)}", annotation_position="top right")
    st.plotly_chart(grafik_rapi(fig, 520), use_container_width=True)
    st.caption("Ukuran lingkaran = jumlah penduduk. Kanan atas: kaya dan mandiri. Kanan bawah: belanja per orang "
               "tinggi tetapi hampir seluruhnya dari pusat. Kiri bawah: belanja per orang kecil dan bergantung pada pusat.")

    st.subheader("Komposisi belanja setiap provinsi")
    urutkan = st.selectbox("Urutkan menurut porsi", ["Modal", "Pegawai", "Barang & Jasa"], index=0)
    komposisi = analisis.komposisi_belanja(th)
    kunci_urut = {"Modal": "porsi_modal", "Pegawai": "porsi_pegawai", "Barang & Jasa": "porsi_barang"}[urutkan]
    urutan = th.sort_values(kunci_urut, ascending=False)["provinsi"].tolist()
    fig = px.bar(komposisi, x="porsi", y="provinsi", color="jenis", orientation="h",
                 category_orders={"provinsi": urutan, "jenis": list(WARNA_BELANJA)},
                 color_discrete_map=WARNA_BELANJA)
    fig.update_layout(xaxis_title="% dari total belanja", yaxis_title="", barmode="stack", legend=dict(orientation="h", y=-0.08))
    st.plotly_chart(grafik_rapi(fig, 820), use_container_width=True)

    st.subheader("Per pulau besar")
    pulau = analisis.agregat_pulau(th).sort_values("belanja", ascending=False)
    tampil = pd.DataFrame({
        "Pulau": pulau["pulau"],
        "Penduduk": pulau["penduduk"].map(orang),
        "Pendapatan": pulau["pendapatan"].map(rupiah),
        "Belanja": pulau["belanja"].map(rupiah),
        "Belanja per penduduk": pulau["belanja_per_kapita"].map(lambda v: rupiah(v, 2)),
        "Kemandirian fiskal": pulau["kemandirian"].map(persen),
        "Porsi belanja modal": pulau["porsi_modal"].map(persen),
    })
    st.dataframe(tampil, hide_index=True, use_container_width=True)

    if mode_belajar:
        with st.expander("🎓 Mengapa per kapita dan skala log?"):
            st.markdown(
                """
                - **Per kapita** menjawab "berapa rupiah untuk setiap warga", bukan "berapa rupiah untuk provinsi".
                  Rp 14 triliun untuk 1,5 juta penduduk Papua Pegunungan berarti sekitar Rp 10 juta per orang;
                  Rp 144 triliun untuk 50 juta penduduk Jawa Barat hanya sekitar Rp 2,8 juta per orang.
                - **Skala logaritmik** memberi jarak yang sama untuk setiap kelipatan 10. Tanpa skala log, provinsi
                  dengan belanja per kapita Rp 2–4 juta akan menumpuk di pojok kiri dan sulit dibedakan.
                - **Ukuran lingkaran** dipetakan ke luas, bukan jari-jari (`size` di Plotly Express), supaya lingkaran
                  dua kali penduduk tampak dua kali lebih besar, bukan empat kali.
                """
            )

# ---------------------------------------------------------------- tab tren
with tab_tren:
    st.subheader("Perubahan 2022 → 2024")
    metrik_tren = st.selectbox("Indikator", options=list(analisis.METRIK),
                               format_func=lambda k: analisis.METRIK[k].nama, index=0, key="metrik_tren")
    m_tren = analisis.METRIK[metrik_tren]
    bawaan = analisis.peringkat(th, metrik_tren, n=6)["provinsi"].tolist()
    pilih_prov = st.multiselect("Provinsi", sorted(lebar["provinsi"].unique()), default=bawaan)
    data_tren = lebar[lebar["provinsi"].isin(pilih_prov)]
    fig = px.line(data_tren, x="tahun", y=metrik_tren, color="provinsi", markers=True)
    fig.update_layout(xaxis=dict(tickmode="array", tickvals=TAHUN_TERSEDIA), xaxis_title="", yaxis_title=m_tren.nama)
    st.plotly_chart(grafik_rapi(fig, 460), use_container_width=True)

    st.subheader("Siapa yang tumbuh paling cepat?")
    kolom_tumbuh = st.radio("Pertumbuhan", ["belanja", "pendapatan", "pad", "tkdd"], horizontal=True,
                            format_func=lambda k: {"belanja": "Belanja", "pendapatan": "Pendapatan", "pad": "PAD", "tkdd": "Transfer pusat"}[k])
    tumbuh = analisis.tambah_pertumbuhan(lebar, kolom_tumbuh)
    tumbuh_th = tumbuh[(tumbuh["tahun"] == tahun)].dropna(subset=[f"pertumbuhan_{kolom_tumbuh}"])
    if tumbuh_th.empty:
        st.info("Pertumbuhan membutuhkan tahun sebelumnya. Pilih tahun yang lebih baru di sidebar.")
    else:
        fig = px.bar(tumbuh_th.sort_values(f"pertumbuhan_{kolom_tumbuh}"), x=f"pertumbuhan_{kolom_tumbuh}", y="provinsi",
                     orientation="h", color="pulau", color_discrete_map=WARNA_PULAU)
        fig.update_layout(xaxis_title=f"Pertumbuhan {kolom_tumbuh} {tahun - 1}→{tahun} (%)", yaxis_title="")
        st.plotly_chart(grafik_rapi(fig, 760), use_container_width=True)
        st.caption("Lonjakan atau penurunan tajam pada provinsi di Papua tahun 2023 mencerminkan pemekaran wilayah, "
                   "bukan perubahan kebijakan fiskal.")

    st.subheader("Potret nasional per jenis belanja")
    nas = lebar.groupby("tahun", as_index=False)[["belanja_pegawai", "belanja_barang", "belanja_modal", "belanja_lainnya"]].sum()
    nas = nas.melt(id_vars="tahun", var_name="jenis", value_name="nilai")
    nas["jenis"] = nas["jenis"].map({"belanja_pegawai": "Pegawai", "belanja_barang": "Barang & Jasa",
                                     "belanja_modal": "Modal", "belanja_lainnya": "Lainnya (bagi hasil, bankeu, hibah, bansos)"})
    fig = px.area(nas, x="tahun", y="nilai", color="jenis", color_discrete_map=WARNA_BELANJA)
    fig.update_layout(xaxis=dict(tickmode="array", tickvals=TAHUN_TERSEDIA), xaxis_title="", yaxis_title="Rupiah")
    st.plotly_chart(grafik_rapi(fig, 380), use_container_width=True)

# ---------------------------------------------------------------- tab data
with tab_data:
    st.subheader(f"Tabel indikator per provinsi, {tahun} ({basis})")
    kolom_tampil = ["provinsi", "pulau", "penduduk", "pendapatan", "pad", "tkdd", "belanja", "belanja_pegawai",
                    "belanja_barang", "belanja_modal", "belanja_lainnya", "belanja_per_kapita", "kemandirian",
                    "ketergantungan", "porsi_modal", "porsi_pegawai", "serapan_belanja", "capaian_pendapatan"]
    st.dataframe(
        th[kolom_tampil].sort_values("belanja", ascending=False),
        hide_index=True, use_container_width=True, height=520,
        column_config={
            "penduduk": st.column_config.NumberColumn("Penduduk", format="localized"),
            **{k: st.column_config.NumberColumn(k, format="localized") for k in
               ["pendapatan", "pad", "tkdd", "belanja", "belanja_pegawai", "belanja_barang", "belanja_modal",
                "belanja_lainnya", "belanja_per_kapita"]},
            **{k: st.column_config.NumberColumn(k, format="%.1f %%") for k in
               ["kemandirian", "ketergantungan", "porsi_modal", "porsi_pegawai", "serapan_belanja", "capaian_pendapatan"]},
        },
    )
    u1, u2 = st.columns(2)
    u1.download_button("⬇️ Unduh tabel indikator (CSV)", lebar.to_csv(index=False).encode("utf-8"),
                       file_name="indikator_apbd_provinsi.csv", mime="text/csv")
    u2.download_button("⬇️ Unduh data mentah per akun (CSV)", apbd.to_csv(index=False).encode("utf-8"),
                       file_name="apbd_provinsi.csv", mime="text/csv")

    st.subheader("Rincian akun")
    prov_data = st.selectbox("Provinsi", sorted(apbd["provinsi"].unique()), key="prov_data")
    rinci = apbd[(apbd["provinsi"] == prov_data) & (apbd["tahun"] == tahun)].copy()
    rinci["akun"] = rinci.apply(lambda r: ("    " * (r["tingkat"] - 1)) + label(r["akun"]), axis=1)
    rinci["% realisasi"] = (rinci["realisasi"] / rinci["anggaran"].where(rinci["anggaran"] != 0) * 100).round(1)
    st.dataframe(rinci[["akun", "anggaran", "realisasi", "% realisasi"]], hide_index=True, use_container_width=True,
                 column_config={"anggaran": st.column_config.NumberColumn(format="localized"),
                                "realisasi": st.column_config.NumberColumn(format="localized")})

    st.subheader("Sumber dan keterbatasan")
    st.markdown(muat_data.muat_sumber())

# ---------------------------------------------------------------- tab cara kerja
with tab_cara:
    st.markdown(
        """
        ### Dari portal pemerintah sampai peta

        ```
        Portal SIKD DJPK ──(XML per provinsi & tahun)──▶ scripts/unduh_djpk.py
                                                             │  rapikan: tingkat akun, alias, buang ganda
                                                             ▼
                                                  data/apbd_provinsi.csv  (3.600 baris)
                                                             │
        data/penduduk_provinsi.csv ───────────▶ src/analisis.tabel_lebar() ──▶ 38 provinsi × 3 tahun × indikator
        data/provinsi.geojson ────────────────▶ src/peta.buat_peta()        ──▶ choropleth Folium
                                                             │
                                                             ▼
                                                        app.py (Streamlit)
        ```

        ### Rumus yang dipakai

        | Indikator | Rumus |
        |---|---|
        | Belanja per penduduk | Belanja Daerah ÷ Penduduk |
        | Kemandirian fiskal | PAD ÷ Pendapatan Daerah × 100 % |
        | Ketergantungan pada pusat | TKD ÷ Pendapatan Daerah × 100 % |
        | Porsi belanja modal | Belanja Modal ÷ Belanja Daerah × 100 % |
        | Serapan belanja | Realisasi Belanja ÷ Anggaran Belanja × 100 % |
        | Pertumbuhan | (Nilai tahun ini ÷ Nilai tahun lalu − 1) × 100 % |

        ### Mengapa agregat per provinsi?

        Portal DJPK memungkinkan pemilihan satu pemda saja, tetapi membandingkan APBD *pemprov* antar provinsi
        bisa menyesatkan: di provinsi tertentu urusan dan uang lebih banyak berada di kabupaten/kota. Menjumlahkan
        semua pemda dalam satu provinsi memberi gambaran "berapa uang publik yang beredar di wilayah ini",
        yang lebih adil untuk peta.

        ### Yang perlu diwaspadai

        - Transfer antar daerah (pemprov → kab/kota) tercatat dua kali dalam agregat: sebagai belanja pemprov dan pendapatan kab/kota.
        - Penduduk memakai proyeksi 2025 untuk semua tahun.
        - Realisasi adalah angka yang dilaporkan pemda ke SIKD, belum tentu sama dengan laporan keuangan yang diaudit.
        - Papua 2022 masih provinsi induk sebelum pemekaran; tren 2022→2023 untuk Papua dan Papua Barat tidak dapat dibandingkan langsung.

        Bacaan lebih lanjut: `docs/BELAJAR.md` (konsep) dan `docs/LATIHAN.md` (soal latihan).
        """
    )
