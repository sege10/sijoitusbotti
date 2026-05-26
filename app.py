import streamlit as st
import os

# Pakotetaan Streamlit käyttämään Secrets-avainta CrewAI:lle
if "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

from crewai import Agent, Crew, Process, Task
import yfinance as yf

# PARANNETTU HAKU: Hakee livenä hinnan ja muuntaa sen euroiksi
def hae_porssitiedot_euroina(ticker):
    try:
        data = yf.Ticker(ticker)
        info = data.info
        current_price_usd = info.get('regularMarketPrice') or info.get('currentPrice')
        
        # Haetaan historiatiedot lyhyttä trendiä varten
        hist = data.history(period="7d")
        if current_price_usd is None:
            current_price_usd = hist['Close'].iloc[-1]
            
        # Haetaan EUR/USD valuuttakurssi muunnosta varten
        eurusd_data = yf.Ticker("EURUSD=X")
        # Jos haku epäonnistuu, käytetään suuntaa-antavaa kiinteää kurssia 1.09
        eurusd_kurssi = eurusd_data.info.get('regularMarketPrice') or 1.09
        
        # Muunnetaan dollarit euroiksi (jaetaan dollarit kurssilla)
        current_price_eur = current_price_usd / eurusd_kurssi
        
        alkuhinta_usd = hist['Close'].iloc[0]
        muutos = ((current_price_usd - alkuhinta_usd) / alkuhinta_usd) * 100
        
        return f"Kohteen {ticker} LIVE-HINTA: {current_price_eur:,.2f} EUR (valuuttakurssilla {eurusd_kurssi:.4f}). Viimeisen 7 päivän muutos: {muutos:.2f}%."
    except Exception as e:
        return f"Virhe haettaessa dataa kohteelle {ticker}: {e}"

# Tyylitellään Streamlit-sivua hieman siistimmäksi
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
            backstory=f"Olet tarkka analyytikko. Saat käyttöösi tämän REAALIAIKAISEN datan euroina: {reaaliaikainen_data}. Tehtäväsi on tiivistää hinta ja kehitys.",
            verbose=True
        )
        
        manager_agent = Agent(
            role="Salkunhoitaja",
            goal="Tehdä selkeä ja suoraviivainen sijoitussuositus euroissa.",
            backstory="Olet kokenut salkunhoitaja. Tehtäväsi on antaa tiukka ja selkeä suositus ilman kiertelyä.",
            verbose=True
        )

        # Tehtävät – pakotetaan haluttu vastausmuoto
        task1 = Task(
            description=f"Ota talteen annettu eurohinta kohteesta {kohde} ja kuvaile sen suunta.",
            expected_output="Raportti, jossa mainitaan kohteen aito hinta euroina ja viikon muutos.",
            agent=data_agent
        )
        task2 = Task(
            description=f"""Päätä sijoitussuositus kohteelle {kohde}. 
            Sinun on PAKKO aloittaa lopullinen vastauksesi täsmälleen seuraavalla muodolla (korvaa X:t oikeilla tiedoilla):
            
            **LIVE HINTA:** X,XX EUR
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
        
        # Tulostetaan agentin vastaus
        st.write(str(tulos))
        
    except Exception as e:
        st.error(f"Tapahtui virhe datan haussa tai analyysissa: {e}")
