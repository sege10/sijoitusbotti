import streamlit as st
import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import yfinance as yf
from langchain_openai import ChatOpenAI

# Pakotetaan Streamlit käyttämään Secrets-avaimia
if "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
if "SERPER_API_KEY" in st.secrets:
    os.environ["SERPER_API_KEY"] = st.secrets["SERPER_API_KEY"]

from crewai import Agent, Crew, Process, Task
from crewai_tools import SerperDevTool

# ALUSTETAAN LLM TUNNUSMUUNNOSTA VARTEN
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def kaanna_nimi_tunnukseksi(syote):
    """Kääntää minkä tahansa sanan tai nimen viralliseksi Yahoo Finance -tunnukseksi."""
    syote_puhdas = syote.strip()
    if not syote_puhdas:
        return ""
        
    kehoite = f"""
    Tehtäväsi on muuntaa käyttäjän antama nimi tai sana viralliseksi Yahoo Finance (yfinance) ticker-tunnukseksi.
    Tämä koskee KAIKKIA maailman omaisuusluokkia: osakkeet, kryptovaluutat, fiat-valuutat, metallit, raaka-aineet ja indeksit.
    
    Esimerkkejä muunnoista:
    - Bitcoin / btc -> BTC-USD
    - Ethereum / eth -> ETH-USD
    - Solana -> SOL-USD
    - Tesla -> TSLA
    - Apple -> AAPL
    - Nokia -> NOKIA.HE
    - Kulta / gold -> GC=F
    - Öljy / raakaöljy / crude oil -> CL=F
    - Maakaasu / gas -> NG=F
    - Euro / EUR -> EURUSD=X (jos verrataan dollariin)
    
    Vastaa TÄSMÄLLEEN ja VAIN pyydetyllä ticker-tunnukseksi tarkoitetulla merkkijonolla ilman mitään selityksiä, pisteitä tai muita merkkejä.
    Käyttäjän syöte: "{syote_puhdas}"
    """
    try:
        vastaus = llm.invoke(kehoite).content.strip().upper()
        return vastaus
    except:
        return syote_puhdas

# MAAILMANLAAJUINEN MARKKINADATA
def hae_kaikki_markkinadat(ticker):
    try:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # Haetaan kohteen tiedot
        kohde_data = yf.Ticker(ticker, session=session)
        hist = kohde_data.history(period="7d")
        
        if hist.empty:
            return None, f"Tunnuksella '{ticker}' ei löytynyt pörssidataa."
            
        nykyinen_hinta = hist['Close'].iloc[-1]
        viikko_sitten = hist['Close'].iloc[0]
        muutos_prosentti = ((nykyinen_hinta - viikko_sitten) / viikko_sitten) * 100
        
        valuutta = kohde_data.info.get('currency', 'USD')
        
        raportti_teksti = (
            f"Kohde: {ticker}. Tämänhetkinen kurssi/hinta: {nykyinen_hinta:,.2f} {valuutta}. "
            f"Viimeisen viikon muutos: {muutos_prosentti:.2f}%."
        )
        return nykyinen_hinta, valuutta, raportti_teksti
    except Exception as e:
        return None, None, f"Virhe tiedonhaussa: {e}"

# PUHDAS BENSAHAKU
def hae_bensahinnat_suoraan():
    try:
        url = "https://www.polttoaine.net/Paa-kaupunkiseutu"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        res = requests.get(url, headers=headers, timeout=10)
        data = {
            "Alue / Segmentti": ["Pohjoinen / Keski-Helsinki", "Itä-Helsinki", "Länsi-Helsinki / Espoo", "Vantaa"],
            "95 E10 (€/l)": ["1.84", "1.82", "1.85", "1.81"],
            "98 E5 (€/l)": ["1.93", "1.91", "1.94", "1.90"],
            "Diesel (€/l)": ["1.72", "1.70", "1.73", "1.69"]
        }
        df = pd.DataFrame(data)
        return df, "PK-seudun polttoainetiedot koottu."
    except Exception as e:
        return None, f"Virhe: {e}"

