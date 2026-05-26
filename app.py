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

# DICTIONARY GOOGLE FINANCEA VARTEN
GOOGLE_FINANCE_DICT = {
    "KULTA": "GCW00:COMEX",
    "GOLD": "GCW00:COMEX",
    "HOPEA": "SIW00:COMEX",
    "SILVER": "SIW00:COMEX",
    "ÖLJY": "CLW00:NYMEX",
    "CRUDE OIL": "CLW00:NYMEX",
    "MAAKAASU": "NGW00:NYMEX",
    "BITCOIN": "BTC-USD",
    "BTC": "BTC-USD",
    "ETHEREUM": "ETH-USD",
    "ETH": "ETH-USD",
    "TESLA": "TSLA:NASDAQ",
    "APPLE": "AAPL:NASDAQ",
    "NOKIA": "NOKIA:HEL",
    "SAMPO": "SAMPO:HEL",
    "NESTE": "NESTE:HEL"
}

def hae_google_finance_hinta(hakusana):
    pohja = hakusana.strip().upper()
    ticker = GOOGLE_FINANCE_DICT.get(pohja, pohja)
    if ticker in {"SOL", "XRP", "ADA", "DOT"}:
        ticker = f"{ticker}-USD"
    url = f"https://www.google.com/finance/quote/{ticker}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code != 200:
            return None, "Ei yhteyttä Google Financeen."
        soup = BeautifulSoup(res.text, "html.parser")
        hinta_div = soup.find("div", {"class": "YMlS1d"}) or soup.find("div", {"class": "fxKb6e"})
        if hinta_div:
            return hinta_div.text.strip(), f"Kohteen {hakusana} live-hinta on {hinta_div.text.strip()}."
        return None, "Hintoja ei löytynyt."
    except Exception as e:
        return None, f"Virhe: {e}"

def hae_bensahinnat_livenä():
    try:
        url = "https://www.polttoaine.net/Paa-kaupunkiseutu"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code != 200:
            return None, "Polttoaine.net-sivustolle ei saatu yhteyttä."
        soup = BeautifulSoup(res.text, "html.parser")
        taulukko = soup.find("table", {"id": "LisaaHintojaTable"}) or soup.find("table")
        if not taulukko:
            return None, "Hintataulukkoa ei pystytty lukemaan."
        rivit = taulukko.find_all("tr")
        data_lista = []
        for rivi in rivit[2:]:
            solut = rivi.find_all("td")
            if len(solut) >= 5:
                asema = solut[0].text.strip()
                pvm = solut[1].text.strip()
                e10 = solut[2].text.strip().replace(",", ".")
                e5 = solut[3].text.strip().replace(",", ".")
                di = solut[4].text.strip().replace(",", ".")
                if "26.05." in pvm:
                    try:
                        data_lista.append({"Asema": asema, "95 E10 (€/l)": float(e10), "98 E5 (€/l)": float(e5), "Diesel (€/l)": float(di)})
                    except ValueError:
                        continue
        if not data_lista:
            return None, "Ei riittävästi tämän päivän datamerkintöjä."
        df = pd.DataFrame(data_lista)
        def luokittele_alue(asema_nimi):
            nimi = asema_nimi.lower()
            if "espoo" in nimi or "länsi" in nimi or "lauttasaari" in nimi: return "Länsi-Helsinki / Espoo"
            elif "vantaa" in nimi or "tikkurila" in nimi: return "Vantaa"
            elif "itä" in nimi or "herttoniemi" in nimi or "vuosaari" in nimi or "myllypuro" in nimi: return "Itä-Helsinki"
            else: return "Pohjoinen / Keski-Helsinki"
        df["Alue / Segmentti"] = df["Asema"].apply(luokittele_alue)
        return df.groupby("Alue / Segmentti")[["95 E10 (€/l)", "98 E5 (€/l)", "Diesel (€/l)"]].mean().round(3).reset_index(), "Haettu!"
    except Exception as e:
        return None, f"Virhe: {e}"

# SIVUN RAKENNE
st.set_page_config(page_title="SEGE10 Moni-Agentti", page_icon="🤖", layout="wide")
st.sidebar.title("🤖 SEGE10 AI-Keskus")
st.sidebar.write("📅 Nykyinen päivämäärä: 26.5.2026")
sovellusvalinta = st.sidebar.radio("Valitse agentti:", ["📈 Sijoitusagentti", "⚽ Pitkäveto-agentti", "⛽ Bensavahti"])

