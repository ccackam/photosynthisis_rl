from photosynthisis_env import PhotosynthisisEnv

print("Let's Play Photosynthisis!")

game = PhotosynthisisEnv(prespecified_players=[PhotosynthisisEnv.old_ai,None,None,None],animate=True)

_,r,_,_ = game.step(None)

print("\nGood Game!")