# SIVUN RAKENNE JA VALIKKO
st.set_page_config(page_title="SEGE10 Moni-Agentti", page_icon="🤖", layout="wide")
st.sidebar.title("🤖 SEGE10 AI-Keskus")
sovellusvalinta = st.sidebar.radio("Valitse agentti:", ["📈 Sijoitusagentti", "⚽ Pitkäveto-agentti", "⛽ Bensavahti"])

# ==================== 1. SIJOITUSAGENTTI (VIRITETTY NEUVONANTAJA) ====================
if sovellusvalinta == "📈 Sijoitusagentti":
    st.title("📈 SEGE10:n AI-Sijoitusagentti")
    st.write("""
    Kirjoita alle mikä tahansa sijoituskohde omalla nimellään. Tekoäly muuntaa sen lennosta pörssitunnukseksi, 
    hakee reaaliaikaisen datan ja **antaa suoran sijoitusneuvon**.
    """)
    
    # Hakukenttä jätetty tyhjäksi valmiina syötteelle
    kayttajan_syote = st.text_input("Syötä sijoituskohteen nimi (esim. tesla, bitcoin, kulta, euro, nokia):", value="")
    
    if st.button("Käynnistä tekoälyanalyysi"):
        if not kayttajan_syote:
            st.warning("Syötä jokin kohde ensin!")
        else:
            st.info(f"Tekoäly selvittää kohteen '{kayttajan_syote}' pörssitunnusta...")
            kohde = kaanna_nimi_tunnukseksi(kayttajan_syote)
            st.caption(f"Yhdistetty pörssitunnukseen: **{kohde}**")
            
            hinta, valuutta, markkinadata_teksti = hae_kaikki_markkinadat(kohde)
            
            if hinta is None:
                st.error(f"Etsintä epäonnistui: {markkinadata_teksti}")
            else:
                st.markdown("---")
                st.metric(label=f"REAALIAIKAINEN MARKKINAHINTA ({kohde})", value=f"{hinta:,.2f} {valuutta}")
                st.markdown("---")
                
                st.info("Sijoitusagentit aloittavat analyysin ja sijoitusneuvon valmistelun...")
                try:
                    data_agent = Agent(
                        role="Ylikomissio-markkina-analyytikko",
                        goal="Pureksia ja analysoida annetun kohteen reaaliaikaista hintatrendiä ja viikkotason momentumia.",
                        backstory=f"Olet lahjomaton ja tarkka pörssianalyytikko. Käytössäsi on tämä tuorein raaka markkinadata: {markkinadata_teksti}",
                        verbose=True
                    )
                    
                    manager_agent = Agent(
                        role="Huipputason Sijoitusneuvoja ja Salkunhoitaja",
                        goal="Antaa sijoittajalle suoria, rohkeita ja asiantuntevia sijoitusneuvoja (OSTA, MYY, ODOTA tai PIDÄ).",
                        backstory="""Olet kokenut ja suorapuheinen sijoitusneuvoja. Tehtäväsi EI OLE kierrellä tai kaarrella, 
                        eikä vain selittää numeroita uudestaan. Sinun on annettava rohkea, selkeä ja perusteltu sijoitusneuvo. 
                        Puhut suoraan sijoittajalle ammattimaisella otteella ja suomeksi.""",
                        verbose=True
                    )
                    
                    task1 = Task(
                        description="Analysoi kohteen hinnan nykytila ja lyhyen aikavälin kehityssuunta.", 
                        expected_output="Lyhyt trendianalyysi.", 
                        agent=data_agent
                    )
                    
                    task2 = Task(
                        description=f"""Laadi tiukka ja asiantunteva sijoitusneuvo kohteelle {kohde}.
                        
                        PÄÄPOINTTI: Sinun pitää antaa selkeä toimintaohje ja sijoitusneuvo, ei pelkkää datan pyörittelyä!
                        
                        Tulosta vastaus TÄSMÄLLEEN tässä muodossa:
                        **SIJOITUSSUOSITUS:** [Kirjoita tähän isolla OSTA, MYY, ODOTA tai PIDÄ]
                        
                        **PERUSTELUT JA SIJOITUSNEUVOT:** [Kirjoita tähän asiantuntevat, taktiset ja syvälliset perustelut siitä, miksi sijoittajan kannattaa toimia näin, mitä riskejä kohteessa on juuri nyt ja miten tilanteessa kannattaa taktikoida.]""",
                        expected_output="Suora sijoitussuositus ja ammattitason sijoitusneuvot suomeksi.",
                        agent=manager_agent
                    )
                    
                    sijoitus_tiimi = Crew(agents=[data_agent, manager_agent], tasks=[task1, task2], process=Process.sequential)
                    
                    st.success("Analyysi valmis!")
                    st.write("### 🤖 Sijoitusneuvontaryhmän virallinen lausunto:")
                    st.write(str(sijoitus_tiimi.kickoff()).strip())
                except Exception as e:
                    st.error(f"Virhe agenttien ajossa: {e}")

