############ Angkan Baidya ############
########### 112309655 ############
########### abaidya ############

from enum import Enum
import random

# Defines possible hazards in the game.
class Hazard(Enum):
    guard = "Guard"
    pit = "Pit"
    bats = "Bats"


# Defines possible actions a player can take.
class Action(Enum):
    move = "move"
    shoot = "shoot"
    stay = "stay"
    startle_guard = "startle_guard"


class Cave:
    def __init__(self):
        self.edges = [[1, 2], [2, 10], [10, 11], [11, 8], [8, 1], [1, 5], [2, 3], [9, 10], [20, 11], [7, 8], [5, 4],
                      [4, 3], [3, 12], [12, 9], [9, 19], [19, 20], [20, 17], [17, 7], [7, 6], [6, 5], [4, 14], [12, 13],
                      [18, 19], [16, 17], [15, 6], [14, 13], [13, 18], [18, 16], [16, 15], [15, 14]]
        self.rooms = {}        
        for i in range(0,21):
            self.rooms[i] = Room(i)
        for i in self.edges:
            self.rooms.get(i[0]).connect(self.rooms.get(i[1]))
        

 
    def add_hazard(self, hazard, count):
        numberstochoosefrom = self.rooms.fromkeys(range(20))
        randomkeys = random.sample(list(numberstochoosefrom),count)
        for i in randomkeys:
            self.rooms.get(i).add(hazard)
        

    def random_room(self):
        return self.rooms.get(random.choice(list(self.rooms)))


    def room_with(self, hazard):
        for  i in self.edges:
            if self.rooms.get(i[0]).has(hazard):
                return self.rooms.get(i[0])
            if self.rooms.get(i[1]).has(hazard):
                return self.rooms.get(i[1])
        return None
        

    def move(self, hazard, frm, to):
            if frm.has(hazard):
                to.add(hazard)
                frm.remove(hazard)
            else:
                raise ValueError("Hazard does not exist")

    def room(self, number):
            if self.rooms.get(number) == None:
                raise KeyError
            else:
                return self.rooms.get(number)
        

    def entrance(self):
        for  i in self.edges:
            if self.rooms.get(i[0]).safe():
                return self.rooms.get(i[0])
            if self.rooms.get(i[1]).safe():
                return self.rooms.get(i[1])


class Room:
    def __init__(self, number):
        self.number = number
        self.hazards = []
        self.neighbors = []

    def has(self, hazard):
        for i in self.hazards:
            if i == hazard:
                return True
        return False

    def add(self, hazard):
        self.hazards.append(hazard)

    def remove(self, hazard):
            flag = False
            count = 0
            for i in self.hazards:
                count = count + 1
                if i == hazard:
                    del self.hazards[count-1]
                    flag = True
            if flag == False:
                raise ValueError
        

    def empty(self):
        if len(self.hazards) == 0:
            return True
        return False

    def safe(self):
        if len(self.hazards) != 0:
            return False
        for i in self.neighbors:
            if len(i.hazards) != 0:
                return False
        return True

    def connect(self, other_room):
        self.neighbors.append(other_room)
        self.neighbors[-1].neighbors.append(self)

    def exits(self):
        if len(self.neighbors) == 0:
            return []
        returnable = []
        for i in self.neighbors:
            returnable.append(i.number)
        return returnable


    def neighbor(self, number):
        if len(self.neighbors) == 0:
            return None
        for i in self.neighbors:
            if i.number == number:
                return i
        return None
        

    def random_neighbor(self):
        if len(self.neighbors) == 0:
            raise IndexError("No neighbors")
        return random.choice(self.neighbors)
       
        


class Player:

    def __init__(self):
       self.senses ={}
       self.encounters = {}
       self.actions = {}
       self.room = None

    def sense(self, hazard, callback):
        self.senses[hazard] = callback



    def encounter(self, hazard, callback):
        self.encounters[hazard] = callback


    def action(self, hazard, callback):
        self.actions[hazard] =callback


    def enter(self, room):
       self.room = room
       if self.room.empty() == False:
           if len(self.room.hazards) == 1:
               return self.encounters.get(self.room.hazards[0])()
           return self.encounters.get(list(self.encounters.keys())[0])()
       

    def explore_room(self):
            for i in self.room.neighbors: 
                for j in i.hazards:
                    self.senses.get(j)()
                

    def act(self, action, destination):
        if self.actions.get(action) == None:
            raise KeyError
        else:
            self.actions.get(action)(destination)
        


class Narrator:
    def __init__(self):
        self.ending_message = None

    def say(self, message):
        print(message)

    def ask(self, question):
        return input(question)

    def tell_story(self, story):
        while not self.ending_message:
            story()
        self.say("-----------------------------------------")
        self.say(self.ending_message)

    def finish_story(self, message):
        self.ending_message = message


class Console:
    def __init__(self, player, narrator):
        self.player = player
        self.narrator = narrator

    def show_room_description(self):
        self.narrator.say("-----------------------------------------")
        self.narrator.say("You are in room #" + str(self.player.room.number))
        self.player.explore_room()
        self.narrator.say("Exits go to: " + ",".join([str(x) for x in self.player.room.exits()]))

    def ask_player_to_act(self):
        actions = {"m": Action.move, "s": Action.shoot}
        self.accepting_player_input(
            lambda command, room_number: self.player.act(actions[command], self.player.room.neighbor(room_number)))

    def accepting_player_input(self, act):
        self.narrator.say("-----------------------------------------")
        command = self.narrator.ask("What do you want to do? (m)ove or (s)hoot?")
        if command not in ["m", "s"]:
            self.narrator.say("INVALID ACTION! TRY AGAIN!")
            return
        try:
            dest = int(self.narrator.ask("Where?"))
            if dest not in self.player.room.exits():
                self.narrator.say("INVALID ACTION! TRY AGAIN!")
                return
        except ValueError:
            self.narrator.say("INVALID ACTION! TRY AGAIN!")
            return
        act(command, dest)

