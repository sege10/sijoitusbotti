import streamlit as st
import os
import requests

# Pakotetaan Streamlit käyttämään Secrets-avaimia
if "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
if "SERPER_API_KEY" in st.secrets:
    os.environ["SERPER_API_KEY"] = st.secrets["SERPER_API_KEY"]

from crewai import Agent, Crew, Process, Task
from crewai_tools import SerperDevTool

# KRYPTOHAKU PUHTAASTI COINGECKOLTA (Ei yfinancea)
def hae_porssitiedot_euroina(ticker):
    ticker = ticker.strip().upper()
    puhdas_ticker = ticker.replace("-USD", "")
    crypto_ids = {"BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana", "XRP": "ripple", "ADA": "cardano", "DOT": "polkadot"}
    
    if puhdas_ticker in crypto_ids:
        crypto_id = crypto_ids[puhdas_ticker]
        try:
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies=eur&include_24hr_change=true"
            response = requests.get(url, timeout=10).json()
            current_price_eur = response[crypto_id]['eur']
            muutos = response[crypto_id]['eur_24h_change']
            return current_price_eur, f"Kohde: {ticker}. Hinta: {current_price_eur:,.2f} EUR. 24h muutos: {muutos:.2f}%."
        except Exception as e:
            return None, f"Virhe CoinGecko-haussa: {e}"
            
    return None, f"Tunnus '{ticker}' ei ole tuettujen kryptojen listalla (BTC, ETH, SOL, XRP, ADA, DOT)."

# SIVUN RAKENNE JA VALIKKO
st.set_page_config(page_title="SEGE10 Moni-Agentti", page_icon="🤖", layout="wide")
st.sidebar.title("🤖 SEGE10 AI-Keskus")
st.sidebar.write("Valitse tekoälytiimi käyttötarkoituksen mukaan:")
sovellusvalinta = st.sidebar.radio("Valitse agentti:", ["📈 Sijoitusagentti", "⚽ Pitkäveto-agentti", "⛽ Bensavahti"])

# ==================== 1. SIJOITUSAGENTTI ====================
if sovellusvalinta == "📈 Sijoitusagentti":
    st.title("📈 SEGE10:n AI-Sijoitusagentti")
    kohde = st.text_input("Syötä kryptovaluutan tunnus (esim. BTC, ETH, SOL):", "BTC")
    
    if st.button("Käynnistä tekoälyanalyysi"):
        st.info(f"Haetaan kohteen {kohde} reaaliaikaista markkinahintaa CoinGeckosta...")
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
                    goal="Tulkita annettua numerodataa.",
                    backstory=f"Käytössäsi on tämä tuore markkinatieto CoinGeckosta: {markkinadata_teksti}",
                    verbose=True
                )
                manager_agent = Agent(
                    role="Salkunhoitaja",
                    goal="Tehdä selkeä suomenkielinen sijoitussuositus (OSTA, MYY, ODOTA tai PIDÄ).",
                    backstory="Olet tiukka salkunhoitaja. Kirjoitat suosituksesi ammattimaisesti suomeksi.",
                    verbose=True
                )
                task1 = Task(description="Tiivistä markkinasuunta.", expected_output="Lyhyt suunta-analyysi.", agent=data_agent)
                task2 = Task(description="Anna suositus. Aloita vastauksesi sanalla OSTA, MYY, ODOTA tai PIDÄ.", expected_output="Suositus ja perustelut.", agent=manager_agent)
                
                sijoitus_tiimi = Crew(agents=[data_agent, manager_agent], tasks=[task1, task2], process=Process.sequential)
                st.write(str(sijoitus_tiimi.kickoff()).strip())
            except Exception as e:
                st.error(f"Virhe: {e}")

