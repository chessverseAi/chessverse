import json
import chess

# Cargar estadísticas
try:
    with open("move_stats.json", "r") as f:
        raw_stats = json.load(f)
        move_stats = {tuple(key.split("::")): value for key, value in raw_stats.items()}
except FileNotFoundError:
    move_stats = {}

def evaluate_move(fen, move_uci):
    board = chess.Board(fen)
    simplified_fen = " ".join(fen.split()[:4])
    key = (simplified_fen, move_uci)

    if key not in move_stats:
        return {
            "frequency": 0,
            "win_rate": 0.0,
            "quality_score": 0.0,
            "visual_effect": "neutral",
            "error": "Movimiento no encontrado"
        }

    data = move_stats[key]
    total = data["total"]
    wins = data["white_wins"] if board.turn == chess.WHITE else data["black_wins"]
    draws = data["draws"]

    win_rate = (wins + 0.5 * draws) / total
    quality_score = (win_rate * 0.7) + (min(total / 100, 1) * 0.3)

    if quality_score >= 0.7:
        effect = "grow"
    elif quality_score <= 0.3:
        effect = "shrink"
    else:
        effect = "neutral"

    return {
        "frequency": total,
        "win_rate": round(win_rate, 3),
        "quality_score": round(quality_score, 3),
        "visual_effect": effect
    }
