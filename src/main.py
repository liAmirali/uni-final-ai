from therapist_bot import TherapistBot


def main():
    print("🧪 Testing Graph-Based Therapist Bot")
    print("=" * 50)

    # Create the bot
    bot = TherapistBot()

    bot.graph.get_graph().draw_png("graph.png")

    # Run the conversation
    try:
        # bot.run()
        pass
    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during test: {e}")


if __name__ == "__main__":
    main()
