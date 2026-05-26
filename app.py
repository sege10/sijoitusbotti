import streamlit as st
import os

# Pakotetaan Streamlit käyttämään Secrets-avainta CrewAI:lle
if "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

from crewai import Agent, Crew, Process, Task
from crewai_tools import ScrapeWebsiteTool
import yfinance as yf

# Luodaan yksinkertainen työkalu kurssihakuun
def hae_porssitiedot(ticker):
    try:
        data = yf.Ticker(ticker)
        hist = data.history(period="1mo")
        viimeisin_hinta = hist['Close'].iloc[-1]
        return f"Kohteen {ticker} tämänhetkinen hinta on {viimeisin_hinta:.2f}. Viimeisen kuukauden kehitys: {hist['Close'].to_string()}"
    except Exception as e:
        return f"Virhe haettaessa dataa kohteelle {ticker}: {e}"

st.title("🤖 SEGE10:n AI-Sijoitusagentti")
st.write("Tämä tekoälytiimi analysoi reaaliaikaista markkinadataa.")

kohde = st.text_input("Syötä osakkeen tai krypton tunnus (esim. AAPL tai BTC-USD):", "BTC-USD")

if st.button("Käynnistä tekoälyanalyysi"):
    st.info(f"Agentit aloittavat kohteen {kohde} tutkimisen tämän päivän datalla. Odota hetki...")
    
    try:
        # Haetaan reaaliaikainen data valmiiksi tekstiksi agentille
        reaaliaikainen_data = hae_porssitiedot(kohde)
        
        # Agentit
        data_agent = Agent(
            role="Markkinadata-analyytikko",
            goal=f"Analysoida annettua reaaliaikaista pörssidata kohteesta {kohde}.",
            backstory=f"Olet kokenut analyytikko. Saat käyttöösi tämän tuoreen datan: {reaaliaikainen_data}. Tehtäväsi on tulkita tämä data.",
            verbose=True
        )
        
        manager_agent = Agent(
            role="Salkunhoitaja",
            goal="Tehdä selkeä sijoitussuositus tämän päivän tilanteen mukaan.",
            backstory="Olet varovainen salkunhoitaja, joka perustaa päätöksensä vain tuoreisiin faktoihin.",
            verbose=True
        )

        # Tehtävät
        task1 = Task(
            description=f"Käy läpi analyytikon saama reaaliaikainen data kohteesta {kohde} ja tiivistä sen trendi.",
            expected_output="Raportti tämänhetkisestä hintatrendistä.",
            agent=data_agent
        )
        task2 = Task(
            description=f"Tee sijoitussuositus (OSTA/MYY/ODOTA) kohteelle {kohde} tuoreen raportin pohjalta.",
            expected_output="Lopullinen suositus perusteluineen suomeksi tämän päivän markkinatilanteessa.",
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
        st.error(f"Tapahtui virhe. Virhe: {e}")
