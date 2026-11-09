# mystery_island

energy = 5
location = "Beach"

destination = input(
    f"You are currently at {location}. Where would you like to go? "
).strip().title()

if destination in map_connections[location]:
    print("You can travel there!")
    print(f"Your new location is {destination}.")
else:
    print("You cannot travel there!")

    location = destination
    print("You can travel there!")
    print(f"Your new location is {location}.")
else:
    print("You cannot travel there!")

    location = destination
    energy -= 1

    print("You can travel there!")
    print(f"Your new location is {location}.")
    print(f"Energy remaining: {energy}")

else:
    print("You cannot travel there!")

if energy <= 0:
    print("You have run out of energy!")
    print("GAME OVER!")
    break

#Rejection of invalid movement without losing energy.

if destination not in map_connections[location]:
    print("You cannot travel there!")
    print(f"Your current location is still {location}.")
    print(f"Energy remaining: {energy}")