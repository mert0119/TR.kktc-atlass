import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import math

# --- 1. SAYFA AYARLARI ---
st.set_page_config(layout="wide", page_title="Türkiye Hibrit Atlası")

# --- 2. VERİ TABANI (Detaylı) ---
veriler = {
    "Denizler": [
        # [İsim, Enlem, Boylam, Sıcaklık, Derinlik]
        ["Artvin / Hopa", 41.40, 41.42, 15.5, 2212],
        ["Trabzon Limanı", 41.01, 39.75, 15.8, 2212],
        ["Sinop Limanı", 42.02, 35.15, 14.9, 2212],
        ["Bartın / Amasra", 41.63, 32.38, 14.6, 2000],
        ["Kocaeli / Kefken", 41.17, 30.26, 14.2, 2212],
        ["İstanbul / Boğaz", 41.00, 28.97, 14.5, 60],
        ["Çanakkale Boğazı", 40.14, 26.40, 16.5, 70],
        ["İzmir / Çeşme", 38.32, 26.30, 19.2, 80],
        ["Muğla / Bodrum", 37.03, 27.42, 21.2, 100],
        ["Muğla / Marmaris", 36.85, 28.27, 22.0, 120],
        ["Muğla / Fethiye", 36.54, 29.12, 22.8, 4000],
        ["Antalya Limanı", 36.83, 30.60, 24.2, 200],
        ["Mersin Limanı", 36.79, 34.64, 25.2, 50],
        ["Hatay / İskenderun", 36.59, 36.17, 24.5, 40],
        ["KKTC / Girne", 35.34, 33.32, 25.5, 200]
    ],
    "Dağlar": [
        # [İsim, Enlem, Boylam, Yükseklik]
        ["Ağrı Dağı", 39.70, 44.29, 5137],
        ["Erciyes Dağı", 38.54, 35.45, 3917],
        ["Uludağ", 40.06, 29.22, 2543],
        ["Kaz Dağı", 39.70, 26.85, 1774],
        ["Kaçkar Dağı", 40.83, 41.16, 3932]
    ],
    "Göller": [
        # [İsim, Enlem, Boylam, Özellik]
        ["Van Gölü", 38.62, 42.90, "Sodalı / En Büyük"],
        ["Tuz Gölü", 38.83, 33.33, "Tuzlu"],
        ["Salda Gölü", 37.55, 29.67, "Tatlı / Turistik"],
        ["Abant Gölü", 40.60, 31.27, "Tatlı / Tabiat Parkı"]
    ],
    "Tarihi Yerler": [
        # [İsim, Enlem, Boylam, Bilgi]
        ["Göbeklitepe", 37.22, 38.92, "Tarihin Sıfır Noktası"],
        ["Efes Antik Kenti", 37.94, 27.34, "Antik Roma Başkenti"],
        ["Anıtkabir", 39.92, 32.83, "Ulu Önder'in Kabri"]
    ]
}

# Veri Birleştirme
tum_veriler = []
for kat, liste in veriler.items():
    for i in liste:
        tum_veriler.append({"İsim": i[0], "Enlem": i[1], "Boylam": i[2], "Kategori": kat})
df_all = pd.DataFrame(tum_veriler)

