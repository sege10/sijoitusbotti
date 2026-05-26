import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from crewai import Agent, Crew, Task
from crewai_tools import SerperDevTool

st.set_page_config(page_title="SEGE10 AI-Salkunhoitaja", layout="wide")
st.sidebar.title("🤖 SEGE10 AI-Keskus")
valinta = st.sidebar.radio("Työkalu:", ["📈 Sijoitusagentti", "💼 Salkunhoitaja", "⛽ Bensavahti"])

# --- SALKUNHOITAJA-SIMULAATTORI ---
if valinta == "💼 Salkunhoitaja":
    st.title("💼 AI-Salkunhoitaja (Simulaattori)")
    st.write("Toimin kuin pankkisi sijoitusneuvoja. Annan sinulle konkreettisen allokaatioehdotuksen.")
    
    riski = st.select_slider("Valitse riskinsietokykysi:", ["Varovainen (Korkoa/Indeksiä)", "Tasapainoinen (60/40)", "Kasvuhakuinen (Osakkeet/Tech)"])
    summa = st.number_input("Sijoitettava summa (€):", value=5000, step=500)
    
    if st.button("Luo salkkuehdotus"):
        with st.spinner("Analysoidaan markkinaa ja rakennetaan salkkua..."):
            salkunhoitaja = Agent(
                role="Pankin Senior Salkunhoitaja",
                goal="Rakentaa optimaalinen ja hajautettu salkku annetulla riskitasolla.",
                backstory="Olet kokenut salkunhoitaja. Käytät sijoitusstrategioissa modernia portfolioteoriaa. Ehdotat vain todellisia omaisuusluokkia (esim. S&P 500, Valtionlainat, Teknologiaosakkeet).",
                verbose=True
            )
            
            task = Task(
                description=f"""Asiakkaan sijoitussumma on {summa} euroa ja riskitaso on {riski}.
                1. Määritä prosentuaalinen jako eri omaisuusluokkien kesken.
                2. Anna 4-5 konkreettista esimerkkiä sijoituskohteista (esim. ETF-rahastot, indeksit).
                3. Perustele, miksi tämä allokaatio toimii valitsemallasi riskitasolla.
                4. Listaa sijoitusten painotukset (€-määräisesti).""",
                expected_output="Asiantunteva salkkusuunnitelma perusteluineen.",
                agent=salkunhoitaja
            )
            
            crew = Crew(agents=[salkunhoitaja], tasks=[task], verbose=True)
            tulos = crew.kickoff()
            st.markdown("---")
            st.write(str(tulos))
            st.info("Huom: Tämä on simulaatio. Ennen oikeita sijoituspäätöksiä, keskustele aina pankkisi sijoitusasiantuntijan kanssa.")

# --- BENSAVAHTI (Nopea) ---
elif valinta == "⛽ Bensavahti":
    st.title("⛽ Bensavahti (Helsinki)")
    if st.button("Hae päivän hinnat"):
        try:
            res = requests.get("https://www.polttoaine.net/Helsinki", headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            t = soup.find("table", {"id": "LisaaHintojaTable"})
            data = [{"Asema": r.find_all("td")[0].text.strip(), "95E10": r.find_all("td")[2].text.strip(), "Diesel": r.find_all("td")[4].text.strip()} for r in t.find_all("tr")[2:12]]
            st.table(pd.DataFrame(data))
        except: st.error("Ei yhteyttä palveluun.")

# --- SIJOITUSAGENTTI (Konkreettinen) ---
elif valinta == "📈 Sijoitusagentti":
    st.title("📈 Sijoitusagentti")
    kohde = st.text_input("Analysoitava kohde (esim. Nokia, Neste):")
    if st.button("Analysoi"):
        a = Agent(role="Analyytikko", goal="Anna tunnusluvut ja osta/myy suositus.", tools=[SerperDevTool()])
        t = Task(description=f"Etsi {kohde}. Ilmoita sen kurssi, P/E-luku ja anna perusteltu suositus.", expected_output="Analyysiraportti.", agent=a)
        st.write(str(Crew(agents=[a], tasks=[t]).kickoff()))
