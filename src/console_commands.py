import roy_counter

async def interactive_console(client):
    print("Ready for commands...")

    user_input = input()
    while user_input.lower() != "close":
        if user_input.lower() == "save":
            roy_counter.save_count()
        user_input = input()

    roy_counter.save_count()
    await client.close()