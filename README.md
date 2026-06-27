(i forgot to put the source, i'll do it tomorow)
# 🎯 Muda Remote Solver

An intelligent solver and assistant for the **Muda Remote** puzzle minigame.

The application allows players to solve puzzles manually with probability assistance or automatically using an optimized bot that maximizes the expected score.

---

## Features

- 🧠 Intelligent puzzle solver
- 🤖 Automatic Bot Solver
- 🎮 Manual solving mode
- 📊 Real-time probability calculations
- 🔴 Remaining possible Red positions
- 💰 Expected score calculation
- ⚡ Optimized board filtering with caching
- 🖥️ Simple Tkinter graphical interface

---

## Requirements

- Python 3.10 or newer
- Windows 10/11 (recommended)

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/muda-remote-solver.git
cd muda-remote-solver
```

or simply download the ZIP and extract it.

---

### 2. Create a virtual environment (recommended)

Windows

```bash
python -m venv myenv
```

Activate it:

Command Prompt

```cmd
myenv\Scripts\activate
```

PowerShell

```powershell
myenv\Scripts\Activate.ps1
```

If PowerShell blocks execution:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

---

### 3. Install dependencies

This project only uses Python's standard library.

No external packages are required.

---

## Installing the Font

The interface uses a custom font.

1. Open the **font** folder.
2. Double-click the `.ttf` file.
3. Click **Install**.

Or:

- Right-click the font.
- Select **Install for all users**.

Restart the application after installing the font.

---

## Running

Execute:

```bash
python run_oc_solver.py
```

or

```bash
python -m oc_solver.run_oc_solver
```

depending on your project structure.

---

# How to Use

## Manual Mode

1. Start a new puzzle.
2. Click a tile.
3. Select the color revealed in-game.
4. Repeat for every click.
5. The solver automatically updates:
   - Remaining possible boards
   - Remaining Red positions
   - Best recommended move

---

## Bot Mode

Click

```
▶ Bot Solver
```

The bot will automatically:

- choose the best move;
- maximize the expected score;
- stop after finding the Red tile or using all available clicks.

---

# Interface

| Label | Description |
|--------|-------------|
| Score | Current puzzle score |
| Clicks | Number of clicks used |
| Possible Reds | Remaining valid Red locations |
| Status | Solver recommendation or game state |

---

# Project Structure

```
project/
│
├── run_oc_solver.py
│
├── oc_solver/
│   ├── oc_solver_core.py
│   ├── oc_solver_visual.py
│   └── ...
│
├── font/
│   └── YourFont.ttf
│
└── README.md
```

---

# Algorithm

The solver works by:

1. Generating every valid board configuration.
2. Removing impossible boards after every observation.
3. Computing probabilities for every remaining tile.
4. Estimating expected score.
5. Choosing the move with the highest expected value.

Recent optimizations include:

- cached board filtering;
- reduced redundant calculations;
- significantly faster manual interaction.

---

# Troubleshooting

## PowerShell blocks Activate.ps1

Run:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

---

## ModuleNotFoundError

Run the project from its root folder.

---

## Font is not displayed

Install the font manually and restart the application.

---

# License

This project is provided for educational and personal use.
