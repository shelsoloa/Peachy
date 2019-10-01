# FOREWORD

### What is Peachy?
Peachy is a python game development framework. Peachy was made because developing games in python is currently lacking. Peachy is meant to bridge the game between writing your entire

### Why not unity?
Because I like to program. Peachy is not the fastest development library out there, nor is it the fastest. But I am a firm believer that the development process must be enjoyable, otherwise, what's the point. Peachy is for python developers who want to make games, but dont want to deal with C++, Javascript, or heaven forbid GML.

Hopefully, peachy will reach a point that it is fully featured and viable for commercial indie games. But we will see.

---

# BUILDING BLOCKS
> `WORLD -{ ROOM -{ ENTITY } }`

Peachy follows a Entity/World/Room structure. And to explain that we first need to break down what each of those are.

### Entities
    peachy.Entity
An entity is defined in peachy as any object that impacts the player or room. Entites are updated and rendered every frame.

###### Examples of entities
- Player
- Lightbulb

###### Related
 - Collision Detection
 - Rendering

### Rooms
A room is how peachy defines the canvas/stage. A room is where all the action for your game
takes place. Every entity that is active and displayed to the screen is being held within the current
Room. Depending on the game you are making, you could have 1 or hundreds of rooms.

For example:
    Simple games like Tetris would have only 1 room.

##### Custom Rooms
For sure you can create custom rooms? Let's say you have a level in your game that requires a special shader to
be applied to it, well then you may create a room for that level.

Rooms hold your entities. Really, they are nothing more than fancy lists. I use rooms as level content. Loading
assets for a level. Any level specific logic. Rooms could be: LevelOneRoom,

### Worlds
Worlds encapsulate Rooms. The difference between rooms and worlds is simple and very important
to understanding the design decisions behind peachy. Worlds are for engine logic. Rooms are for gameplay logic.

#### Changing Worlds
You can access rooms by their name (World.name) in the Engine.

    engine.change_world(World.name)
Worlds hold rooms and control the overall flow of your game. Worlds could be: GameplayWorld, MainMenuWorld

---

# INITIALIZING
Worlds are held within the Engine which is the topmost container for peachy. The engine is in charge of:
- running the game loop
- holding and changing worlds
- initializing configs
- setting the window size
- toggling fullscreen
- enabling debug mode

# GRAPHICS
Rendering is handled using pygame. Assets are loaded through peachy.fs.
For a list of all the operations that you can do, checkout reference/peachy.graphics
