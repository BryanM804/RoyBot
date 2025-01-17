import roy_counter

async def handle_ready(client):
    print("Bot Ready!")
    print(f"Roys to date: {roy_counter.roy_count}")
    # await console_commands.interactive_console(client)