# --- 3. FONKSİYONLAR ---
def mesafe_hesapla(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) * math.sin(dlat / 2) + \
        math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
        math.sin(dlon / 2) * math.sin(dlon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# --- 4. ARAYÜZ ---
st.sidebar.title("🗺️ Türkiye Hibrit Atlası")
mod = st.sidebar.radio("Mod Seçiniz:", 
    ["🗺️ Harita Keşfi", "🚗 Kara Yolu (Yakıt)", "🚢 Deniz Yolu (Seyir)", "⚖️ Dağ vs Deniz Analizi"])

st.title(f"Mod: {mod}")

# ==========================================
# MOD 1: HARİTA KEŞFİ (DETAYLAR GERİ GELDİ! ✅)
# ==========================================
if mod == "🗺️ Harita Keşfi":
    katman = st.selectbox("Görünüm:", ["Sokak", "Uydu", "Karanlık"])
    m = folium.Map(location=[39.0, 35.0], zoom_start=6)
    
    if katman == "Uydu": folium.TileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', attr='Esri').add_to(m)
    elif katman == "Karanlık": folium.TileLayer('CartoDB dark_matter').add_to(m)

    for kat, liste in veriler.items():
        for item in liste:
            isim, lat, lon = item[0], item[1], item[2]
            detay = item[3] # 4. eleman (Sıcaklık/Yükseklik/Tür/Bilgi)
            
            # Kategorilere göre ÖZEL ayarlar
            if kat == "Denizler":
                derinlik = item[4] # Denizlerde 5. eleman derinliktir
                sicaklik = detay
                
                # Sıcaklığa göre renk
                if sicaklik >= 24: color, icon = "red", "fire"
                elif sicaklik >= 20: color, icon = "orange", "thumbs-up"
                else: color, icon = "blue", "anchor"
                
                # DETAYLI POPUP
                popup_text = f"<b>{isim}</b><br>🌡️ {sicaklik}°C<br>📉 Derinlik: {derinlik}m"

            elif kat == "Dağlar":
                yukseklik = detay
                if yukseklik >= 5000: color, icon = "black", "star"
                else: color, icon = "gray", "arrow-up"
                
                popup_text = f"<b>{isim}</b><br>⛰️ Yükseklik: {yukseklik}m"

            elif kat == "Göller":
                tur = detay
                color, icon = "cadetblue", "tint"
                popup_text = f"<b>{isim}</b><br>💧 Özellik: {tur}"

            else: # Tarih
                bilgi = detay
                color, icon = "purple", "camera"
                popup_text = f"<b>{isim}</b><br>🏛️ {bilgi}"

            # Haritaya Ekle
            folium.Marker(
                [lat, lon], 
                popup=popup_text, 
                tooltip=isim,
                icon=folium.Icon(color=color, icon=icon, prefix="fa")
            ).add_to(m)
    
    st_folium(m, width=1000, height=500)

# ==========================================
# MOD 2: KARA YOLU & YAKIT (HAFIZALI 🧠)
# ==========================================
elif mod == "🚗 Kara Yolu (Yakıt)":
    if 'kara_sonuc' not in st.session_state: st.session_state['kara_sonuc'] = None

    st.info("Aracınızla yapacağınız yolculuğun maliyetini hesaplayın.")

    c1, c2 = st.columns(2)
    with c1: baslangic = st.selectbox("Başlangıç:", df_all["İsim"].unique())
    with c2: bitis = st.selectbox("Varış:", df_all["İsim"].unique())

    st.markdown("---")
    c3, c4 = st.columns(2)
    with c3: tuketim = st.number_input("Ortalama Tüketim (Litre/100km):", 3.0, 20.0, 7.0)
    with c4: fiyat = st.number_input("Yakıt Litre Fiyatı (TL):", 20.0, 60.0, 42.0)

    if st.button("Maliyeti Hesapla 💸"):
        if baslangic == bitis:
            st.warning("Aynı yeri seçtiniz.")
        else:
            p1 = df_all[df_all["İsim"] == baslangic].iloc[0]
            p2 = df_all[df_all["İsim"] == bitis].iloc[0]
            
            kus_ucusu = mesafe_hesapla(p1["Enlem"], p1["Boylam"], p2["Enlem"], p2["Boylam"])
            yol_mesafesi = kus_ucusu * 1.3 
            toplam_yakit = (yol_mesafesi / 100) * tuketim
            toplam_tutar = toplam_yakit * fiyat

            st.session_state['kara_sonuc'] = {
                "rota": f"{baslangic} ➡️ {bitis}",
                "km": int(yol_mesafesi),
                "litre": toplam_yakit,
                "tl": int(toplam_tutar)
            }

    if st.session_state['kara_sonuc']:
        res = st.session_state['kara_sonuc']
        st.success(f"Rota: **{res['rota']}**")
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Tahmini Yol", f"{res['km']} km")
        col_b.metric("Yakıt", f"{res['litre']:.1f} Litre")
        col_c.metric("Tutar", f"{res['tl']} TL")

# ==========================================
# MOD 3: DENİZ YOLU & SEYİR (HAFIZALI 🧠)
# ==========================================
elif mod == "🚢 Deniz Yolu (Seyir)":
    if 'deniz_sonuc' not in st.session_state: st.session_state['deniz_sonuc'] = None

    st.info("Tekneyle iki liman arasındaki seyir süresini hesaplayın.")

    deniz_isimleri = [item[0] for item in veriler["Denizler"]]
    c1, c2 = st.columns(2)
    with c1: baslangic = st.selectbox("⚓ Kalkış Limanı:", deniz_isimleri, index=4) 
    with c2: bitis = st.selectbox("🏁 Varış Limanı:", deniz_isimleri, index=2) 

    st.markdown("---")
    hiz_knot = st.number_input("Tekne Hızı (Knot):", 5.0, 50.0, 15.0)
    
    if st.button("Seyir Planı Oluştur 🧭"):
        if baslangic == bitis:
            st.warning("Aynı limandasınız!")
        else:
            p1 = df_all[df_all["İsim"] == baslangic].iloc[0]
            p2 = df_all[df_all["İsim"] == bitis].iloc[0]
            
            mesafe_km = mesafe_hesapla(p1["Enlem"], p1["Boylam"], p2["Enlem"], p2["Boylam"])
            mesafe_mil = mesafe_km / 1.852
            sure_saat = mesafe_mil / hiz_knot
            
            st.session_state['deniz_sonuc'] = {
                "start": baslangic, "end": bitis,
                "nm": mesafe_mil, "km": mesafe_km, "saat": sure_saat,
                "p1": p1, "p2": p2
            }

    if st.session_state['deniz_sonuc']:
        d_res = st.session_state['deniz_sonuc']
        st.success(f"Rota: **{d_res['start']}** ➡️ **{d_res['end']}**")
        
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Mesafe (NM)", f"{d_res['nm']:.1f} NM")
        col_b.metric("Mesafe (Km)", f"{d_res['km']:.1f} km")
        col_c.metric("Süre", f"{d_res['saat']:.1f} Saat ⏱️")

        m_rota = folium.Map(location=[(d_res['p1']["Enlem"]+d_res['p2']["Enlem"])/2, (d_res['p1']["Boylam"]+d_res['p2']["Boylam"])/2], zoom_start=6)
        folium.Marker([d_res['p1']["Enlem"], d_res['p1']["Boylam"]], icon=folium.Icon(color="green", icon="play")).add_to(m_rota)
        folium.Marker([d_res['p2']["Enlem"], d_res['p2']["Boylam"]], icon=folium.Icon(color="red", icon="stop")).add_to(m_rota)
        folium.PolyLine([(d_res['p1']["Enlem"], d_res['p1']["Boylam"]), (d_res['p2']["Enlem"], d_res['p2']["Boylam"])], color="blue", weight=3, dash_array='10').add_to(m_rota)
        st_folium(m_rota, width=1000, height=450)

# ==========================================
# MOD 4: ANALİZ
# ==========================================
elif mod == "⚖️ Dağ vs Deniz Analizi":
    st.write("Simülasyon Modu: Dağları denizlere batırıyoruz.")
    dag_sec = st.selectbox("Dağ:", [d[0] for d in veriler["Dağlar"]])
    deniz_sec = st.selectbox("Deniz:", [d[0] for d in veriler["Denizler"]])
    
    if st.button("Simüle Et"):
        d_veri = next(d for d in veriler["Dağlar"] if d[0] == dag_sec)
        s_veri = next(s for s in veriler["Denizler"] if s[0] == deniz_sec)
        
        yuk, der = d_veri[3], s_veri[4]
        fark = yuk - der
        
        st.bar_chart(pd.DataFrame({"Metre": [yuk, -der]}, index=[dag_sec, deniz_sec]))
        if fark > 0: st.success(f"Sonuç: **{dag_sec}**, **{fark}m** farkla su üstünde kalır! 🏝️")
        else: st.error(f"Sonuç: **{dag_sec}** tamamen batar! 🌊")