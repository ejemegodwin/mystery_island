map_connections = {
    "Beach": ["Jungle"],
    "Jungle": ["Beach", "Cave"],
    "Cave": ["Jungle", "Old Bridge"],
    "Old Bridge": ["Cave", "Lighthouse"],
    "Lighthouse": ["Old Bridge"]
}

energy = 5
location = "Beach"

game_running = True
while game_running:
    choice = input("What would you like to do? (1-3): ").strip()
    if choice == "1":
        destination = input(
            f"You are currently at {location}. Where would you like to go? "
        ).strip().title()

        if destination in map_connections[location]:
            location = destination
            energy -= 1
            print(f"You have moved to {location}. Energy remaining: {energy}")

            if energy <= 0:
                print("You have run out of energy and cannot move anymore.")
                print("GAME OVER!")
                game_running = False
        else:
            print(f"You cannot move to {destination} from {location}. Please choose a valid destination.")
            print(f"Your location remains {location}. Energy remaining: {energy}")

    elif choice == "2":
        print("Your inventory is empty.")

    elif choice == "3":
        print("Thanks for playing Mystery Island!")
        game_running = False

    else:
        print("Invalid choice. Try again.")