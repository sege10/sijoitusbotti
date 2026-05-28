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

# --- 1. SIJOITUSAGENTTI ---
if valinta == "📈 Sijoitusagentti":
    st.title("📈 Sijoitusagentti")
    kohde = st.text_input("Syötä osake (esim. NOKIA.HE):")
    if st.button("Analysoi"):
        # Lisätään User-Agent, jotta Yahoo ei estä hakuja
        ticker = yf.Ticker(kohde, session=None) 
        try:
            # Käytetään lyhyempää hakuväliä ja estetään liialliset pyynnöt
            hist = ticker.history(period="1d", interval="1d")
            
            if not hist.empty:
                price = hist['Close'].iloc[-1]
                st.metric(f"Hinta: {kohde}", f"{price:.2f} €")
                
                # AI-analyysi (tämä toimii normaalisti)
                agent = Agent(role="Analyytikko", goal="Analysoi ja anna suositus.", backstory="Pörssiasiantuntija.", tools=[search_tool])
                task = Task(description=f"Analysoi {kohde}, jonka hinta on {price}. Anna suositus.", expected_output="Analyysi.", agent=agent)
                st.write(str(Crew(agents=[agent], tasks=[task]).kickoff()))
            else:
                st.error("Ei dataa Yahoo Financesta.")
        except Exception as e:
            st.warning("Yahoo Finance on hetkellisesti ruuhkautunut. Kokeile uudestaan hetken päästä tai käytä Google-hakua.")

# --- 2. SALKUNHOITAJA ---
elif valinta == "💼 Salkunhoitaja":
    st.title("💼 Salkunhoitaja")
    summa = st.number_input("Summa (€):", value=1000)
    if st.button("Luo salkku"):
        agent = Agent(role="Salkunhoitaja", goal="Rakenna salkku.", backstory="Asiantuntija.", tools=[search_tool])
        task = Task(description=f"Luo salkku {summa} eurolle. Käytä Google-hakua markkinatrendeihin.", expected_output="Salkku.", agent=agent)
        st.write(str(Crew(agents=[agent], tasks=[task]).kickoff()))

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
