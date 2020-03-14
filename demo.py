import berry
flip=False
def rotate(instance, speed):
    global flip
    step=instance.get_speed(speed)
    if instance.scale[0] >= -1.0 and flip == False:
        instance.scale[0]-=step
    else:
        flip=True
    if flip == True:
        instance.scale[0]+=step
        if instance.scale[0] >= 1.0:
            flip=False
            instance.scale[0]=1.0
if __name__ == '__main__':
    game=berry.instance(vsync=1, show_fps=False, req=330)
    light=berry.light_source()
    model=berry.model()
    camera=berry.camera()
    game.bind_light(light)
    game.bind_camera(camera)
    game.bind_model(model)
    game.create_window(name='Berry Engine Demo', x=800, y=600, fullscreen=True)
    game.start()
    while game.alive:
        rotate(game, 2.5)
        game.render()
        if game.key_pressed == 256: #esc key
            game.close()
