import streamlit as st
import database as db
import pandas as pd
import fpdf

# Sayfa Ayarları
st.set_page_config(page_title="Diyet Portalı", page_icon="🍏", layout="wide")

# Güvenlik: Admin Girişi
def check_password():
    """Sadece doğru şifre girildiğinde panellere erişim sağlar."""
    def password_entered():
        if st.session_state["password"] == "senaarıman2004": # Buradaki admin123 şifresini istediğin gibi değiştirebilirsin
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Güvenlik için şifreyi hafızadan sil
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.title("🔒 Diyet Portalı - Yönetici Girişi")
        st.text_input("Lütfen yönetici şifrenizi girin", type="password", key="password", on_change=password_entered)
        return False
    
    elif not st.session_state["password_correct"]:
        st.title("🔒 Diyet Portalı - Yönetici Girişi")
        st.text_input("Lütfen yönetici şifrenizi girin", type="password", key="password", on_change=password_entered)
        st.error("😕 Yanlış şifre. Lütfen tekrar deneyin.")
        return False
    
    return True

# Şifre doğruysa ana uygulamayı çalıştır
# Şifre doğruysa ana uygulamayı çalıştır
if check_password():
    
    # --- ÜST BİLGİ VE MENÜ (SOL VE SAĞ YERLEŞİM) ---
    header_col1, header_col2 = st.columns([4, 6]) # Ekranı %40 Sol, %60 Sağ olarak böldük
    
    with header_col1:
        # En sol üste büyük başlık
        st.markdown("<h1 style='margin-top: -20px;'>🍏 Diyet Portalı</h1>", unsafe_allow_html=True)
        
    with header_col2:
        # Menüyü sağ üste hizalamak için ufak bir boşluk
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        # Yatay seçim menüsü
        secili_panel = st.radio(
            "Menü",
            ["📚 Besin Veritabanı", "📁 Danışanlar", "✍️ Diyet Yazma", "🧮 BMI & Kalori"],
            horizontal=True,
            label_visibility="collapsed"
        )
        
    st.markdown("---") # Panelleri ayıran ince çizgi
    
    # --- 1. PANEL: BESİN VERİTABANI ---
    if secili_panel == "📚 Besin Veritabanı":
        st.header("Besin Veritabanı Yönetimi")
        
        def clear_food_inputs():
            keys = ["f_name", "f_cat", "f_meal", "f_unit", "f_cal", "f_pro", "f_fat", "f_carb", "f_allergens", "f_notes"]
            for key in keys:
                if key in st.session_state:
                    del st.session_state[key]

        with st.expander("➕ Yeni Besin / Tarif Ekle", expanded=True):
            col1, col2, col3 = st.columns(3)
            f_name = col1.text_input("Besin Adı*", key="f_name")
            f_cat = col2.selectbox("Kategori", ["Protein", "Karbonhidrat", "Yağ", "Sebze", "Meyve", "Süt Ürünü", "İçecek", "Tarifler", "Diğer"], key="f_cat")
            f_meal = col3.selectbox("Öğün", ["Hepsi", "Sabah", "Öğle", "Akşam", "Ara Öğün"], key="f_meal")
            
            col4, col5, col6, col7 = st.columns(4)
            f_unit = col4.text_input("Birim*", key="f_unit")
            f_cal = col5.text_input("Kalori", value="0", key="f_cal")
            f_pro = col6.text_input("Protein", value="0", key="f_pro")
            f_fat = col7.text_input("Yağ", value="0", key="f_fat")
            
            f_carb = st.text_input("Karbonhidrat", value="0", key="f_carb")
            f_allergens = st.text_input("Alerjenler", key="f_allergens") # Parantezi kaldırdık
            
            if f_cat == "Tarifler":
                f_notes = st.text_area("📝 Tarifin Hazırlanışı", key="f_notes")
            else:
                f_notes = st.text_area("Özel Notlar", key="f_notes")
            
            if st.button("Besini Kaydet", type="primary"):
                if f_name and f_unit:
                    cal_val = int(f_cal) if f_cal.isdigit() else 0
                    pro_val = int(f_pro) if f_pro.isdigit() else 0
                    fat_val = int(f_fat) if f_fat.isdigit() else 0
                    carb_val = int(f_carb) if f_carb.isdigit() else 0
                    
                    db.add_food(f_name, f_cat, f_meal, f_unit, cal_val, pro_val, fat_val, carb_val, f_allergens, f_notes)
                    st.success(f"✅ '{f_name}' başarıyla kaydedildi!")
                    clear_food_inputs()
                    st.rerun()
                else:
                    st.error("Lütfen Besin Adı ve Birim alanlarını doldurun.")

        st.subheader("Mevcut Besinler")
        foods_df = db.get_all_foods()
        
        if not foods_df.empty:
            display_df = foods_df.copy()
            display_df[['calories', 'protein', 'fat', 'carbs']] = display_df[['calories', 'protein', 'fat', 'carbs']].astype(int)
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            with st.expander("✏️ Besin Düzenle veya Sil"):
                edit_food_name = st.selectbox("İşlem Yapılacak Besini Seçin", foods_df['name'].tolist())
                
                if edit_food_name:
                    selected_food = foods_df[foods_df['name'] == edit_food_name].iloc[0]
                    
                    st.markdown(f"**{edit_food_name}** için yeni değerleri girin:")
                    e_col1, e_col2, e_col3 = st.columns(3)
                    e_name = e_col1.text_input("Yeni Ad", value=selected_food['name'])
                    
                    categories = ["Protein", "Karbonhidrat", "Yağ", "Sebze", "Meyve", "Süt Ürünü", "İçecek", "Tarifler", "Diğer"]
                    default_cat_index = categories.index(selected_food['category']) if selected_food['category'] in categories else 8
                    e_cat = e_col2.selectbox("Yeni Kategori", categories, index=default_cat_index)
                    
                    meals = ["Hepsi", "Sabah", "Öğle", "Akşam", "Ara Öğün"]
                    default_meal_index = meals.index(selected_food['meal_time']) if selected_food['meal_time'] in meals else 0
                    e_meal = e_col3.selectbox("Yeni Öğün", meals, index=default_meal_index)
                    
                    e_col4, e_col5, e_col6, e_col7 = st.columns(4)
                    e_unit = e_col4.text_input("Yeni Birim", value=selected_food['unit'])
                    e_cal = e_col5.text_input("Kalori", value=str(int(selected_food['calories'])))
                    e_pro = e_col6.text_input("Protein", value=str(int(selected_food['protein'])))
                    e_fat = e_col7.text_input("Yağ", value=str(int(selected_food['fat'])))
                    
                    e_carb = st.text_input("Karbonhidrat", value=str(int(selected_food['carbs'])))
                    e_notes = st.text_area("Tarif / Not", value=selected_food['notes'] if selected_food['notes'] else "")
                    
                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        if st.button("💾 Güncelle", type="primary", use_container_width=True):
                            db.update_food(
                                selected_food['id'], e_name, e_cat, e_meal, e_unit,
                                int(e_cal) if e_cal.isdigit() else 0,
                                int(e_pro) if e_pro.isdigit() else 0,
                                int(e_fat) if e_fat.isdigit() else 0,
                                int(e_carb) if e_carb.isdigit() else 0,
                                selected_food['allergens'], e_notes
                            )
                            st.success("✅ Besin güncellendi!")
                            st.rerun()
                            
                    with btn_col2:
                        if st.button("🗑️ Besini Sil", use_container_width=True):
                            db.delete_food(selected_food['id'])
                            st.warning(f"⚠️ {edit_food_name} silindi.")
                            st.rerun()
        else:
            st.info("Veritabanında henüz besin yok.")

    # --- 2. PANEL: DANIŞANLAR ---
    elif secili_panel == "📁 Danışanlar":
        st.header("Danışan Arşivi")
        with st.form("add_client_form"):
            col1, col2 = st.columns([8, 2])
            with col1:
                c_name = st.text_input("Yeni Danışan Adı Soyadı")
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                c_submitted = st.form_submit_button("Danışan Ekle")
            
            if c_submitted:
                if c_name:
                    success = db.add_client(c_name.strip())
                    if success:
                        st.success(f"✅ {c_name} sisteme eklendi!")
                        st.rerun()
                    else:
                        st.error("⚠️ Bu isimde bir danışan zaten kayıtlı.")
                else:
                    st.error("Lütfen bir isim girin.")
        
        st.markdown("---")
        st.subheader("Kayıtlı Danışanlar")
        clients_df = db.get_all_clients()
        
        if not clients_df.empty:
            for index, row in clients_df.iterrows():
                with st.expander(f"📁 {row['name']}"):
                    st.write(f"**Danışan ID:** {row['id']}")
                    st.info("Bu danışanın geçmiş diyet listeleri oluşturulduğunda burada listelenecek.")
                    st.button("Diyet Yaz", key=f"write_diet_{row['id']}") 
        else:
            st.info("Henüz kayıtlı danışan bulunmuyor. Yukarıdan ekleyebilirsiniz.")

    # --- 3. PANEL: DİYET YAZMA ---
    elif secili_panel == "✍️ Diyet Yazma":
        st.header("Yeni Diyet Listesi")
        if 'diet_cart' not in st.session_state:
            st.session_state.diet_cart = []

        col1, col2 = st.columns([6, 4])
        
        with col1:
            st.subheader("🔍 Besin Seçimi ve Filtreleme")
            foods_df = db.get_all_foods()
            
            if not foods_df.empty:
                foods_df[['calories', 'protein', 'fat', 'carbs']] = foods_df[['calories', 'protein', 'fat', 'carbs']].astype(float)
                
                with st.expander("⚙️ Detaylı Filtreleme Seçenekleri", expanded=False):
                    f_col1, f_col2 = st.columns(2)
                    
                    cat_list = ["Hepsi"] + foods_df['category'].dropna().unique().tolist()
                    meal_list = ["Hepsi"] + foods_df['meal_time'].dropna().unique().tolist()
                    
                    s_cat = f_col1.selectbox("Kategori", cat_list)
                    s_meal = f_col2.selectbox("Öğün", meal_list)
                    
                    st.markdown("---")
                    
                    st.markdown("""
                        <style>
                        .stSlider > div[data-baseweb="slider"] > div > div > div {
                            background-color: white !important;
                        }
                        .stSlider > div[data-baseweb="slider"] div[role="slider"] {
                            background-color: white !important;
                            border: 2px solid #ddd !important;
                        }
                        </style>
                    """, unsafe_allow_html=True)
                    
                    m_col1, m_col2 = st.columns(2)
                    s_cal = m_col1.slider("Kalori Aralığı", 0.0, 9999.0, (0.0, 9999.0))
                    s_pro = m_col1.slider("Protein Aralığı (g)", 0.0, 999.0, (0.0, 999.0))
                    s_fat = m_col2.slider("Yağ Aralığı (g)", 0.0, 999.0, (0.0, 999.0))
                    s_carb = m_col2.slider("Karb. Aralığı (g)", 0.0, 999.0, (0.0, 999.0))
                    
                    st.markdown("---")
                    
                    allergen_options = ["Gluten", "Süt", "Yumurta", "Mısır"]
                    s_allergens = st.multiselect("🚫 Bu Alerjenleri İçerenleri Çıkar:", allergen_options)

                filtered_df = foods_df.copy()
                
                search_term = st.text_input("Besin Ara ")
                if search_term:
                    filtered_df = filtered_df[filtered_df['name'].str.contains(search_term, case=False, na=False)]
                    
                if s_cat != "Hepsi":
                    filtered_df = filtered_df[filtered_df['category'] == s_cat]
                if s_meal != "Hepsi":
                    filtered_df = filtered_df[filtered_df['meal_time'] == s_meal]
                    
                filtered_df = filtered_df[
                    (filtered_df['calories'] >= s_cal[0]) & (filtered_df['calories'] <= s_cal[1]) &
                    (filtered_df['protein'] >= s_pro[0]) & (filtered_df['protein'] <= s_pro[1]) &
                    (filtered_df['fat'] >= s_fat[0]) & (filtered_df['fat'] <= s_fat[1]) &
                    (filtered_df['carbs'] >= s_carb[0]) & (filtered_df['carbs'] <= s_carb[1])
                ]
                
                if s_allergens:
                    pattern = '|'.join(s_allergens) 
                    filtered_df = filtered_df[~filtered_df['allergens'].str.contains(pattern, case=False, na=False)]
                
                display_cols = ['name', 'category', 'meal_time', 'calories', 'protein', 'fat', 'carbs', 'allergens']
                renamed_df = filtered_df[display_cols].rename(columns={
                    'name': 'Besin', 'category': 'Kategori', 'meal_time': 'Öğün',
                    'calories': 'Kalori', 'protein': 'Protein', 'fat': 'Yağ', 'carbs': 'Karb', 'allergens': 'Alerjen'
                })
                
                st.write(f"**Bulunan Besin Sayısı:** {len(filtered_df)}")
                st.dataframe(renamed_df, use_container_width=True, hide_index=True)
                
                with st.form("add_to_cart_form"):
                    st.write("**Besini Listeye Ekle**")
                    if not filtered_df.empty:
                        selected_food = st.selectbox("Besin Seçin", filtered_df['name'].tolist())
                        meal_type = st.selectbox("Hangi Öğün?", ["Sabah", "Ara Öğün 1", "Öğlen", "Ara Öğün 2", "Akşam", "Gece"])
                        amount = st.number_input("Miktar Çarpanı", min_value=0.1, step=0.5, value=1.0)
                        add_btn = st.form_submit_button("Listeye Ekle")
                        
                        if add_btn and selected_food:
                            food_data = filtered_df[filtered_df['name'] == selected_food].iloc[0]
                            st.session_state.diet_cart.append({
                                'Öğün': meal_type,
                                'Besin': food_data['name'],
                                'Miktar': amount,
                                'Kalori': food_data['calories'] * amount,
                                'Protein': food_data['protein'] * amount,
                                'Yağ': food_data['fat'] * amount,
                                'Karb': food_data['carbs'] * amount
                            })
                            st.success(f"✅ {selected_food} ({meal_type}) listeye eklendi!")
                            st.rerun()
                    else:
                        st.warning("Seçtiğiniz filtrelere uygun besin bulunamadı.")
                        st.form_submit_button("Listeye Ekle", disabled=True)
            else:
                st.warning("⚠️ Önce 1. Panelden veri tabanına birkaç besin eklemelisiniz.")

        with col2:
            # Görsel sıralamayı kilitlemek için 3 ayrı "Konteyner" (Kutu) oluşturuyoruz
            progress_container = st.container()
            target_container = st.container()
            cart_container = st.container()
            
            # --- 2. KUTU (ORTA): HEDEF BELİRLEME GİRDİLERİ ---
            with target_container:
                st.markdown("#### 🎯 Hedef Belirleme")
                h_col1, h_col2, h_col3, h_col4 = st.columns(4)
                hedef_kalori = h_col1.number_input("Kalori", min_value=500, max_value=10000, value=2000, step=100)
                hedef_karb_y = h_col2.number_input("Karb %", min_value=0, max_value=100, value=50, step=5)
                hedef_pro_y = h_col3.number_input("Pro %", min_value=0, max_value=100, value=20, step=5)
                hedef_yag_y = h_col4.number_input("Yağ %", min_value=0, max_value=100, value=30, step=5)
                
                # Yüzde kontrolü
                toplam_yuzde = hedef_karb_y + hedef_pro_y + hedef_yag_y
                if toplam_yuzde != 100:
                    st.error(f"⚠️ Makro yüzdeleri toplamı 100 olmalıdır! (Şu an: {toplam_yuzde})")
                
                st.markdown("---")
                
            # Hedef Gramajları Matematiksel Olarak Hesaplama (1g Karb=4, 1g Pro=4, 1g Yağ=9 kcal)
            hedef_karb_gr = (hedef_kalori * (hedef_karb_y / 100)) / 4
            hedef_pro_gr = (hedef_kalori * (hedef_pro_y / 100)) / 4
            hedef_yag_gr = (hedef_kalori * (hedef_yag_y / 100)) / 9

            # Sepet Verilerini Toplama
            total_cal, total_pro, total_fat, total_carb = 0.0, 0.0, 0.0, 0.0
            if len(st.session_state.diet_cart) > 0:
                cart_df = pd.DataFrame(st.session_state.diet_cart)
                total_cal = cart_df['Kalori'].sum()
                total_pro = cart_df['Protein'].sum()
                total_fat = cart_df['Yağ'].sum()
                total_carb = cart_df['Karb'].sum()

            # Sepetin Şu Anki Yüzdelerini Hesaplama
            mevcut_karb_y = (total_carb * 4 / total_cal * 100) if total_cal > 0 else 0
            mevcut_pro_y = (total_pro * 4 / total_cal * 100) if total_cal > 0 else 0
            mevcut_yag_y = (total_fat * 9 / total_cal * 100) if total_cal > 0 else 0

            # --- 1. KUTU (ÜST): CANLI İLERLEME ÇUBUKLARI ---
            with progress_container:
                st.markdown("#### 📊 Canlı Makro Takibi")
                
                # Kalori Çubuğu
                cal_oran = min(total_cal / hedef_kalori, 1.0) if hedef_kalori > 0 else 0
                st.markdown(f"**Kalori:** {total_cal:.0f} / {hedef_kalori} kcal")
                st.progress(cal_oran)
                
                # Makro Çubukları
                p_col1, p_col2, p_col3 = st.columns(3)
                with p_col1:
                    karb_oran = min(total_carb / hedef_karb_gr, 1.0) if hedef_karb_gr > 0 else 0
                    st.markdown(f"<span style='font-size: 14px;'>🍞 **Karb:** {total_carb:.0f}g / {hedef_karb_gr:.0f}g</span>", unsafe_allow_html=True)
                    st.markdown(f"<span style='font-size: 12px; color: gray;'>Güncel Liste: **%{mevcut_karb_y:.0f}**</span>", unsafe_allow_html=True)
                    st.progress(karb_oran)
                    
                with p_col2:
                    pro_oran = min(total_pro / hedef_pro_gr, 1.0) if hedef_pro_gr > 0 else 0
                    st.markdown(f"<span style='font-size: 14px;'>🥩 **Pro:** {total_pro:.0f}g / {hedef_pro_gr:.0f}g</span>", unsafe_allow_html=True)
                    st.markdown(f"<span style='font-size: 12px; color: gray;'>Güncel Liste: **%{mevcut_pro_y:.0f}**</span>", unsafe_allow_html=True)
                    st.progress(pro_oran)
                    
                with p_col3:
                    yag_oran = min(total_fat / hedef_yag_gr, 1.0) if hedef_yag_gr > 0 else 0
                    st.markdown(f"<span style='font-size: 14px;'>🥑 **Yağ:** {total_fat:.0f}g / {hedef_yag_gr:.0f}g</span>", unsafe_allow_html=True)
                    st.markdown(f"<span style='font-size: 12px; color: gray;'>Güncel Liste: **%{mevcut_yag_y:.0f}**</span>", unsafe_allow_html=True)
                    st.progress(yag_oran)
                
                st.markdown("<br>", unsafe_allow_html=True) # Araya ufak bir boşluk atıyoruz

            # --- 3. KUTU (ALT): SEPET VE PDF BUTONLARI ---
            with cart_container:
                if len(st.session_state.diet_cart) > 0:
                    st.markdown("#### 🛒 Sepetteki Besinler")
                    st.dataframe(cart_df[['Öğün', 'Besin', 'Miktar', 'Kalori']], use_container_width=True, hide_index=True)
                    
                    st.markdown("##### Ürün Sil")
                    del_col1, del_col2 = st.columns([7, 3])
                    
                    with del_col1:
                        cart_options = [f"{i} - {row['Besin']} ({row['Öğün']})" for i, row in enumerate(st.session_state.diet_cart)]
                        item_to_delete = st.selectbox("Silinecek ürünü seçin:", cart_options, label_visibility="collapsed")
                        
                    with del_col2:
                        if st.button("🗑️ Sil", use_container_width=True):
                            idx = int(item_to_delete.split(" - ")[0])
                            st.session_state.diet_cart.pop(idx)
                            st.rerun()

                    st.markdown("---")
                    
                    # --- PDF FONKSİYONU ---
                    def create_pdf(cart_data, foods_dataframe):
                        def tr_char(text):
                            if not isinstance(text, str): return str(text)
                            tr_map = {'ş':'s', 'Ş':'S', 'ı':'i', 'İ':'I', 'ğ':'g', 'Ğ':'G', 'ü':'u', 'Ü':'U', 'ö':'o', 'Ö':'O', 'ç':'c', 'Ç':'C'}
                            for k, v in tr_map.items(): text = text.replace(k, v)
                            return text

                        pdf = fpdf.FPDF()
                        pdf.add_page()
                        
                        pdf.set_font("Arial", 'B', 11)
                        pdf.cell(0, 5, txt=tr_char("Sena Afacan"), ln=True, align='R')
                        pdf.set_font("Arial", 'I', 10)
                        pdf.cell(0, 5, txt="senafacan45@gmail.com", ln=True, align='R')
                        pdf.ln(10) 
                        
                        pdf.set_font("Arial", 'B', 18)
                        pdf.cell(0, 10, txt=tr_char("DIYET LISTESI"), ln=True, align='C')
                        pdf.ln(10)
                        
                        meals_order = ["Sabah", "Ara Öğün 1", "Öğlen", "Ara Öğün 2", "Akşam", "Gece"]
                        recipes = []
                        
                        for meal in meals_order:
                            meal_items = [item for item in cart_data if item['Öğün'] == meal]
                            if meal_items:
                                pdf.set_font("Arial", 'B', 14)
                                pdf.cell(0, 10, txt=tr_char(meal), ln=True, align='L')
                                
                                pdf.set_font("Arial", '', 12)
                                for item in meal_items:
                                    miktar = item['Miktar']
                                    miktar_str = f"{int(miktar)}" if miktar.is_integer() else f"{miktar}"
                                    text_line = f"- {tr_char(item['Besin'])} ({miktar_str} Porsiyon/Adet/Birim)"
                                    pdf.cell(0, 8, txt=text_line, ln=True, align='L')
                                    
                                    food_info = foods_dataframe[foods_dataframe['name'] == item['Besin']]
                                    if not food_info.empty:
                                        if food_info.iloc[0]['category'] == 'Tarifler' and food_info.iloc[0]['notes']:
                                            recipes.append({'name': item['Besin'], 'recipe': food_info.iloc[0]['notes']})
                                pdf.ln(5)
                                
                        if recipes:
                            pdf.add_page()
                            pdf.set_font("Arial", 'B', 11)
                            pdf.cell(0, 5, txt=tr_char("Sena Afacan"), ln=True, align='R')
                            pdf.set_font("Arial", 'I', 10)
                            pdf.cell(0, 5, txt="senafacan45@gmail.com", ln=True, align='R')
                            pdf.ln(10)
                            for r in recipes:
                                pdf.set_font("Arial", 'B', 14)
                                pdf.cell(0, 8, txt=f"{tr_char(r['name'])} Tarifi", ln=True, align='L')
                                pdf.set_font("Arial", '', 12)
                                pdf.multi_cell(0, 8, txt=tr_char(r['recipe']))
                                pdf.ln(8)
                                
                        return pdf.output(dest='S').encode('latin-1')

                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.button("Tüm Sepeti Temizle", use_container_width=True):
                            st.session_state.diet_cart = []
                            st.rerun()
                    with col_btn2:
                        pdf_bytes = create_pdf(st.session_state.diet_cart, foods_df)
                        st.download_button(label="📄 PDF Olarak Kaydet", data=pdf_bytes, file_name="diyet_listesi.pdf", mime="application/pdf", use_container_width=True, type="primary")
                else:
                    st.info("Sepetiniz şu an boş. Sol taraftaki listeden öğünlerinize besin eklemeye başlayın.")

                # --- 4. PANEL: BMI & KALORİ HESAPLAYICI ---
    elif secili_panel == "🧮 BMI & Kalori":
        st.header("🧮 BMI & Kalori Hesaplayıcı")
        
        # Temizle butonu için session_state ayarları
        if 'bmi_cinsiyet' not in st.session_state:
            st.session_state.bmi_cinsiyet = "Kadın"
            st.session_state.bmi_yas = 25
            st.session_state.bmi_boy = 165
            st.session_state.bmi_kilo = 65.0
            
        def formu_temizle():
            st.session_state.bmi_cinsiyet = "Kadın"
            st.session_state.bmi_yas = 25
            st.session_state.bmi_boy = 165
            st.session_state.bmi_kilo = 65.0
            if 'hesaplandi' in st.session_state:
                del st.session_state['hesaplandi']

        # Girdi Alanları
        col1, col2 = st.columns(2)
        with col1:
            cinsiyet = st.radio("Cinsiyet", ["Kadın", "Erkek"], key="bmi_cinsiyet", horizontal=True)
            yas = st.number_input("Yaş", min_value=1, max_value=120, key="bmi_yas")
        with col2:
            boy = st.number_input("Boy (cm)", min_value=50, max_value=250, key="bmi_boy")
            kilo = st.number_input("Kilo (kg)", min_value=10.0, max_value=300.0, step=0.1, key="bmi_kilo")

        # Butonlar
        btn_col1, btn_col2 = st.columns([2, 1])
        with btn_col1:
            hesapla = st.button("🧮 Hesapla", use_container_width=True, type="primary")
        with btn_col2:
            temizle = st.button("🧹 Temizle", use_container_width=True, on_click=formu_temizle)

        if hesapla:
            st.session_state.hesaplandi = True

        st.markdown("---")

        # Sonuç Ekranı
        if st.session_state.get('hesaplandi', False):
            # 1. BMI Hesaplama
            boy_m = boy / 100
            bmi = kilo / (boy_m ** 2)
            
            # Kategori ve Renk Belirleme (WHO Standardı)
            if bmi < 16:
                kategori, renk = "İleri Derece Zayıflık", "#d32f2f" 
            elif 16 <= bmi < 17:
                kategori, renk = "Orta Derece Zayıflık", "#ffb74d" 
            elif 17 <= bmi < 18.5:
                kategori, renk = "Hafif Zayıflık", "#ff9800" 
            elif 18.5 <= bmi < 25:
                kategori, renk = "Normal Kilo", "#4caf50" 
            elif 25 <= bmi < 30:
                kategori, renk = "Fazla Kilolu", "#ff9800" 
            elif 30 <= bmi < 35:
                kategori, renk = "1. Derece Obezite", "#ffb74d" 
            elif 35 <= bmi < 40:
                kategori, renk = "2. Derece Obezite", "#d32f2f" 
            else:
                kategori, renk = "3. Derece Obezite", "#d32f2f" 

            # BMI Sonucunu Renkli Kutuda Gösterme
            st.markdown(f"""
                <div style="background-color: {renk}; padding: 20px; border-radius: 10px; color: white; text-align: center; margin-bottom: 20px;">
                    <h2 style="margin:0; color: white;">BMI Değeriniz: {bmi:.1f}</h2>
                    <h4 style="margin:0; margin-top:5px; color: white;">({kategori})</h4>
                </div>
            """, unsafe_allow_html=True)

            # 2. Kalori (Bazal Metabolizma) Hesaplama
            if cinsiyet == "Erkek":
                mifflin = (10 * kilo) + (6.25 * boy) - (5 * yas) + 5
                harris = 66.5 + (13.75 * kilo) + (5 * boy) - (6.77 * yas)
            else:
                mifflin = (10 * kilo) + (6.25 * boy) - (5 * yas) - 161
                harris = 655.1 + (9.56 * kilo) + (1.85 * boy) - (4.67 * yas)

            # Kalori Sonuçlarını Gösterme
            # Kalori Sonuçlarını Gösterme
            st.markdown(f"""
<div style="background-color: rgba(128, 128, 128, 0.1); padding: 20px; border-radius: 10px; text-align: center;">
<h3 style="margin-top: 0; margin-bottom: 15px;">🔥 Bazal Metabolizma Hızı (BMH)</h3>
<div style="margin-bottom: 15px;">
<span style="font-size: 28px; font-weight: bold;">{mifflin:.0f} kcal</span><br>
<span style="font-size: 14px; font-style: italic; opacity: 0.8;">(Mifflin-St Jeor Formülü)</span>
</div>
<div>
<span style="font-size: 28px; font-weight: bold;">{harris:.0f} kcal</span><br>
<span style="font-size: 14px; font-style: italic; opacity: 0.8;">(Harris-Benedict Formülü)</span>
</div>
</div>
""", unsafe_allow_html=True)