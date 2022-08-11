from wave_function_collapse_v2 import *

def test_initialisation():
    path = Path('canvas.png')
    assert path.is_file()
    assert canvas.size == (36, 24)
    for row in tile_array:
        for tile in row:
            assert isinstance(tile, Tile)

def test_draw_onto_canvas():
    draw_onto_canvas(
        rand_y := choice(range(len(tile_array))),
        rand_x := choice(range(len(tile_array[0]))),
        rand_state := choice(tuple(TILE_STATES))
        )
    crop_rect = canvas.crop((3*rand_x, 3*rand_y, 3*rand_x+3, 3*rand_y+3))
    rect1 = list(Image.Image.getdata(crop_rect))
    rect2 = list(Image.Image.getdata(TILE_SET[rand_state]))
    rect2 = [pix[:3] for pix in rect2]
    assert rect1 == rect2

def test_tile_methods():
    rand_y = choice(range(len(tile_array)))
    rand_x = choice(range(len(tile_array[0])))

    test_subject = tile_array[rand_y][rand_x]
    num_of_states = len(test_subject.superpositions)

    # Test collapse()
    test_subject.collapse()
    assert isinstance(test_subject.superpositions, str)

    # Test propogate() and reduce_states()
    for dir_index in range(4):
        dir_y = DIRS_Y[dir_index]
        dir_x = DIRS_X[dir_index]

        if -1 < test_subject.y + dir_y < len(tile_array) \
        and -1 < test_subject.x + dir_x < len(tile_array[0]):
            target_tile: Tile = tile_array[test_subject.y + dir_y][test_subject.x + dir_x]
            assert len(target_tile.superpositions) < num_of_states

    