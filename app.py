import streamlit as st
import os
import requests

# Pakotetaan Streamlit käyttämään Secrets-avainta CrewAI:lle
if "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

from crewai import Agent, Crew, Process, Task
from crewai_tools import ScrapeWebsiteTool
import yfinance as yf

# KRYPTOHAKU COINGECKOLTA
def hae_porssitiedot_euroina(ticker):
    ticker = ticker.strip().upper()
    puhdas_ticker = ticker.replace("-USD", "")
    
    crypto_ids = {
        "BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana",
        "XRP": "ripple", "ADA": "cardano", "DOT": "polkadot"
    }
    
    if puhdas_ticker in crypto_ids:
        crypto_id = crypto_ids[puhdas_ticker]
        try:
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies=eur&include_24hr_change=true"
            response = requests.get(url, timeout=10).json()
            current_price_eur = response[crypto_id]['eur']
            muutos = response[crypto_id]['eur_24h_change']
            return current_price_eur, f"Kohde: {ticker}. Hinta: {current_price_eur:,.2f} EUR. 24h muutos: {muutos:.2f}%."
        except:
            pass
            
    try:
        ticker_data = yf.Ticker(ticker)
        hist_1d = ticker_data.history(period="3d")
        if hist_1d.empty:
            return None, f"Tunnuksella '{ticker}' ei löytynyt pörssidataa."
        current_price_usd = hist_1d['Close'].iloc[-1]
        current_price_eur = current_price_usd / 1.09
        return current_price_eur, f"Kohde: {ticker}. Hinta: {current_price_eur:,.2f} EUR."
    except Exception as e:
        return None, f"Virhe tiedonhaussa: {e}"

# SIVUN ASETUKSET JA NAVIGOINTIVALIKKO (Sivupalkki)
st.set_page_config(page_title="SEGE10 AI-Agentit", page_icon="🤖", layout="wide")

st.sidebar.title("🤖 SEGE10 AI-Keskus")
st.sidebar.write("Valitse alta, mitä tekoälytiimiä haluat käyttää:")
sovellusvalinta = st.sidebar.radio("Valitse agentti:", ["📈 Sijoitusagentti", "⚽ Pitkäveto-agentti"])

st.sidebar.markdown("---")
st.sidebar.write("Versio 2.0 (2026)")

# ==================== VAIHTOEHTO 1: SIJOITUSAGENTTI ====================
if sovellusvalinta == "📈 Sijoitusagentti":
    st.title("📈 SEGE10:n AI-Sijoitusagentti")
    st.write("Tämä tiimi analysoi reaaliaikaista pörssi- ja kryptodataa euroissa.")
    
    kohde = st.text_input("Syötä osakkeen tai krypton tunnus (esim. BTC, ETH tai AAPL):", "BTC")
    
    if st.button("Käynnistä tekoälyanalyysi"):
        st.info(f"Haetaan kohteen {kohde} markkinahintaa...")
        aito_hinta_eur, markkinadata_teksti = hae_porssitiedot_euroina(kohde)
        
        if aito_hinta_eur is None:
            st.error(markkinadata_teksti)
        else:
            st.markdown("---")
            st.metric(label=f"HINTA EUROISSA ({kohde.upper()})", value=f"{aito_hinta_eur:,.2f} EUR")
            st.markdown("---")
            
            st.info("Käynnistetään sijoitustiimi analysoimaan tilannetta...")
            try:
                data_agent = Agent(
                    role="Markkinadata-analyytikko",
                    goal="Tulkita annettua numerodataa ja kertoa kurssin suunta.",
                    backstory=f"Olet tarkka analyytikko. Käytössäsi on tämä pörssitieto: {markkinadata_teksti}",
                    verbose=True
                )
                manager_agent = Agent(
                    role="Salkunhoitaja",
                    goal="Tehdä selkeä suomenkielinen sijoitussuositus (OSTA, MYY, ODOTA tai PIDÄ).",
                    backstory="Olet tiukka salkunhoitaja. Kirjoitat suosituksesi ammattimaisesti suomeksi.",
                    verbose=True
                )
                
                task1 = Task(
                    description="Tiivistä lyhyesti kohteen tämänhetkinen markkinasuunta.",
                    expected_output="Lyhyt suunta-analyysi.",
                    agent=data_agent
                )
                task2 = Task(
                    description=f"""Anna suositus kohteelle {kohde}. Aloita vastauksesi TÄSMÄLLEEN tällä yhdellä sanalla isolla kirjoitettuna: OSTA, MYY, ODOTA tai PIDÄ. Kirjoita sen jälkeen perustelut suomeksi.""",
                    expected_output="Yhdellä sanalla alkava suositus ja sen suomenkieliset perustelut.",
                    agent=manager_agent
                )
                
                sijoitus_tiimi = Crew(agents=[data_agent, manager_agent], tasks=[task1, task2], process=Process.sequential)
                tulos = sijoitus_tiimi.kickoff()
                
                st.success("Analyysi valmis!")
                st.write("### 🤖 Tekoälytiimin suositus ja perustelut:")
                st.write(str(tulos).strip())
            except Exception as e:
                st.error(f"Virhe: {e}")

