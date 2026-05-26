import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from crewai import Agent, Crew, Task
from crewai_tools import SerperDevTool

# Sivun perusasetukset
st.set_page_config(page_title="SEGE10 AI-Keskus", layout="wide")
st.sidebar.title("🤖 SEGE10 AI-Keskus")
st.sidebar.write("📅 Päivämäärä: 26.5.2026")
valinta = st.sidebar.radio("Valitse työkalu:", ["📈 Sijoitusagentti", "⚽ Pitkäveto-agentti", "⛽ Bensavahti", "💼 Salkunhoitaja"])

# --- 1. SIJOITUSAGENTTI ---
if valinta == "📈 Sijoitusagentti":
    st.title("📈 Sijoitusagentti")
    kohde = st.text_input("Analysoitava kohde (esim. Nokia, Neste, BTC):")
    if st.button("Käynnistä analyysi"):
        a = Agent(role="Analyytikko", goal="Anna tunnusluvut ja sijoitussuositus.", tools=[SerperDevTool()])
        t = Task(description=f"Etsi {kohde}. Ilmoita sen kurssi, P/E-luku ja anna perusteltu suositus.", expected_output="Analyysiraportti.", agent=a)
        st.write(str(Crew(agents=[a], tasks=[t]).kickoff()))

# --- 2. PITKÄVETO-AGENTTI ---
elif valinta == "⚽ Pitkäveto-agentti":
    st.title("⚽ AI-Pitkävetoagentti")
    ottelu = st.text_input("Syötä ottelu (esim. Suomi - Sveitsi):")
    kertoimet = st.text_input("Syötä kertoimet (esim. 1: 2.50, X: 3.30, 2: 2.90):")
    if st.button("Käynnistä analyysi"):
        agent = Agent(role="Ammattivedonlyöjä", goal="Valita voittaja ja perustella analyysi.", tools=[SerperDevTool()])
        task = Task(description=f"Ottelu: {ottelu}, Kertoimet: {kertoimet}. Analysoi, valitse 1, X tai 2 ja perustele.", expected_output="Pelivalinta ja perustelut.", agent=agent)
        st.write(str(Crew(agents=[agent], tasks=[task]).kickoff()))

# --- 3. BENSAVAHTI ---
elif valinta == "⛽ Bensavahti":
    st.title("⛽ Bensavahti (Helsinki)")
    if st.button("Hae hinnat"):
        try:
            res = requests.get("https://www.polttoaine.net/Helsinki", headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(res.text, 'html.parser')
            t = soup.find("table", {"id": "LisaaHintojaTable"})
            data = [{"Asema": r.find_all("td")[0].text.strip(), "95E10": r.find_all("td")[2].text.strip(), "Diesel": r.find_all("td")[4].text.strip()} for r in t.find_all("tr")[2:12]]
            st.table(pd.DataFrame(data))
        except: st.error("Ei yhteyttä palveluun.")

# --- 4. SALKUNHOITAJA ---
elif valinta == "💼 Salkunhoitaja":
    st.title("💼 AI-Salkunhoitaja (Simulaattori)")
    riski = st.select_slider("Riski:", ["Varovainen", "Tasapainoinen", "Kasvuhakuinen"])
    summa = st.number_input("Summa (€):", value=5000)
    if st.button("Luo salkkuehdotus"):
        agent = Agent(role="Salkunhoitaja", goal="Rakenna salkku.", backstory="Olet pankin asiantuntija.")
        task = Task(description=f"Luo {riski}-salkku {summa} eurolle. 4-5 kohdetta ja eurosummat.", expected_output="Salkkuehdotus.", agent=agent)
        st.write(str(Crew(agents=[agent], tasks=[task]).kickoff()))
