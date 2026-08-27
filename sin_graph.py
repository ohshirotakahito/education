import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.colors import hsv_to_rgb
import numpy as np


X = np.linspace(0, 10, 500)
FRAME_COUNT = 100
PHASES = np.linspace(0, 2 * np.pi, FRAME_COUNT)

figure, axis = plt.subplots(figsize=(10, 5.5))
axis.set_xlim(0, 10)
axis.set_ylim(-1.2, 1.2)
axis.set_title("100 shifted sine waves")
axis.set_xlabel("x")
axis.set_ylabel("sin(x + phase)")
axis.axhline(0, color="black", linewidth=0.8)
axis.grid(True, alpha=0.3)
drawn_lines = []
current_line, = axis.plot([], [], linewidth=2.8)


def update(frame: int):
	phase = PHASES[frame]
	color = hsv_to_rgb((frame / (FRAME_COUNT - 1), 0.78, 0.9))
	line, = axis.plot(
		X,
		np.sin(X + phase),
		color=color,
		alpha=0.3,
		linewidth=1.0,
	)
	drawn_lines.append(line)
	current_line.set_data(X, np.sin(X + phase))
	current_line.set_color(color)
	axis.set_title(f"sin(x + phase) | {frame + 1}/{FRAME_COUNT}")
	return [*drawn_lines, current_line]


animation = FuncAnimation(
	figure,
	update,
	frames=FRAME_COUNT,
	interval=45,
	repeat=False,
	blit=False,
)
figure.tight_layout()
figure.savefig("sin_graph.png", dpi=150)

try:
	animation.save("sin_animation.mp4", writer="ffmpeg", fps=20, dpi=120)
	print("Saved video: sin_animation.mp4")
except (FileNotFoundError, OSError, RuntimeError, ValueError):
	animation.save("sin_animation.gif", writer=PillowWriter(fps=20), dpi=100)
	print("FFmpeg was unavailable. Saved animation: sin_animation.gif")

plt.show()