# ==================== VAIHTOEHTO 2: PITKÄVETO-AGENTTI ====================
elif sovellusvalinta == "⚽ Pitkäveto-agentti":
    st.title("⚽ SEGE10:n AI-Pitkävetoagentti")
    st.write("Tämä tiimi analysoi urheiluotteluita, tilastoja ja kertoimia löytääkseen parhaat pelikohteet.")
    
    ottelu = st.text_input("Syötä illan ottelu ja sarja (esim. Real Madrid - Barcelona, La Liga):", "Suomi - Ruotsi, Jääkiekko")
    kertoimet = st.text_input("Syötä tarjolla olevat kertoimet (esim. 1: 2.10 | X: 3.40 | 2: 3.10):", "1: 1.95 | X: 4.20 | 2: 2.90")
    
    if st.button("Käynnistä Pitkäveto-analyysi"):
        st.info(f"Käynnistetään urheiluanalyytikot tutkimaan ottelua: {ottelu}...")
        
        try:
            # Annetaan agentille nettisivujen lukutyökalu uutisten ja tilastojen hakuun
            nettityokalu = ScrapeWebsiteTool()
            
            urheilu_analyytikko = Agent(
                role="Urheiludata-analyytikko",
                goal=f"Etsiä tuoreimmat uutiset, kuntopuntarit ja loukkaantumistiedot ottelusta: {ottelu}.",
                backstory="Olet urheilutilastoihin erikoistunut tutkija. Löydät netistä aina tärkeimmät pointit otteluiden taustoista.",
                tools=[nettityokalu],
                verbose=True
            )
            
            vihje_mestari = Agent(
                role="Vedonlyöntiasiantuntija",
                goal="Laskea kumpi joukkue tarjoaa kertoimiin nähden parhaan peliarvon (Value bet).",
                backstory=f"Olet ammattimainen vedonlyöjä. Tehtäväsi on analysoida ottelua annettujen kertoimien valossa: {kertoimet}.",
                verbose=True
            )
            
            utask1 = Task(
                description=f"Etsi netistä ja tiivistä molempien joukkueiden 3 viimeisintä ottelua ja mahdolliset tärkeät poissaolot otteluun {ottelu} liittyen.",
                expected_output="Tiivis raportti joukkueiden tämänhetkisestä pelivireestä ja kokoonpanotilanteesta.",
                agent=urheilu_analyytikko
            )
            
            utask2 = Task(
                description=f"""Vertaa analyytikon löytämiä tietoja annettuihin kertoimiin ({kertoimet}). 
                Päätä paras pelivalinta (esim. Kotivoitto 1, Tasapeli X, Vierasvoitto 2, tai jokin muu varma pelikohde).
                
                Sinun on PAKKO aloittaa vastauksesi TÄSMÄLLEEN tässä muodossa:
                **PELIVALINTA:** [Kirjoita tähän suositeltu merkki tai kohde]
                **PERUSTELUT:**
                
                Kirjoita tämän jälkeen selkeät, asiantuntevat suomenkieliset perustelut sille, miksi tämä veto kannattaa asettaa.""",
                expected_output="Pelivalinta oikeassa muodossa ja kattavat perustelut suomeksi.",
                agent=vihje_mestari
            )
            
            veto_tiimi = Crew(agents=[urheilu_analyytikko, vihje_mestari], tasks=[utask1, utask2], process=Process.sequential)
            veto_tulos = veto_tiimi.kickoff()
            
            st.success("Pitkäveto-analyysi valmis!")
            st.write("### 🤖 Pitkäveto-agentin pelisuositus:")
            st.write(str(veto_tulos).strip())
            
        except Exception as e:
            st.error(f"Urheiluagenttien käynnistyksessä tapahtui virhe: {e}")
