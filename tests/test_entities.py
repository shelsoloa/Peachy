import peachy

engine = None
world = None
room = None


def test_startup():
    global engine
    global world
    global room

    engine = peachy.Engine()
    world = engine.add_world(peachy.World('Test'))
    room = world.room

    for i in range(100):
        room.add(peachy.Entity())

    assert len(room) == 100


def test_naming():
    t = room[0]
    t.name = 'test'
    assert t == room.get_name('test')
    t.name = ''


def test_grouping():
    # ents = room.entities[0:10]
    # ents.clear()
    pass