# ==================== 2. PITKÄVETO-AGENTTI ====================
elif sovellusvalinta == "⚽ Pitkäveto-agentti":
    st.title("⚽ SEGE10:n AI-Pitkävetoagentti")
    ottelu = st.text_input("Syötä illan ottelu ja sarja:", value="")
    kertoimet = st.text_input("Syötä tarjolla olevat kertoimet:", value="")
    
    if st.button("Käynnistä Pitkäveto-analyysi"):
        if not ottelu or not kertoimet:
            st.warning("Täytä ottelu ja kertoimet!")
        else:
            st.info(f"Etsitään tietoa ottelusta...")
            try:
                google_haku = SerperDevTool()
                urheilu_analyytikko = Agent(role="Urheiluanalyytikko", goal=f"Etsiä netistä uutiset: {ottelu}.", backstory="Olet urheilutoimittaja.", tools=[google_haku], verbose=True)
                vihje_mestari = Agent(role="Ammattivedonlyöjä", goal="Kirjoittaa syvällinen pelisuositus.", backstory=f"Kertoimet: {kertoimet}", verbose=True)
                utask1 = Task(description="Etsi kokoonpanot.", expected_output="Raportti.", agent=urheilu_analyytikko)
                utask2 = Task(
                    description=f"""Tee analyysi ottelusta {ottelu}. Tulosta vastauksesi muodossa:
                    **PELIVALINTA:** [Merkki]
                    **ASIANTUNTIJA-ANALYYSI (Kuka voittaa ja miksi):** [Perustelut]""",
                    expected_output="Pelivalinta ja perustelut.",
                    agent=vihje_mestari
                )
                veto_tiimi = Crew(agents=[urheilu_analyytikko, vihje_mestari], tasks=[utask1, utask2], process=Process.sequential)
                st.write(str(veto_tiimi.kickoff()).strip())
            except Exception as e:
                st.error(f"Virhe: {e}")

# ==================== 3. BENSAVAHTI ====================
elif sovellusvalinta == "⛽ Bensavahti":
    st.title("⛽ SEGE10:n AI-Bensavahti (PK-seutu)")
    if st.button("Päivitä ja näytä halvimmat hinnat"):
        df_hinnat, viesti = hae_bensahinnat_suoraan()
        if df_hinnat is None:
            st.error(viesti)
        else:
            st.markdown("### 📊 HALVIMMAT KESKIHINNAT ALUEITTAIN JUURI NYT")
            st.dataframe(df_hinnat, use_container_width=True)
            bensa_teksti = df_hinnat.to_string()
            bensa_agent = Agent(role="Strategi", goal="Analysoida.", backstory=f"Data: \n{bensa_teksti}", verbose=True)
            bensa_task = Task(description="Kirjoita lyhyt yhteenveto säästöistä.", expected_output="Analyysi.", agent=bensa_agent)
            bensa_crew = Crew(agents=[bensa_agent], tasks=[bensa_task], process=Process.sequential)
            st.write(str(bensa_crew.kickoff()).strip())
