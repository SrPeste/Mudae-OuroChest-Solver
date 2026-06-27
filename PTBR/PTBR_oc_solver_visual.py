"""
Visual Mudae $oc Chest solver — bot em tempo real.
Run: python oc_solver_visual.py
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional, Tuple

from PTBR_oc_solver_core import (
    CENTER,
    COLOR_CYCLE,
    Color,
    GRID_SIZE,
    PuzzleSession,
    SolverState,
    TOTAL_RED_POSITIONS,
    new_random_session,
)

Pos = Tuple[int, int]
CELL = 72
PAD = 8


class OcSolverApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Mudae $oc Chest Solver")
        self.configure(bg="#1a1a2e")
        self.resizable(False, False)

        self.session: Optional[PuzzleSession] = None
        self.solver = SolverState()
        self.bot_running = False
        self.bot_delay_ms = 900
        self.cell_widgets: Dict[Pos, tk.Canvas] = {}

        self._build_ui()
        self.new_game()

    def _build_ui(self) -> None:
        main = tk.Frame(self, bg="#1a1a2e", padx=16, pady=16)
        main.pack()

        left = tk.Frame(main, bg="#1a1a2e")
        left.pack(side=tk.LEFT)

        title = tk.Label(
            left,
            text="$oc Chest — Puzzle Solver",
            font=("Segoe UI", 14, "bold"),
            fg="#eaeaea",
            bg="#1a1a2e",
        )
        title.pack(anchor="w")

        rules = tk.Label(
            left,
            text=(
                "Laranja: adjacente (dist. 1) · Amarelo: linha diagonal "
                "(qualquer dist.) · Verde: linha/coluna · Teal: linha/col/diag · "
                "Azul: fora · Vermelho nunca no centro"
            ),
            font=("Segoe UI", 8),
            fg="#888",
            bg="#1a1a2e",
            wraplength=GRID_SIZE * CELL + PAD * 2,
        )
        rules.pack(anchor="w", pady=(4, 12))

        grid_frame = tk.Frame(left, bg="#16213e", padx=PAD, pady=PAD)
        grid_frame.pack()

        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                pos = (r, c)
                cv = tk.Canvas(
                    grid_frame,
                    width=CELL,
                    height=CELL,
                    bg="#0f3460",
                    highlightthickness=1,
                    highlightbackground="#333",
                )
                cv.grid(row=r, column=c, padx=2, pady=2)
                cv.bind("<Button-1>", lambda e, p=pos: self.on_left_click(p))
                cv.bind("<Button-3>", lambda e, p=pos: self.on_right_click(p))
                self.cell_widgets[pos] = cv

        btn_row = tk.Frame(left, bg="#1a1a2e", pady=12)
        btn_row.pack(fill=tk.X)

        self.btn_new = tk.Button(
            btn_row,
            text="Nova partida",
            command=self.new_game,
            bg="#e94560",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT,
            padx=10,
            pady=6,
        )
        self.btn_new.pack(side=tk.LEFT, padx=4)

        self.btn_bot = tk.Button(
            btn_row,
            text="▶ Bot resolver",
            command=self.toggle_bot,
            bg="#533483",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT,
            padx=10,
            pady=6,
        )
        self.btn_bot.pack(side=tk.LEFT, padx=4)

        self.btn_reveal = tk.Button(
            btn_row,
            text="Revelar solução",
            command=self.reveal_solution,
            bg="#444",
            fg="white",
            font=("Segoe UI", 10),
            relief=tk.FLAT,
            padx=10,
            pady=6,
        )
        self.btn_reveal.pack(side=tk.LEFT, padx=4)

        speed_row = tk.Frame(left, bg="#1a1a2e")
        speed_row.pack(fill=tk.X, pady=4)
        tk.Label(
            speed_row,
            text="Velocidade bot:",
            fg="#aaa",
            bg="#1a1a2e",
            font=("Segoe UI", 9),
        ).pack(side=tk.LEFT)
        self.speed_scale = tk.Scale(
            speed_row,
            from_=200,
            to=2000,
            orient=tk.HORIZONTAL,
            length=180,
            showvalue=True,
            bg="#1a1a2e",
            fg="#eaeaea",
            highlightthickness=0,
            command=self._on_speed,
        )
        self.speed_scale.set(self.bot_delay_ms)
        self.speed_scale.pack(side=tk.LEFT, padx=8)

        right = tk.Frame(main, bg="#1a1a2e")
        right.pack(side=tk.LEFT, fill=tk.BOTH, padx=(20, 0))

        self.lbl_status = tk.Label(
            right,
            text="",
            font=("Segoe UI", 11, "bold"),
            fg="#4ecca3",
            bg="#1a1a2e",
            wraplength=280,
            justify=tk.LEFT,
        )
        self.lbl_status.pack(anchor="w")

        self.lbl_score = tk.Label(
            right,
            text="Pontuação: 0 SP",
            font=("Segoe UI", 12, "bold"),
            fg="#ffd369",
            bg="#1a1a2e",
        )
        self.lbl_score.pack(anchor="w", pady=(8, 4))

        self.lbl_clicks = tk.Label(
            right,
            text="Cliques: 0 / 5",
            font=("Segoe UI", 10),
            fg="#ccc",
            bg="#1a1a2e",
        )
        self.lbl_clicks.pack(anchor="w")

        self.lbl_reds = tk.Label(
            right,
            text=f"Reds possíveis: 24/{TOTAL_RED_POSITIONS}",
            font=("Segoe UI", 10),
            fg="#ccc",
            bg="#1a1a2e",
        )
        self.lbl_reds.pack(anchor="w", pady=(4, 12))

        tk.Label(
            right,
            text="Log do bot",
            font=("Segoe UI", 10, "bold"),
            fg="#eaeaea",
            bg="#1a1a2e",
        ).pack(anchor="w")

        log_frame = tk.Frame(right, bg="#16213e")
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(
            log_frame,
            width=34,
            height=18,
            bg="#0f3460",
            fg="#eaeaea",
            font=("Consolas", 9),
            relief=tk.FLAT,
            wrap=tk.WORD,
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.configure(state=tk.DISABLED)

        hint = tk.Label(
            right,
            text="Manual: clique esquerdo cicla cor · direito limpa célula",
            font=("Segoe UI", 8),
            fg="#666",
            bg="#1a1a2e",
            wraplength=280,
        )
        hint.pack(anchor="w", pady=(8, 0))

    def _on_speed(self, val: str) -> None:
        self.bot_delay_ms = int(float(val))

    def log(self, msg: str) -> None:
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def new_game(self) -> None:
        self.bot_running = False
        self.btn_bot.configure(text="▶ Bot resolver")
        self.session = new_random_session()
        self.solver = SolverState()
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.configure(state=tk.DISABLED)
        self.log("Nova partida — tabuleiro oculto gerado.")
        self.refresh_all()

    def reveal_solution(self) -> None:
        if not self.session:
            return
        self.bot_running = False
        self.btn_bot.configure(text="▶ Bot resolver")
        self.refresh_all(show_hidden=True)
        self.log("Solução revelada (vermelho real).")

    def toggle_bot(self) -> None:
        if not self.session:
            return
        if self.session.found_red or self.session.remaining_clicks() <= 0:
            self.log("Partida já terminada.")
            return
        self.bot_running = not self.bot_running
        self.btn_bot.configure(
            text="⏸ Parar bot" if self.bot_running else "▶ Bot resolver"
        )
        if self.bot_running:
            self.log("Bot iniciado — analisando melhor jogada...")
            self.bot_step()

    def bot_step(self) -> None:
        if not self.bot_running or not self.session:
            return
        if self.session.found_red or self.session.remaining_clicks() <= 0:
            self.bot_running = False
            self.btn_bot.configure(text="▶ Bot resolver")
            return

        pos = self.solver.recommend_click()
        if pos is None:
            self.log("Sem jogada válida (configuração inválida?).")
            self.bot_running = False
            self.btn_bot.configure(text="▶ Bot resolver")
            return

        reason = self.solver.recommendation_reason(pos)
        self.log(f"→ Analisando: {reason}")
        self.highlight_cell(pos, "#ffffff")
        self.after(400, lambda: self._bot_execute_click(pos))

    def _bot_execute_click(self, pos: Pos) -> None:
        if not self.bot_running or not self.session:
            return
        try:
            color = self.session.click(pos)
            self.solver.add_observation(pos, color)
            self.log(
                f"   Clique em ({pos[0]},{pos[1]}) → "
                f"{color.label_pt} (+{color.value_sp} SP)"
            )
            if color == Color.RED:
                self.log("   ★ Vermelho encontrado! +150 SP")
            self.refresh_all()
            if self.session.found_red:
                self.log(f"   Partida ganha! Total: {self.session.score} SP")
                self.bot_running = False
                self.btn_bot.configure(text="▶ Bot resolver")
                return
            if self.session.remaining_clicks() <= 0:
                self.log(
                    f"   Sem cliques restantes. Total: {self.session.score} SP"
                )
                self.bot_running = False
                self.btn_bot.configure(text="▶ Bot resolver")
                return
            self.after(self.bot_delay_ms, self.bot_step)
        except RuntimeError as e:
            self.log(f"   Erro: {e}")
            self.bot_running = False
            self.btn_bot.configure(text="▶ Bot resolver")

    def on_left_click(self, pos: Pos) -> None:
        if self.bot_running:
            return
        # Manual mode: cycle colors for deduction (mudaehelper style)
        if pos in self.solver.observations:
            cur = self.solver.observations[pos]
            idx = COLOR_CYCLE.index(cur)
            nxt = COLOR_CYCLE[(idx + 1) % len(COLOR_CYCLE)]
            self.solver.observations[pos] = nxt
        else:
            self.solver.observations[pos] = Color.BLUE
            self.solver.clicked.add(pos)
        self.refresh_all(manual=True)

    def on_right_click(self, pos: Pos) -> None:
        if self.bot_running:
            return
        if pos in self.solver.observations:
            del self.solver.observations[pos]
            self.solver.clicked.discard(pos)
        self.refresh_all(manual=True)

    def highlight_cell(self, pos: Pos, ring: str) -> None:
        cv = self.cell_widgets[pos]
        cv.configure(highlightbackground=ring, highlightthickness=3)

    def refresh_all(self, manual: bool = False, show_hidden: bool = False) -> None:
        if self.session is None:
            return

        # Calcula os boards apenas uma vez
        boards = self.solver.matching_boards()
        valid = bool(boards)

        # Evita chamar matching_boards() novamente
        possible_reds = {b.red for b in boards}

        # Redesenha apenas as células
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                self.draw_cell(
                    (r, c),
                    manual=manual,
                    show_hidden=show_hidden,
                    valid=valid,
                )

        # Atualiza informações
        score = self.session.score
        clicks_used = len(self.session.clicks)

        self.lbl_score.configure(
            text=f"Pontuação: {score} SP"
        )

        self.lbl_clicks.configure(
            text=f"Cliques: {clicks_used} / {self.session.max_clicks}"
        )

        self.lbl_reds.configure(
            text=f"Reds possíveis: {len(possible_reds)}/{TOTAL_RED_POSITIONS}"
        )

        # Atualiza status
        if manual:
            if not valid:
                status = "⚠ Configuração inválida — revise as cores."
                color = "#e94560"
            else:
                # ALTERE recommend_click para receber boards
                rec = self.solver.recommend_click()
                
                if rec:
                    status = self.solver.recommendation_reason(rec)
                    color = "#4ecca3"
                else:
                    status = "Sem recomendação."
                    color = "#888"

        elif self.session.found_red:
            status = "Vermelho encontrado! Melhor resultado."
            color = "#4ecca3"

        elif clicks_used >= self.session.max_clicks:
            status = f"Fim dos {self.session.max_clicks} cliques — {score} SP total."
            color = "#ffd369"

        elif self.bot_running:
            status = "Bot resolvendo..."
            color = "#a29bfe"

        else:
            status = "Clique em ▶ Bot resolver ou defina cores manualmente."
            color = "#888"

        self.lbl_status.configure(text=status, fg=color)

    def draw_cell(
        self,
        pos: Pos,
        manual: bool,
        show_hidden: bool,
        valid: bool,
    ) -> None:
        cv = self.cell_widgets[pos]
        cv.delete("all")
        r, c = pos
        cx, cy = CELL // 2, CELL // 2
        radius = CELL // 2 - 10

        is_center = pos == CENTER
        clicked_in_game = pos in (self.session.clicks if self.session else [])

        cv.configure(bg="#0f3460", highlightbackground="#333", highlightthickness=1)

        color: Optional[Color] = None

        if show_hidden and self.session:
            color = self.session.board.cells[pos]
        elif clicked_in_game and self.session:
            color = self.session.board.cells[pos]
        elif manual and pos in self.solver.observations:
            color = self.solver.observations[pos]

        if color:
            cv.create_oval(
                cx - radius, cy - radius, cx + radius, cy + radius,
                fill=color.hex, outline="#fff", width=2,
            )
            if clicked_in_game:
                cv.create_text(
                    cx, cy - radius - 2, text="✓", fill="#4ecca3",
                    font=("Segoe UI", 10, "bold"),
                )
        else:
            p_red = 0.0 if is_center else self.solver.red_probability(pos)
            if valid and p_red > 0:
                cv.create_oval(
                    cx - radius, cy - radius, cx + radius, cy + radius,
                    fill="#2a2a4a", outline="#555", width=1,
                )
                pct = f"{int(p_red * 100)}%"
                cv.create_text(
                    cx, cy, text=pct, fill="#888",
                    font=("Segoe UI", 9, "bold"),
                )
            else:
                cv.create_text(
                    cx, cy, text="?" if not is_center else "≠R",
                    fill="#555",
                    font=("Segoe UI", 14 if not is_center else 10),
                )

        if is_center and not color:
            cv.create_text(
                cx, cy + radius + 2, text="sem red", fill="#666",
                font=("Segoe UI", 7),
            )


def main() -> None:
    app = OcSolverApp()
    app.mainloop()


if __name__ == "__main__":
    main()