# ==================== 2. PITKÄVETO-AGENTTI ====================
elif sovellusvalinta == "⚽ Pitkäveto-agentti":
    st.title("⚽ SEGE10:n AI-Pitkävetoagentti")
    ottelu = st.text_input("Syötä illan ottelu ja sarja:", "Suomi - Ruotsi, Jääkiekko")
    kertoimet = st.text_input("Syötä tarjolla olevat kertoimet:", "1: 1.95 | X: 4.20 | 2: 2.90")
    
    if st.button("Käynnistä Pitkäveto-analyysi"):
        st.info(f"Agentit etsivät tietoa ottelusta Googlella...")
        try:
            google_haku = SerperDevTool()
            urheilu_analyytikko = Agent(
                role="Urheiludata-analyytikko",
                goal=f"Etsiä Googlesta TÄMÄN PÄIVÄN tuoreimmat uutiset ja poissaolot ottelusta: {ottelu}.",
                backstory="Olet urheilutoimittaja. Käytät Google-hakua löytääksesi reaaliaikaiset kokoonpanotiedot.",
                tools=[google_haku],
                verbose=True
            )
            vihje_mestari = Agent(
                role="Vedonlyöntiasiantuntija",
                goal="Laskea kumpiko kohde tarjoaa parhaan edun kertoimiin nähden.",
                backstory=f"Olet ammattimainen vedonlyöjä. Analysoit peliä näillä kertoimilla: {kertoimet}.",
                verbose=True
            )
            utask1 = Task(description=f"Etsi Googlesta tuoreimmat uutiset ja kokoonpanotilanteet otteluun {ottelu}.", expected_output="Raportti joukkueiden tilanteesta.", agent=urheilu_analyytikko)
            utask2 = Task(description=f"Vertaa tietoja kertoimiin ({kertoimet}). Aloita vastauksesi muodossa **PELIVALINTA:** ja sen jälkeen perustelut.", expected_output="Pelivalinta ja perustelut suomeksi.", agent=vihje_mestari)
            
            veto_tiimi = Crew(agents=[urheilu_analyytikko, vihje_mestari], tasks=[utask1, utask2], process=Process.sequential)
            st.write(str(veto_tiimi.kickoff()).strip())
        except Exception as e:
            st.error(f"Virhe: {e}")

# ==================== 3. BENSAVAHTI ====================
elif sovellusvalinta == "⛽ Bensavahti":
    st.title("⛽ SEGE10:n AI-Bensavahti (PK-seutu)")
    st.write("Tämä agentti etsii netistä reaaliajassa pääkaupunkiseudun halvimmat polttoainehinnat ja ryhmittelee ne alueittain.")
    
    bensalaatu = st.selectbox("Valitse polttoaine:", ["95 E10", "98 E5", "Diesel"])
    
    if st.button("Etsi halvin bensa"):
        st.info("Käynnistetään Bensavahti-agentti selaamaan julkisia hintalistoja Googlella...")
        try:
            google_haku = SerperDevTool()
            bensa_agent = Agent(
                role="Polttoainehintoja seuraava data-botti",
                goal=f"Etsiä Googlesta tämän hetken halvimmat {bensalaatu} hinnat Helsingistä, Espoosta ja Vantaalta.",
                backstory="Olet säästeliäs kuluttaja-asiamies. Tehtäväsi on kaivaa tuoreimmat bensanhinnat netistä ja poimia sieltä halvimmat asemat.",
                tools=[google_haku],
                verbose=True
            )
            bensa_task = Task(
                description=f"""Etsi netistä tuoreimmat hinnat laadulle: {bensalaatu}.
                Segmentoi ja ryhmittele vastaus selkeästi seuraaviin alueisiin:
                - **Pohjoinen / Keski-Helsinki**
                - **Itä-Helsinki**
                - **Länsi-Helsinki / Espoo**
                - **Vantaa**
                Ilmoita kunkin alueen kohdalla halvin asema, sen osoite/paikka ja hinta (€/l). Lopuksi tee lyhyt yhteenveto kaikkein halvimmasta.""",
                expected_output="Selkeä alueittain segmentoitun raportti halvimmista polttoainehinnoista.",
                agent=bensa_agent
            )
            bensa_crew = Crew(agents=[bensa_agent], tasks=[bensa_task], process=Process.sequential)
            st.write(str(bensa_crew.kickoff()).strip())
        except Exception as e:
            st.error(f"Virhe: {e}")
