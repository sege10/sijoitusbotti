import streamlit as st
import os

# Pakotetaan Streamlit käyttämään Secrets-avainta CrewAI:lle
if "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

from crewai import Agent, Crew, Process, Task
import yfinance as yf

# PUHDAS MATEMAATTINEN HAKU (Ei tekoälyä sotkemassa numeroita)
def hae_porssitiedot_euroina(ticker):
    ticker = ticker.strip().upper()
    if ticker in ["BTC", "ETH", "SOL", "XRP", "ADA", "DOT"]:
        ticker = f"{ticker}-USD"
        
    try:
        ticker_data = yf.Ticker(ticker)
        
        # Haetaan tuorein minuuttidata
        hist_1d = ticker_data.history(period="1d", interval="1m")
        if hist_1d.empty:
            hist_1d = ticker_data.history(period="5d")
            
        if hist_1d.empty:
            return None, f"Tunnuksella '{ticker}' ei löytynyt pörssidataa."
            
        current_price_usd = hist_1d['Close'].iloc[-1]
        
        # Haetaan valuuttakurssi EUR/USD
        eurusd_data = yf.Ticker("EURUSD=X")
        eurusd_hist = eurusd_data.history(period="1d")
        eurusd_kurssi = eurusd_hist['Close'].iloc[-1] if not eurusd_hist.empty else 1.09
        
        # Lasketaan aito eurohinta numerona
        current_price_eur = current_price_usd / eurusd_kurssi
        
        # 7 päivän kehitys trendiä varten
        hist_7d = ticker_data.history(period="7d")
        alkuhinta_usd = hist_7d['Close'].iloc[0] if not hist_7d.empty else current_price_usd
        muutos = ((current_price_usd - alkuhinta_usd) / alkuhinta_usd) * 100
        
        raportti_teksti = f"Kohde: {ticker}. Tämänhetkinen hinta: {current_price_eur:,.2f} EUR. 7 päivän muutosprosentti: {muutos:.2f}%."
        return current_price_eur, raportti_teksti
    except Exception as e:
        return None, f"Virhe tiedonhaussa: {e}"

# SIVUN RAKENNE
st.set_page_config(page_title="AI-Sijoitusagentti", page_icon="🤖")
st.title("🤖 SEGE10:n AI-Sijoitusagentti")
st.write("Tämä tekoälytiimi analysoi reaaliaikaista pörssidataa.")

kohde = st.text_input("Syötä osakkeen tai krypton tunnus (esim. AAPL, BTC tai NOKIA.HE):", "BTC")

if st.button("Käynnistä tekoälyanalyysi"):
    st.info(f"Haetaan kohteen {kohde} reaaliaikaista markkinahintaa...")
    
    # 1. HAETAAN HINTA VARMASTI NUMERONA
    aito_hinta_eur, markkinadata_teksti = hae_porssitiedot_euroina(kohde)
    
    if aito_hinta_eur is None:
        st.error(markkinadata_teksti)
    else:
        # TÄMÄ TULOSTUU RUUDULLE SUORAAN KOODISTA, TEKOÄLY EI PÄÄSE SOTKEMAAN TÄTÄ
        st.markdown("---")
        st.subheader("📊 REAALIAIKAINEN MARKKINATILANNE")
        st.metric(label=f"LIVE HINTA ({kohde.upper()})", value=f"{aito_hinta_eur:,.2f} EUR")
        st.markdown("---")
        
        st.info("Käynnistetään tekoälytiimi analysoimaan markkinatilannetta...")
        
        try:
            # Agentit
            data_agent = Agent(
                role="Markkinadata-analyytikko",
                goal="Tulkita annettua numerodataa ja kertoa onko kurssi nousussa vai laskussa.",
                backstory=f"Olet analyytikko. Käytössäsi on tämä tarkka tämän sekunnin pörssitieto: {markkinadata_teksti}",
                verbose=True
            )
            
            manager_agent = Agent(
                role="Salkunhoitaja",
                goal="Tehdä selkeä suomenkielinen sijoitussuositus (OSTA, MYY, ODOTA tai PIDÄ).",
                backstory="Olet tiukka salkunhoitaja. Kirjoitat suosituksesi ammattimaisesti suomeksi.",
                verbose=True
            )

            # Tehtävät
            task1 = Task(
                description="Tiivistä lyhyesti kohteen tämänhetkinen markkinasuunta viikon kehityksen perusteella.",
                expected_output="Lyhyt suunta-analyysi.",
                agent=data_agent
            )
            task2 = Task(
                description=f"""Kirjoita kohteelle {kohde} sijoitussuositus.
                Aloita vastauksesi TÄSMÄLLEEN tällä yhdellä sanalla isolla kirjoitettuna: OSTA, MYY, ODOTA tai PIDÄ.
                Kirjoita sen jälkeen välilyönti ja kattavat suomenkieliset perustelut sille, miksi päädyit tähän tulokseen.""",
                expected_output="Yhdellä sanalla alkava suositus ja sen suomenkieliset perustelut.",
                agent=manager_agent
            )

            sijoitus_tiimi = Crew(
                agents=[data_agent, manager_agent],
                tasks=[task1, task2],
                process=Process.sequential
            )
            
            tulos = sijoitus_tiimi.kickoff()
            
            st.success("Tekoälyanalyysi valmis!")
            
            # Tulostetaan tekoälyn suositus siististi
            vastaus = str(tulos).strip()
            
            st.write("### 🤖 Tekoälytiimin suositus ja perustelut:")
            st.write(vastaus)
            
        except Exception as e:
            st.error(f"Tekoälytiimin käynnistyksessä tapahtui virhe: {e}")
