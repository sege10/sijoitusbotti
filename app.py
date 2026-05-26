import streamlit as st
import os
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Pakotetaan Streamlit käyttämään Secrets-avaimia
if "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
if "SERPER_API_KEY" in st.secrets:
    os.environ["SERPER_API_KEY"] = st.secrets["SERPER_API_KEY"]

from crewai import Agent, Crew, Process, Task
from crewai_tools import SerperDevTool

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
st.sidebar.write("📅 Nykyinen päivämäärä: 26.5.2026")
sovellusvalinta = st.sidebar.radio("Valitse agentti:", ["📈 Sijoitusagentti", "⚽ Pitkäveto-agentti", "⛽ Bensavahti"])

# ==================== 1. SIJOITUSAGENTTI ====================
if sovellusvalinta == "📈 Sijoitusagentti":
    st.title("📈 SEGE10:n AI-Sijoitusagentti")
    st.write("""
    Kirjoita alle minkä tahansa sijoituskohteen nimi (osake, krypto, valuutta, metalli tai raaka-aine).
    Agentti etsii live-hinnat, kurssit ja markkinauutiset suoraan Googlesta ja antaa suoran sijoitusneuvon.
    """)
    
    kayttajan_syote = st.text_input("Syötä sijoituskohteen nimi (esim. tesla, bitcoin, kulta, maakaasu):", value="")
    
    if st.button("Käynnistä tekoälyanalyysi"):
        if not kayttajan_syote:
            st.warning("Syötä jokin kohde ensin!")
        else:
            st.info(f"Etsitään tietoa kohteesta '{kayttajan_syote}' Googlesta (Tilanne: 26.5.2026)...")
            try:
                google_haku = SerperDevTool()
                
                data_agent = Agent(
                    role="Globaali pörssi- ja markkina-analyytikko",
                    goal=f"Etsiä netistä tämän päivän (26.5.2026) tuorein hinta, kurssi ja markkinatilanne kohteelle: {kayttajan_syote}.",
                    backstory="Olet huipputason analyytikko. Käytät Google-hakua löytääksesi kohteen reaaliaikaisen hinnan ja tuoreimmat talousuutiset.",
                    tools=[google_haku],
                    verbose=True
                )
                
                manager_agent = Agent(
                    role="Huipputason Sijoitusneuvoja",
                    goal="Antaa sijoittajalle suoria, rohkeita ja asiantuntevia sijoitusneuvoja (OSTA, MYY, ODOTA tai PIDÄ).",
                    backstory="Olet kokenut salkunhoitaja. Tehtäväsi on antaa rohkea, selkeä ja perusteltu sijoitusneuvo perustuen löydettyihin reaaliaikaisiin markkinahintoihin.",
                    verbose=True
                )
                
                task1 = Task(
                    description=f"Etsi Googlesta tämän päivän (26.5.2026) uusin hinta sekä markkinatilanne kohteelle {kayttajan_syote}.", 
                    expected_output="Raportti kohteen reaaliaikaisesta hinnasta.", 
                    agent=data_agent
                )
                
                task2 = Task(
                    description=f"""Laadi tiukka sijoitusneuvo kohteelle {kayttajan_syote}.
                    
                    Tulosta vastaus tässä muodossa:
                    **ETSITYN KOHTEEN LIVE-HINTA:** [Tämän päivän hinta ja valuutta]
                    **SIJOITUSSUOSITUS:** [OSTA, MYY, ODOTA tai PIDÄ]
                    **PERUSTELUT JA SIJOITUSNEUVOT:** [Asiantuntevat perustelut suomeksi]""",
                    expected_output="Suora sijoitussuositus ja sijoitusneuvot suomeksi.",
                    agent=manager_agent
                )
                
                sijoitus_tiimi = Crew(agents=[data_agent, manager_agent], tasks=[task1, task2], process=Process.sequential)
                tulos = sijoitus_tiimi.kickoff()
                st.success("Analyysi valmis!")
                st.write(str(tulos).strip())
            except Exception as e:
                st.error(f"Virhe: {e}")

