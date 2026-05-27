import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from crewai import Agent, Crew, Task

# Sivun asetukset
st.set_page_config(page_title="SEGE10 AI-Keskus", layout="wide")
st.sidebar.title("🤖 SEGE10 AI-Keskus")
valinta = st.sidebar.radio("Valitse työkalu:", ["📈 Sijoitusagentti", "⚽ Pitkäveto", "⛽ Bensavahti (Uusimaa)", "💼 Salkunhoitaja"])

# --- 1. SIJOITUSAGENTTI ---
if valinta == "📈 Sijoitusagentti":
    st.title("📈 Sijoitusagentti")
    kohde = st.text_input("Syötä osake tai kohde:")
    if st.button("Analysoi"):
        # Luodaan linkit suoraan
        k = kohde.replace(" ", "-")
        st.write(f"### 🔗 Linkit kohteeseen {kohde}")
        col1, col2, col3 = st.columns(3)
        col1.markdown(f"[📊 Inderes](https://www.inderes.fi/fi/haku?q={k})")
        col2.markdown(f"[📰 Taloussanomat](https://is.fi/haku/?query={k})")
        col3.markdown(f"[📈 Google Finance](https://www.google.com/finance/quote/{k}:HEL)")
        
        # Analyysi ilman API-avainta
        agent = Agent(role="Analyytikko", goal="Analysoi kohde.", backstory="Olet kokenut pörssianalyytikko.")
        task = Task(description=f"Anna lyhyt, ytimekäs suositus kohteelle {kohde}.", expected_output="Analyysi.", agent=agent)
        st.write(str(Crew(agents=[agent], tasks=[task]).kickoff()))

# --- 2. PITKÄVETO ---
elif valinta == "⚽ Pitkäveto":
    st.title("⚽ Pitkäveto")
    o = st.text_input("Ottelu:")
    if st.button("Analysoi"):
        agent = Agent(role="Vedonlyöjä", goal="Valitse voittaja.", backstory="Olet ammattivedonlyöjä.")
        task = Task(description=f"Ottelu {o} analyysi ja pelivalinta.", expected_output="Tulos.", agent=agent)
        st.write(str(Crew(agents=[agent], tasks=[task]).kickoff()))

# --- 3. BENSAVAHTI ---
elif valinta == "⛽ Bensavahti (Uusimaa)":
    st.title("⛽ Uudenmaan bensahinnat")
    if st.button("Päivitä Uudenmaan hinnat"):
        try:
            url = "https://www.polttoaine.net/Uusimaa"
            res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            t = soup.find("table", {"id": "LisaaHintojaTable"})
            data = [{"Asema": r.find_all("td")[0].text.strip(), "95E10": r.find_all("td")[2].text.strip(), "Diesel": r.find_all("td")[4].text.strip()} for r in t.find_all("tr")[2:15]]
            st.table(pd.DataFrame(data))
        except: st.error("Ei yhteyttä palveluun.")

# --- 4. SALKUNHOITAJA ---
elif valinta == "💼 Salkunhoitaja":
    st.title("💼 Salkunhoitaja")
    riski = st.select_slider("Riski:", ["Varovainen", "Tasapainoinen", "Kasvuhakuinen"])
    if st.button("Luo salkku"):
        agent = Agent(role="Salkunhoitaja", goal="Rakenna salkku.", backstory="Olet pankin asiantuntija.")
        task = Task(description=f"Luo {riski}-salkku ja listaa konkreettisia kohteita.", expected_output="Salkku.", agent=agent)
        st.write(str(Crew(agents=[agent], tasks=[task]).kickoff()))
