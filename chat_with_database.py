"""
FundPilot — CLI chat interface voor multi-database Teleknowledge Connect querying.
Stel vragen in het Nederlands over 6 databases.
"""

from fundpilot_config import create_fundpilot_agent


def main():
    """Start de FundPilot CLI chat."""
    print("🚀 FundPilot Multi-Database Chat Agent starten...")
    print()

    try:
        agent = create_fundpilot_agent()

        print("✅ FundPilot Agent verbonden met Teleknowledge Connect!")
        print("💬 Stel vragen in het Nederlands over je data.")
        print("📊 De agent kan SQL-query's genereren over 6 databases.")
        print()
        print("Voorbeeldvragen:")
        print('  - "Hoeveel tabellen zitten er in elke database?"')
        print('  - "Waar komen onze beste donateurs vandaan?"')
        print('  - "Wat is de retentie na 6 maanden per kanaal?"')
        print('  - "Toon de belgeschiedenis van vandaag"')
        print('  - "Welke campagnes presteren het best?"')
        print()
        print("=" * 50)

        while True:
            try:
                question = input("\n💭 Stel een vraag (of 'stop' om te stoppen): ").strip()

                if question.lower() in ["stop", "quit", "exit", "q"]:
                    print("👋 Tot ziens!")
                    break

                if not question:
                    continue

                print(f"\n🤖 Verwerken: {question}")

                response = agent.ask(question)
                print(f"\n📝 Antwoord: {response}")

            except KeyboardInterrupt:
                print("\n\n👋 Chat onderbroken. Tot ziens!")
                break
            except Exception as e:
                print(f"❌ Fout bij verwerking: {e}")

    except Exception as e:
        print(f"❌ Agent kon niet worden gestart: {e}")
        print()
        print("🔧 Probeer het volgende:")
        print("1. Controleer je .env bestand")
        print("2. Controleer of SQL Server bereikbaar is")
        print("3. Controleer je OpenAI API key")
        print("4. Installeer dependencies:")
        print("   pip install 'vanna[fastapi,mssql,openai,chromadb]' python-dotenv sqlparse")


if __name__ == "__main__":
    main()