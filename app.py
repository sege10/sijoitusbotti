import streamlit as st
import os
from crewai import Agent, Crew, Task
from crewai_tools import SerperDevTool

# Asetukset
os.environ["OPENAI_API_KEY"] = st.secrets.get("OPENAI_API_KEY", "")
os.environ["SERPER_API_KEY"] = st.secrets.get("SERPER_API_KEY", "")

st.set_page_config(page_title="SEGE10 Keskus", layout="wide")
valinta = st.sidebar.radio("Työkalu:", ["📈 Sijoitusagentti", "💼 Salkunhoitaja", "📖 Liiketaloussanasto", "⛽ Bensavahti"])

# --- 1. SIJOITUSAGENTTI ---
if valinta == "📈 Sijoitusagentti":
    st.title("📈 Sijoitusagentti")
    kohde = st.text_input("Syötä yrityksen nimi:")
    if st.button("Käynnistä tekoälyanalyysi"):
        with st.spinner("Agentti tutkii markkinaa..."):
            try:
                search_tool = SerperDevTool()
                agent = Agent(role="Sijoitusanalyytikko", goal="Anna tarkka analyysi ja sijoitussuositus.", backstory="Olet ammattimainen pörssianalyytikko.", tools=[search_tool])
                task = Task(description=f"Etsi {kohde} kurssitiedot, tunnusluvut ja anna perusteltu Osta/Myy-suositus.", expected_output="Analyysiraportti", agent=agent)
                result = Crew(agents=[agent], tasks=[task]).kickoff()
                st.write(str(result))
            except Exception as e:
                st.error(f"Agentti-virhe: {e}")

# --- 2. SALKUNHOITAJA ---
elif valinta == "💼 Salkunhoitaja":
    st.title("💼 Salkunhoitaja")
    summa = st.number_input("Sijoitettava summa (€):", value=1000)
    riski = st.select_slider("Riski:", ["Varovainen", "Tasapainoinen", "Kasvuhakuinen"])
    if st.button("Luo salkkuehdotus"):
        agent = Agent(role="Senior Salkunhoitaja", goal="Rakenna optimaalinen salkku.", backstory="Olet kokenut pankin salkunhoitaja.")
        task = Task(description=f"Luo {riski}-riskitason salkku {summa} eurolle. Listaa konkreettiset kohteet.", expected_output="Salkkuehdotus", agent=agent)
        st.write(str(Crew(agents=[agent], tasks=[task]).kickoff()))

# --- 3. LIIKETALOUSSANASTO (Hakukentällä) ---
elif valinta == "📖 Liiketaloussanasto":
    st.title("📖 Liiketaloussanasto")
    sanasto = {
        "liikevaihto": "Yrityksen myyntien yhteenlaskettu arvo tiettynä aikana.",
        "käyttökate": "EBITDA. Kertoo operatiivisen toiminnan kannattavuudesta ennen poistoja.",
        "inbound": "Myyntitapa, jossa asiakas löytää yrityksen itse.",
        "roi": "Sijoitetun pääoman tuotto-prosentti.",
        "likviditeetti": "Yrityksen kyky maksaa lyhytaikaiset velat heti.",
        "tase": "Yrityksen varojen ja velkojen tila tiettynä ajanhetkenä."
    }
    haku = st.text_input("Kirjoita termi (esim. liikevaihto):").lower()
    if haku:
        if haku in sanasto:
            st.success(f"**{haku.capitalize()}**: {sanasto[haku]}")
        else:
            st.error("Termiä ei löytynyt.")

# --- 4. BENSAVAHTI (Suora linkki) ---
elif valinta == "⛽ Bensavahti":
    st.title("⛽ Bensavahti")
    st.link_button("Hae Uudenmaan bensahinnat tästä", "https://www.polttoaine.net/Uusimaa")