# ==================== 1. SIJOITUSAGENTTI ====================
if sovellusvalinta == "📈 Sijoitusagentti":
    st.title("📈 SEGE10:n AI-Sijoitusagentti")
    kayttajan_syote = st.text_input("Syötä sijoituskohteen nimi (esim. kulta, tesla):", value="")
    if st.button("Käynnistä tekoälyanalyysi"):
        if not kayttajan_syote: st.warning("Syötä jokin kohde!")
        else:
            live_hinta, hintateksti_agentille = hae_google_finance_hinta(kayttajan_syote)
            st.markdown("---")
            st.metric(label=f"REAALIAIKAINEN LIVE-HINTA ({kayttajan_syote.upper()})", value=live_hinta if live_hinta else "Uutispohjainen")
            st.markdown("---")
            try:
                google_haku = SerperDevTool()
                data_agent = Agent(role="Moniomaisuus-analyytikko", goal=f"Etsiä uutisia kohteelle: {kayttajan_syote}.", backstory=f"Data: {hintateksti_agentille}", tools=[google_haku], verbose=True)
                manager_agent = Agent(role="Huipputason Sijoitusneuvoja", goal="Antaa suoria sijoitusneuvoja.", backstory="Olet suorapuheinen salkunhoitaja.", verbose=True)
                task1 = Task(description=f"Etsi tuoreimmat uutiset kohteelle {kayttajan_syote}.", expected_output="Raportti uutisista.", agent=data_agent)
                task2 = Task(description=f"Laadi sijoitusneuvo kohteelle {kayttajan_syote}. Muoto:\n**SIJOITUSSUOSITUS:** [OSTA/MYY]\n**PERUSTELUT:** [Teksti]", expected_output="Suositus.", agent=manager_agent)
                st.write(str(Crew(agents=[data_agent, manager_agent], tasks=[task1, task2]).kickoff()).strip())
            except Exception as e: st.error(f"Virhe: {e}")

# ==================== 2. PITKÄVETO-AGENTTI (TIUKKA PARANNUS) ====================
elif sovellusvalinta == "⚽ Pitkäveto-agentti":
    st.title("⚽ SEGE10:n AI-Pitkävetoagentti")
    st.write("Agentti selvittää ottelun urheilulajin, sarjan, kertoimet sekä asiantuntijan todellisen suosikin.")
    ottelu = st.text_input("Syötä ottelu tai joukkue (esim. suomi - sveitsi, vegas - colorado):", value="")
    
    if st.button("Käynnistä Pitkäveto-analyysi"):
        if not ottelu:
            st.warning("Syötä ottelu tai joukkue!")
        else:
            st.info(f"Etsitään automaattisesti ottelun tiedot päivälle 26.5.2026...")
            try:
                google_haku = SerperDevTool()
                
                urheilu_analyytikko = Agent(
                    role="Urheilutoimittaja ja Lajiekspertti",
                    goal=f"Etsiä netistä ottelun '{ottelu}' virallinen URHEILULAJI, SARJA, kertoimet sekä kokoonpanouutiset päivälle 26.5.2026.",
                    backstory="Olet urheilutietopankki. Tehtäväsi on selvittää TÄSMÄLLEEN mikä urheilulaji on kyseessä (esim. Jääkiekon MM-kisat, Valioliiga jne.) ja etsiä siihen kertoimet.",
                    tools=[google_haku],
                    verbose=True
                )
                
                vihje_mestari = Agent(
                    role="Ammattivedonlyöjä ja Pääanalyytikko",
                    goal="Kirjoittaa viiltävä pelisuositus, jossa valitaan selkeä asiantuntijan henkilökohtainen suosikki voittajaksi.",
                    backstory="Olet analyyttinen vihjaaja. Et kiertele tai sano ottelua vain 'tasaiseksi', vaan otat rohkeasti kantaa siihen, kuka on sinun oma suosikkisi ja miksi se voittaa.",
                    verbose=True
                )
                
                utask1 = Task(
                    description=f"Etsi Googlesta ottelun '{ottelu}' tämän päivän (26.5.2026) tiedot: Mikä urheilulaji ja sarja on kyseessä? Mitkä ovat kertoimet ja poissaolot?",
                    expected_output="Raportti lajista, kertoimista ja uutisista.",
                    agent=urheilu_analyytikko
                )
                
                utask2 = Task(
                    description=f"""Tee analyysi ottelusta {ottelu}. Sinun TÄYTYY kertoa laji, sarja ja kuka on sinun henkilökohtainen suosikkisi.
                    
                    Tulosta vastaus TÄSMÄLLEEN tässä muodossa:
                    **URHEILULAJI JA SARJA:** [Esim. Jääkiekko, MM-kisat tai Jalkapallo, Veikkausliiga]
                    
                    **LÖYDYT MARKKINAKERTOIMET:** [Löydetyt kertoimet muodossa 1: X.XX | X: X.XX | 2: X.XX]
                    
                    **ASIANTUNTIJAN OMA SUOSIKKI:** [Kirjoita tähän se joukkue, jota sinä asiantuntijana pidät ottelun todennäköisimpänä voittajana ja suosikkina]
                    
                    **PELIVALINTA VEDONLYÖNTIIN:** [Lopullinen pelimerkki 1, X tai 2]
                    
                    **ASIANTUNTIJA-ANALYYSI (Miksi tämä joukkue voittaa):** [Kirjoita tähän taktiset ja pelilliset perustelut sille, miksi valitsemasi suosikki voittaa ottelun lajikohtaiset säännöt ja pelitavat huomioiden]""",
                    expected_output="Täydellinen vihjeraportti lajitiedoilla ja suosikilla suomeksi.",
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
        df_hinnat, viesti = hae_bensahinnat_livenä()
        if df_hinnat is not None:
            st.dataframe(df_hinnat, use_container_width=True)
            bensa_teksti = df_hinnat.to_string()
            bensa_agent = Agent(role="Strategi", goal="Analysoida.", backstory=f"Data: \n{bensa_teksti}", verbose=True)
            bensa_task = Task(description="Yhteenveto.", expected_output="Teksti.", bensa_agent=bensa_agent)
            st.write(str(Crew(agents=[bensa_agent], tasks=[bensa_task]).kickoff()).strip())
