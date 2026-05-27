import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from crewai import Agent, Crew, Task
from crewai_tools import SerperDevTool

# 1. BENSAVAHTI (Uusimaa-laajennus)
def hae_bensahinnat_uusimaa():
    try:
        # Polttoaine.netin Uusimaa-sivu
        url = "https://www.polttoaine.net/Uusimaa"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        taulukko = soup.find("table", {"id": "LisaaHintojaTable"})
        data = []
        for r in taulukko.find_all("tr")[2:20]: # 18 tuoreinta Uudeltamaalta
            s = r.find_all("td")
            if len(s) > 4:
                data.append({"Asema": s[0].text.strip(), "95E10": s[2].text.strip(), "Diesel": s[4].text.strip()})
        return pd.DataFrame(data)
    except: return None

# 2. APP-RAKENNE
st.set_page_config(page_title="SEGE:n AI-Keskus", layout="wide")
valinta = st.sidebar.radio("Työkalu:", ["📈 Sijoitusagentti", "⚽ Pitkäveto", "⛽ Bensavahti (Uusimaa)", "💼 Salkunhoitaja"])

if valinta == "⛽ Bensavahti (Uusimaa)":
    st.title("⛽ Bensavahti: Uusimaa")
    if st.button("Päivitä Uudenmaan hinnat"):
        df = hae_bensahinnat_uusimaa()
        if df is not None: st.table(df)
        else: st.error("Ei yhteyttä polttoaine.netiin.")

elif valinta == "📈 Sijoitusagentti":
    st.title("📈 Sijoitusagentti")
    kohde = st.text_input("Kohde:")
    if st.button("Analysoi"):
        try:
            agent = Agent(role="Analyytikko", goal="Analysoi kohde.", backstory="Olet ammattilainen.", tools=[SerperDevTool()])
            task = Task(description=f"Etsi {kohde} kurssi ja analysoi.", expected_output="Lyhyt raportti.", agent=agent)
            st.write(str(Crew(agents=[agent], tasks=[task]).kickoff()))
        except Exception as e: st.error(f"Agentti-virhe: {e}. (Tarkista API-avaimet!)")

elif valinta == "⚽ Pitkäveto":
    st.title("⚽ Pitkäveto")
    o = st.text_input("Ottelu:")
    if st.button("Analysoi"):
        try:
            agent = Agent(role="Vedonlyöjä", goal="Valitse voittaja.", backstory="Analysoija.", tools=[SerperDevTool()])
            task = Task(description=f"Ottelu {o} analyysi.", expected_output="Tulos.", agent=agent)
            st.write(str(Crew(agents=[agent], tasks=[task]).kickoff()))
        except Exception as e: st.error("Pitkäveto-agentti tarvitsee toimivat API-avaimet.")

elif valinta == "💼 Salkunhoitaja":
    st.title("💼 Salkunhoitaja")
    # Salkunhoitaja toimii ilman ulkoisia API-hakuja, siksi se on vakaa
    riski = st.select_slider("Riski:", ["Varovainen", "Tasapainoinen", "Kasvuhakuinen"])
    if st.button("Luo salkku"):
        agent = Agent(role="Salkunhoitaja", goal="Rakenna salkku.", backstory="Pankin asiantuntija.")
        task = Task(description=f"Luo {riski}-salkku.", expected_output="Salkku.", agent=agent)
        st.write(str(Crew(agents=[agent], tasks=[task]).kickoff()))
