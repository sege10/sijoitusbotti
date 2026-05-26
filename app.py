import streamlit as st
import os

# Pakotetaan Streamlit käyttämään Secrets-avainta CrewAI:lle
if "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

from crewai import Agent, Crew, Process, Task

st.title("🤖 SEGE10:n AI-Sijoitusagentti")
st.write("Tämä tekoälytiimi analysoi markkinadataa puolestasi.")

kohde = st.text_input("Syötä osakkeen tai krypton tunnus (esim. AAPL tai BTC-USD):", "BTC-USD")

if st.button("Käynnistä tekoälyanalyysi"):
    st.info(f"Agentit aloittavat kohteen {kohde} tutkimisen. Odota hetki...")
    
    try:
        # Agentit (Uusi CrewAI käyttää oletuksena gpt-4o-modelia, kunhan API-avain on ympäristössä)
        data_agent = Agent(
            role="Markkinadata-analyytikko",
            goal=f"Hakea ja analysoida kohteen {kohde} reaaliaikaista hintadataa.",
            backstory="Olet kokenut analyytikko, joka löytää datasta olennaiset trendit.",
            verbose=True
        )
        manager_agent = Agent(
            role="Salkunhoitaja",
            goal="Tehdä selkeä sijoitussuositus.",
            backstory="Olet varovainen salkunhoitaja, joka perustaa päätöksensä vain faktoihin.",
            verbose=True
        )

        # Tehtävät
        task1 = Task(
            description=f"Analysoi kohteen {kohde} viimeisimmät hintamuutokset netistä.",
            expected_output="Raportti hintatrendistä.",
            agent=data_agent
        )
        task2 = Task(
            description=f"Tee sijoitussuositus (OSTA/MYY/ODOTA) kohteelle {kohde} saamasi raportin pohjalta.",
            expected_output="Lopullinen suositus perusteluineen suomeksi.",
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
        st.error(f"Tapahtui virhe. Varmista, että Secrets-asetuksissa on oikea OpenAI-avain. Virhe: {e}")