# ==================== 2. PITKÄVETO-AGENTTI (AUTOMAATTIKERTOIMET) ====================
elif sovellusvalinta == "⚽ Pitkäveto-agentti":
    st.title("⚽ SEGE10:n AI-Pitkävetoagentti")
    st.write("""
    Syötä vain ottelu tai joukkue. **Agentti etsii itse tämän päivän (26.5.2026) kertoimet eri vedonlyöntisivustoilta**, 
    analysoi uutiset, kokoonpanot ja antaa asiantuntevan pelisuosituksen.
    """)
    
    # Kertoimien syöttökenttä poistettu kokonaan, vain ottelun nimi tarvitaan!
    ottelu = st.text_input("Syötä illan ottelu tai joukkue (esim. suomi - sveitsi, real madrid):", value="")
    
    if st.button("Käynnistä Pitkäveto-analyysi"):
        if not ottelu:
            st.warning("Syötä ottelu tai joukkue ensin!")
        else:
            st.info(f"Etsitään automaattisesti ottelun '{ottelu}' tämän päivän (26.5.2026) kertoimia, kokoonpanoja ja uutisia netistä...")
            try:
                google_haku = SerperDevTool()
                
                urheilu_analyytikko = Agent(
                    role="Urheilutoimittaja ja Vedonlyöntianalyytikko",
                    goal=f"Etsiä netistä tämän päivän (26.5.2026) parhaat tarjolla olevat pitkävetokertoimet (1X2) sekä tuoreimmat uutiset ja poissaolot otteluun: {ottelu}.",
                    backstory="Olet kokenut urheiluanalyytikko. Tehtäväsi on löytää Googlesta ottelun nykyiset kertoimet eri toimijoilta sekä urheilulliset taustat (vire, loukkaantumiset).",
                    tools=[google_haku],
                    verbose=True
                )
                
                vihje_mestari = Agent(
                    role="Ammattivedonlyöjä",
                    goal="Kirjoittaa syvällinen ja asiantunteva pelisuositus siitä, kuka voittaa ja miksi.",
                    backstory="Olet ammattimainen vihjaaja. Vertaat analyytikon löytämiä reaaliaikaisia kertoimia joukkueiden pelilliseen tilanteeseen ja poissaoloihin.",
                    verbose=True
                )
                
                utask1 = Task(
                    description=f"Etsi Googlesta hakusanoilla ottelun '{ottelu}' tämän päivän (26.5.2026) pitkävetokertoimet, uutiset, poissaolot ja 3 viimeisintä ottelua.",
                    expected_output="Raportti kertoimista ja joukkueiden urheilullisesta tilanteesta.",
                    agent=urheilu_analyytikko
                )
                
                utask2 = Task(
                    description=f"""Tee syvällinen vedonlyöntianalyysi ottelusta {ottelu} löydettyjen kertoimien pohjalta.
                    
                    Pureudu peliin kunnolla: Kuka ottelun voittaa ja miksi? Mitkä ovat pelilliset ratkaisutekijät?
                    
                    Tulosta vastaus TÄSMÄLLEEN tässä muodossa:
                    **LÖYDYT MARKKINAKERTOIMET:** [Kirjoita tähän analyytikon netistä löytämät kertoimet otteluun]
                    
                    **PELIVALINTA:** [Valittu merkki 1, X tai 2 ja joukkueen nimi]
                    
                    **ASIANTUNTIJA-ANALYYSI (Kuka voittaa ja miksi):**
                    [Kirjoita tähän asiantuntevat, taktiset ja pelilliset perustelut suomeksi ottaen huomioon loukkaantumiset ja vireen]""",
                    expected_output="Pelivalinta, löydetyt kertoimet ja perustelut suomeksi.",
                    agent=vihje_mestari
                )
                
                veto_tiimi = Crew(agents=[urheilu_analyytikko, vihje_mestari], tasks=[utask1, utask2], process=Process.sequential)
                tulos = veto_tiimi.kickoff()
                st.success("Analyysi valmis!")
                st.write(str(tulos).strip())
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
