import streamlit as st
import os

# Pakotetaan Streamlit käyttämään Secrets-avainta CrewAI:lle
if "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

from crewai import Agent, Crew, Process, Task
import yfinance as yf

# POMMINVARMA HAKU JOKA OTTAA TÄMÄN PÄIVÄN VIIMEISIMMÄN MINUUTTIHINNAN
def hae_porssitiedot_euroina(ticker):
    try:
        # Haetaan kohteen aivan tuoreimmat minuutin välein päivittyvät tiedot tältä päivältä
        ticker_data = yf.Ticker(ticker)
        hist_1d = ticker_data.history(period="1d", interval="1m")
        
        if hist_1d.empty:
            # Jos kohde on viikonloppuna kiinni (esim. osakkeet), otetaan viimeisin sulkemishinta
            hist_1d = ticker_data.history(period="5d")
            
        current_price_usd = hist_1d['Close'].iloc[-1]
        
        # Haetaan euron ja dollarin suhde tältä päivältä
        eurusd_data = yf.Ticker("EURUSD=X")
        eurusd_hist = eurusd_data.history(period="1d")
        eurusd_kurssi = eurusd_hist['Close'].iloc[-1] if not eurusd_hist.empty else 1.09
        
        # Muunnetaan aito dollarimäärä euroiksi
        current_price_eur = current_price_usd / eurusd_kurssi
        
        # Haetaan 7 päivän historia suuntaa varten
        hist_7d = ticker_data.history(period="7d")
        alkuhinta_usd = hist_7d['Close'].iloc[0] if not hist_7d.empty else current_price_usd
        muutos = ((current_price_usd - alkuhinta_usd) / alkuhinta_usd) * 100
        
        return f"Kohteen {ticker} AITO LIVE-HINTA JUURI NYT: {current_price_eur:,.2f} EUR. Viimeisen 7 päivän muutos: {muutos:.2f}%."
    except Exception as e:
        return f"Virhe haettaessa reaaliaikaista dataa kohteelle {ticker}: {e}"

# Tyylitellään Streamlit-sivua
st.set_page_config(page_title="AI-Sijoitusagentti", page_icon="🤖")
st.title("🤖 SEGE10:n AI-Sijoitusagentti")
st.write("Tämä tekoälytiimi analysoi reaaliaikaista pörssidataa ja antaa suosituksia euroissa.")

kohde = st.text_input("Syötä osakkeen tai krypton tunnus (esim. AAPL, BTC-USD tai NOKIA.HE):", "BTC-USD")

if st.button("Käynnistä tekoälyanalyysi"):
    st.info(f"Agentit aloittavat kohteen {kohde} tutkimisen tämän päivän datalla. Odota hetki...")
    
    try:
        # Haetaan reaaliaikainen data euroina valmiiksi tekstiksi agentille
        reaaliaikainen_data = hae_porssitiedot_euroina(kohde)
        
        # Agentit
        data_agent = Agent(
            role="Markkinadata-analyytikko",
            goal=f"Analysoida annettua reaaliaikaista pörssidataa kohteesta {kohde}.",
            backstory=f"Olet tarkka analyytikko. Saat käyttöösi tämän REAALIAIKAISEN datan euroina: {reaaliaikainen_data}. Tehtäväsi on ottaa talteen aito live-hinta ja kehitys.",
            verbose=True
        )
        
        manager_agent = Agent(
            role="Salkunhoitaja",
            goal="Tehdä selkeä ja suoraviivainen sijoitussuositus euroissa.",
            backstory="Olet kokenut salkunhoitaja. Tehtäväsi on antaa tiukka ja selkeä suositus ilman kiertelyä.",
            verbose=True
        )

        # Tehtävät
        task1 = Task(
            description=f"Ota talteen annettu eurohinta kohteesta {kohde} ja kuvaile sen suunta.",
            expected_output="Raportti, jossa mainitaan kohteen aito hinta euroina ja viikon muutos.",
            agent=data_agent
        )
        task2 = Task(
            description=f"""Päätä sijoitussuositus kohteelle {kohde}. 
            Sinun on PAKKO aloittaa lopullinen vastauksesi täsmälleen seuraavalla muodolla (älä pyöristä tuhansia pois):
            
            **LIVE HINTA:** [Kirjoita tähän analyytikon antama aito hinta] EUR
            **SUOSITUS:** [Kirjoita tähän jokin näistä: OSTA / MYY / ODOTA / PIDÄ]
            
            Tämän alun jälkeen kirjoita selkeät, suomenkieliset perustelut päätöksellesi.""",
            expected_output="Suositus ja hinta vaaditussa muodossa, seurattuna suomenkielisillä perusteluilla.",
            agent=manager_agent
        )

        # Tiimi kasaan
        sijoitus_tiimi = Crew(
            agents=[data_agent, manager_agent],
            tasks=[task1, task2],
            process=Process.sequential
        )
        
        tulos = sijoitus_tiimi.kickoff()
        st.success("Analyysi valmis!")
        st.write(str(tulos))
        
    except Exception as e:
        st.error(f"Tapahtui virhe datan haussa tai analyysissa: {e}")
