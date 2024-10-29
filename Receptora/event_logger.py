def save_event(protocol, event_data):
    with open("event_log.txt", "a") as file:
        file.write(f"{protocol} Event: {event_data}\n")
    print(f"Event saved to event_log.txt: {event_data}")
