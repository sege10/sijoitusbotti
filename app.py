import streamlit as st
import yfinance as yf
from crewai import Agent, Crew, Process, Task
from crewai.tools import tool
from langchain_openai import ChatOpenAI

st.title("🤖 SEGE10:n AI-Sijoitusagentti")
st.write("Tämä tekoälytiimi analysoi markkinadataa ja uutisia puolestasi.")

# Käyttöliittymän hakukenttä ja nappi
kohde = st.text_input("Syötä osakkeen tai krypton tunnus (esim. AAPL tai BTC-USD):", "BTC-USD")

if st.button("Käynnistä tekoälyanalyysi"):
    st.info(f"Agentit aloittavat kohteen {kohde} tutkimisen. Odota hetki...")
    
    try:
        # Haetaan tekoälyavain taustajärjestelmästä
        llm = ChatOpenAI(model="gpt-4o")

        # Työkalu markkinadatan hakuun
        @tool("Hae markkinadata")
        def hae_markkinadata(ticker: str) -> str:
            ticker_data = yf.Ticker(ticker)
            hist = ticker_data.history(period="14d")
            info = ticker_data.info
            nykyinen_hinta = info.get("currentPrice", info.get("regularMarketPrice", "Ei saatavilla"))
            return f"Nykyinen hinta: {nykyinen_hinta}\n\nViimeisimmät sulkemishinnat:\n{hist['Close'].to_string()}"

        # Agentit
        data_agent = Agent(
            role="Markkinadata-analyytikko",
            goal="Hakea ja analyzeerata reaaliaikaista dataa.",
            tools=[hae_markkinadata],
            verbose=True,
            llm=llm
        )
        manager_agent = Agent(
            role="Salkunhoitaja",
            goal="Tehdä sijoitussuositus.",
            verbose=True,
            llm=llm
        )

        # Tehtävät
        task1 = Task(
            description=f"Käytä työkalua kohteelle {kohde}. Analysoi hintatrendi.",
            expected_output="Raportti trendistä.",
            agent=data_agent
        )
        task2 = Task(
            description=f"Tee sijoitussuositus (OSTA/MYY/ODOTA) kohteelle {kohde} data-agentin raportin pohjalta.",
            expected_output="Lopullinen suositus perusteluineen.",
            agent=manager_agent
        )

        # Crew-tiimi kasaan ja käyntiin
        sijoitus_tiimi = Crew(
            agents=[data_agent, manager_agent],
            tasks=[task1, task2],
            process=Process.sequential
        )
        
        tulos = sijoitus_tiimi.kickoff()
        st.success("Analyysi valmis!")
        st.write(tulos)
        
    except Exception as e:
        st.error(f"Tapahtui virhe. Tarkista, että olet lisännyt OpenAI API-avaimen asetuksiin. Virhe: {e}")
