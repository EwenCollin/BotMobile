import time
from procedural.main import Driver

from training_envs.gymenvs.fwdopt4.gymenv import Env as Classic

env = Classic(init_all=False, max_step=3000)

BOT = True

driver = Driver()

while True:
    done = False
    obs = env.reset()
    for i in range(100000):
        # Predict
        if BOT:
            action = driver.predict(obs)
        else:
            action = env.sample_action()
        # Get reward
        obs, reward, done, info = env.step(action)
        #print(obs)
        # Render
        env.render()

        time.sleep(0.05)
        
        if done:
            break
env.close()