import streamlit as st
import os
import yfinance as yf
from pycoingecko import CoinGeckoAPI
from crewai import Agent, Crew, Task
from crewai_tools import SerperDevTool

# Asetukset
os.environ["OPENAI_API_KEY"] = st.secrets.get("OPENAI_API_KEY", "")
os.environ["SERPER_API_KEY"] = st.secrets.get("SERPER_API_KEY", "")
cg = CoinGeckoAPI()
search_tool = SerperDevTool()

st.set_page_config(page_title="SEGE10 Keskus", layout="wide")
st.sidebar.title("🤖 SEGE10 Keskus")
valinta = st.sidebar.radio("Työkalu:", ["📈 Sijoitusagentti", "💼 Salkunhoitaja", "📖 Liiketaloussanasto", "⚽ Veikkaus", "⛽ Bensavahti"])

# --- 1. SIJOITUSAGENTTI (Tarkka haku) ---
if valinta == "📈 Sijoitusagentti":
    st.title("📈 Sijoitusagentti")
    kohde = st.text_input("Syötä kohde (esim. Bitcoin, Nokia):")
    if st.button("Hae reaaliaikainen analyysi"):
        with st.spinner("Agentti hakee ajantasaisen markkinahinnan..."):
            try:
                agent = Agent(
                    role="Talousanalyytikko",
                    goal="Etsi kohteen {kohde} tämän hetken hinta euroissa ja anna sijoitussuositus.",
                    backstory="Olet tarkka analyytikko, joka etsii vain uusimmat markkinatiedot.",
                    tools=[search_tool]
                )
                task = Task(
                    description=f"Etsi Googlen avulla: Mikä on {kohde} kurssi euroissa juuri nyt? Anna sen perusteella Osta/Pidä/Myy -suositus.",
                    expected_output="Raportti, jossa lukee hinta euroissa ja analyytikon suositus.",
                    agent=agent
                )
                result = Crew(agents=[agent], tasks=[task]).kickoff()
                st.write(str(result))
            except Exception as e:
                st.error(f"Haku epäonnistui: {e}")

# --- 2. SALKUNHOITAJA (Päivitetty 2026 markkinatilanteeseen) ---
elif valinta == "💼 Salkunhoitaja":
    st.title("💼 Salkunhoitaja (Toukokuu 2026)")
    summa = st.number_input("Sijoitettava summa (€):", value=1000)
    
    if st.button("Luo vuoden 2026 salkkuehdotus"):
        st.write("### Markkinanäkymä 2026:")
        st.write("""
        * **Tekoäly (AI):** Siirrytty sovellusten käyttöön, paino teollisuusautomaatiossa.
        * **Korkotaso:** Vakaampi, suosii yrityksiä, joilla on vahva kassavirta.
        * **Energia:** Vetytalous ja energian varastointi korostuvat.
        """)
        
        # Salkun hajautus 2026 tyyliin
        data = {
            "Sektori": ["AI-Infrastruktuuri", "Vety & Energian varastointi", "Kulutustavarat (Vakaat)", "Kyberturvallisuus", "Käteinen/Lyhyet korot"],
            "Painotus": ["25%", "25%", "20%", "20%", "10%"],
            "Summa (€)": [f"{summa*0.25:.0f}", f"{summa*0.25:.0f}", f"{summa*0.2:.0f}", f"{summa*0.2:.0f}", f"{summa*0.1:.0f}"]
        }
        st.table(pd.DataFrame(data))

# --- 3. LIIKETALOUSSANASTO ---
elif valinta == "📖 Liiketaloussanasto":
    st.title("📖 Liiketaloussanasto")
    term = st.text_input("Etsi termiä (esim. liikevaihto):")
    if st.button("Hae määritelmä"):
        agent = Agent(role="Opettaja", goal="Selitä termi.", backstory="Taloustieteen professori.", tools=[search_tool])
        task = Task(description=f"Selitä lyhyesti ja selkeästi termi: {term}.", expected_output="Määritelmä.", agent=agent)
        st.write(str(Crew(agents=[agent], tasks=[task]).kickoff()))

# --- 4. VEIKKAUSASIANTUNTIJA ---
elif valinta == "⚽ Veikkaus":
    st.title("⚽ Veikkausasiantuntija")
    ottelu = st.text_input("Ottelu:")
    if st.button("Analysoi ottelu"):
        agent = Agent(role="Vedonlyöjä", goal="Valitse voittaja.", backstory="Vedonlyönnin ammattilainen.", tools=[search_tool])
        task = Task(description=f"Analysoi ottelu {ottelu} ja anna pelivalinta (1X2).", expected_output="Analyysi.", agent=agent)
        st.write(str(Crew(agents=[agent], tasks=[task]).kickoff()))

# --- 5. BENSAVAHTI ---
elif valinta == "⛽ Bensavahti":
    st.title("⛽ Bensavahti")
    if st.button("Hae päivän trendit"):
        agent = Agent(role="Bensavahti", goal="Tarkista bensan hinnan kehitys.", backstory="Analyytikko.", tools=[search_tool])
        task = Task(description="Etsi tämän hetken bensan hintatrendit Uudellamaalla.", expected_output="Raportti.", agent=agent)
        st.write(str(Crew(agents=[agent], tasks=[task]).kickoff()))
        st.link_button("Katso tarkat hinnat (Polttoaine.net)", "https://www.polttoaine.net/Uusimaa")
