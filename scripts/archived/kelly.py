import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style="darkgrid")
plt.style.use("dark_background")

starting_capital = 1500
games = 50
odds = 2.0
p_win = 0.651  # model accuracy
capital = [starting_capital]

for _ in range(games):
    f = 0.5 * ((odds-1)*p_win - (1-p_win)) / (odds-1)  # half Kelly
    bet = capital[-1] * f
    win = np.random.rand() < p_win
    capital.append(capital[-1] + bet if win else capital[-1] - bet)

plt.figure(figsize=(12,6))
plt.plot(capital, marker='o', color='cyan')
plt.title("🏦 Capital Growth Over Games")
plt.xlabel("Game Number")
plt.ylabel("Capital (PLN)")
plt.show()
print(f"Final Capital after {games} games: {capital[-1]:.2f} PLN")