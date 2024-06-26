import gymnasium as gym
import numpy as np

env = gym.make("CartPole-v1", render_mode='human') # 描画しない場合はrender_mode=Noneにする

goal_average_steps = 195 # 195ステップ連続でポールが倒れないことを目指す
max_number_of_steps = 200 # 最大ステップ数
num_consecutive_iterations = 100 # 評価の範囲のエピソード数
num_episodes = 5000
last_time_steps = np.zeros(num_consecutive_iterations)

q_table = np.random.uniform(low=-1, high=1, size=(4**4, env.action_space.n))

def bins(clip_min, clip_max, num):
    return np.linspace(clip_min, clip_max, num + 1)[1:-1]
# np.linspaceは指定された範囲における等間隔数列を返す。

def digitize_state(observation):
# 各値を４個の離散値に変換
    cart_pos, cart_v, pole_angle, pole_v = observation
    digitized = [np.digitize(cart_pos, bins=bins(-2.4, 2.4, 4)),
    np.digitize(cart_v, bins = bins(-3.0, 3.0, 4)),
    np.digitize(pole_angle, bins=bins(-0.2095, 0.2095, 4)),
    np.digitize(pole_v, bins=bins(-2.0, 2.0, 4))]

# 0~255に変換
    return sum([x* (4**i) for i, x in enumerate(digitized)])


def get_action(state, action, observation, reward, episode):
    next_state = digitize_state(observation)

    epsilon = 0.5 * (0.99 ** episode)
    if epsilon <= np.random.uniform(0, 1): # もしepsilonよりランダム値のほうが大きければ
        next_action = np.argmax(q_table[next_state])# q_tableの中で次に取りうる行動の中で最も価値の高いものを
# next_actionに格納する
    else:# 逆に言うと20%の確率でランダムな行動を取る
        next_action = np.random.choice([0, 1])


    # Qテーブルの更新
    alpha = 0.2
    gamma = 0.99
    q_table[state, action] = (1 - alpha) * q_table[state, action] + \
    alpha * (reward + gamma * q_table[next_state, next_action])
    return next_action, next_state

step_list = []
for episode in range(num_episodes):
    # 環境の初期化
    observation, info = env.reset()

    state = digitize_state(observation)
    action = np.argmax(q_table[state])

    episode_reward = 0
    for t in range(max_number_of_steps):
        observation, reward, terminated, truncated, info = env.step(action) # actionを取ったときの環境、報酬、状態が終わったかどうか、デバッグに有益な情報
        if terminated or truncated:
            reward = -200

        action, state = get_action(state, action, observation, reward, episode)
        episode_reward += reward

        if terminated or truncated or t == max_number_of_steps - 1:
            print(f'{episode} finished after {t + 1} time steps / mean {last_time_steps.mean()}')
            last_time_steps = np.hstack((last_time_steps[1:], [t+1])) # 継続したステップ数をステップのリストの最後に加える。np.hstack関数は配列をつなげる関数。
            step_list.append(t+1)
            break

    if (last_time_steps.mean() >= goal_average_steps): # 直近の100エピソードの平均が195以上であれば成功
        print('Episode %d train agent successfully!' % episode)
        break


# ステップ数の推移を描画
import matplotlib.pyplot as plt
plt.plot(step_list)
plt.xlabel('episode')
plt.ylabel('mean_step')
plt.show()
