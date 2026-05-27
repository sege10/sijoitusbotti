import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from crewai import Agent, Task, Crew

st.set_page_config(page_title="SEGE10 Keskus", layout="wide")
valinta = st.sidebar.radio("Työkalu:", ["📈 Sijoitusagentti", "⚽ Pitkäveto", "⛽ Bensavahti", "💼 Salkunhoitaja", "📖 Liiketaloussanasto"])

# --- 1. SIJOITUSAGENTTI ---
if valinta == "📈 Sijoitusagentti":
    st.title("📈 Sijoitusagentti")
    kohde = st.text_input("Syötä yrityksen nimi:")
    if st.button("Hae analyysilinkit"):
        k = kohde.replace(" ", "-")
        st.write(f"### 🔗 Suorat lähteet: {kohde}")
        st.markdown(f"- [📊 Inderes](https://www.inderes.fi/fi/haku?q={k})")
        st.markdown(f"- [📰 Taloussanomat](https://is.fi/haku/?query={k})")
        st.markdown(f"- [📈 Google Finance](https://www.google.com/finance/quote/{k}:HEL)")
        st.info("Käytä yllä olevia linkkejä tarkistaaksesi päivän kurssin ja uusimmat raportit.")

# --- 2. PITKÄVETO ---
elif valinta == "⚽ Pitkäveto":
    st.title("⚽ Pitkäveto")
    o = st.text_input("Ottelu:")
    if st.button("Analysoi"):
        agent = Agent(role="Vedonlyöjä", goal="Analysoi ottelu.", backstory="Olet ammattilainen.")
        task = Task(description=f"Analysoi ottelu {o} ja anna pelivalinta.", expected_output="Lyhyt analyysi.", agent=agent)
        st.write(str(Crew(agents=[agent], tasks=[task]).kickoff()))

# --- 3. BENSAVAHTI ---
elif valinta == "⛽ Bensavahti":
    st.title("⛽ Bensahinnat (Uusimaa)")
    st.write("Linkki suoraan hintapalveluun:")
    st.link_button("Avaa Polttoaine.net (Uusimaa)", "https://www.polttoaine.net/Uusimaa")

# --- 4. SALKUNHOITAJA (Rahakenttä palautettu!) ---
elif valinta == "💼 Salkunhoitaja":
    st.title("💼 Salkunhoitaja")
    summa = st.number_input("Sijoitettava summa (€):", value=1000)
    riski = st.select_slider("Riski:", ["Varovainen", "Tasapainoinen", "Kasvuhakuinen"])
    if st.button("Luo salkkuehdotus"):
        agent = Agent(role="Salkunhoitaja", goal="Rakenna hajautettu salkku.", backstory="Olet kokenut salkunhoitaja.")
        task = Task(description=f"Luo {riski}-strategian mukainen salkku {summa} eurolle. Listaa 3-5 kohdetta ja euromääräinen jako.", expected_output="Salkku.", agent=agent)
        st.write(str(Crew(agents=[agent], tasks=[task]).kickoff()))

# --- 5. LIIKETALOUSSANASTO ---
elif valinta == "📖 Liiketaloussanasto":
    st.title("📖 Liiketaloussanasto")
    sanasto = {
        "Liikevaihto": "Yrityksen myyntien yhteenlaskettu arvo tiettynä aikana.",
        "Käyttökate (EBITDA)": "Liiketulos ennen poistoja. Kertoo operatiivisen toiminnan kannattavuudesta.",
        "Inbound-myynti": "Myyntitapa, jossa asiakas löytää yrityksen (esim. hakukoneen tai somen kautta) ja ottaa itse yhteyttä.",
        "ROI (Return on Investment)": "Sijoitetun pääoman tuotto-prosentti.",
        "Likviditeetti": "Yrityksen kyky maksaa lyhytaikaiset velat heti."
    }
    for termi, selitys in sanasto.items():
        st.write(f"**{termi}**: {selitys}")
