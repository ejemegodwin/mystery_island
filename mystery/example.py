map_connections = {
    "Beach": ["Jungle"],
    "Jungle": ["Beach", "Cave"],
    "Cave": ["Jungle", "Old Bridge"],
    "Old Bridge": ["Cave", "Lighthouse"],
    "Lighthouse": ["Old Bridge"]
}

inventory = []

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
        item = input("What item would you like to pick up? ").strip().title()
        if item not in inventory:
            inventory.append(item)
            print(f"You have picked up {item}. Your inventory now contains: {inventory}")
        else:
            print(f"You already have {item} in your inventory.")

        if location == "Beach":
            # Allow the player to collect the Rope
            if "Rope" not in inventory:
                inventory.append("Rope")
                print(f"You have picked up the Rope. Your inventory now contains: {inventory}")
            else:
                print("You already have the Rope in your inventory.")
        else:
            print("There is no Rope available here.")

        if location == "Cave":
            if "Lantern" not in inventory:
                inventory.append("Lantern")
                print(f"You have picked up Lantern. Your inventory now contains: {inventory}")
            else:
                print("You already have Lantern in your inventory.")
        else:
            print("There is no Lantern available here.")

        for item in inventory:
            print(f"You have {item} in your inventory.")

    elif choice == "3":
        print("Thanks for playing Mystery Island!")
        game_running = False

    else:
        print("Invalid choice. Try again.")


# Checks whether the inventory is empty.(if inventory: to check whether the list contains anything.)

if inventory:
    print("Your inventory contains:")
    for item in inventory:
        print(f"- {item}")
else:
    print("Your inventory is empty.")
