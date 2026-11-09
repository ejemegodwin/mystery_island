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
    print("Welcome to Mystery Island!")
    destination = input(
        f"You are currently at {location}. Where would you like to go? "
    ).strip().title()

    if destination in map_connections[location]:

        # Update the location here
        location = destination
        #print(f"You are currently at {location}.")


        # Subtract one energy point here
        energy -= 1

        # Display the new location and energy here
        print(f"You have moved to {location}. Energy remaining: {energy}")

        # Check whether energy is zero here
        if energy <= 0:
            print("You have run out of energy and cannot move anymore.")
            print("GAME OVER!")
            game_running = False

    else:

        # Display invalid movement message
        print(f"You cannot move to {destination} from {location}. Please choose a valid destination.") 

        # Display the unchanged location and energy
        print(f"Your location remains {location}. Energy remaining: {energy}")