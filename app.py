from flask import Flask, render_template, request, jsonify
import chess
import chess.svg
import time

app = Flask(__name__)
board = chess.Board()

piece_value = {
    chess.PAWN: 100,
    chess.ROOK: 500,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.QUEEN: 900,
    chess.KING: 20000
}

pawnEvalWhite = [
    0,  0,  0,  0,  0,  0,  0,  0,
    5, 10, 10, -20, -20, 10, 10,  5,
    5, -5, -10,  0,  0, -10, -5,  5,
    0,  0,  0, 20, 20,  0,  0,  0,
    5,  5, 10, 25, 25, 10,  5,  5,
    10, 10, 20, 30, 30, 20, 10, 10,
    50, 50, 50, 50, 50, 50, 50, 50,
    0, 0, 0, 0, 0, 0, 0, 0
]
pawnEvalBlack = list(reversed(pawnEvalWhite))

knightEval = [
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20, 0, 0, 0, 0, -20, -40,
    -30, 0, 10, 15, 15, 10, 0, -30,
    -30, 5, 15, 20, 20, 15, 5, -30,
    -30, 0, 15, 20, 20, 15, 0, -30,
    -30, 5, 10, 15, 15, 10, 5, -30,
    -40, -20, 0, 5, 5, 0, -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50
]

bishopEvalWhite = [
    -20, -10, -10, -10, -10, -10, -10, -20,
    -10, 5, 0, 0, 0, 0, 5, -10,
    -10, 10, 10, 10, 10, 10, 10, -10,
    -10, 0, 10, 10, 10, 10, 0, -10,
    -10, 5, 5, 10, 10, 5, 5, -10,
    -10, 0, 5, 10, 10, 5, 0, -10,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -20, -10, -10, -10, -10, -10, -10, -20
]
bishopEvalBlack = list(reversed(bishopEvalWhite))

rookEvalWhite = [
    0, 0, 0, 5, 5, 0, 0, 0,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    5, 10, 10, 10, 10, 10, 10, 5,
    0, 0, 0, 0, 0, 0, 0, 0
]
rookEvalBlack = list(reversed(rookEvalWhite))

queenEval = [
    -20, -10, -10, -5, -5, -10, -10, -20,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -10, 0, 5, 5, 5, 5, 0, -10,
    -5, 0, 5, 5, 5, 5, 0, -5,
    0, 0, 5, 5, 5, 5, 0, -5,
    -10, 5, 5, 5, 5, 5, 0, -10,
    -10, 0, 5, 0, 0, 0, 0, -10,
    -20, -10, -10, -5, -5, -10, -10, -20
]

kingEvalWhite = [
    20, 30, 10, 0, 0, 10, 30, 20,
    20, 20, 0, 0, 0, 0, 20, 20,
    -10, -20, -20, -20, -20, -20, -20, -10,
    20, -30, -30, -40, -40, -30, -30, -20,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30
]
kingEvalBlack = list(reversed(kingEvalWhite))

kingEvalEndGameWhite = [
    50, -30, -30, -30, -30, -30, -30, -50,
    -30, -30,  0,  0,  0,  0, -30, -30,
    -30, -10, 20, 30, 30, 20, -10, -30,
    -30, -10, 30, 40, 40, 30, -10, -30,
    -30, -10, 30, 40, 40, 30, -10, -30,
    -30, -10, 20, 30, 30, 20, -10, -30,
    -30, -20, -10,  0,  0, -10, -20, -30,
    -50, -40, -30, -20, -20, -30, -40, -50
]
kingEvalEndGameBlack = list(reversed(kingEvalEndGameWhite))

def evaluate_piece(piece: chess.Piece, square: chess.Square, end_game: bool) -> int:
    piece_type = piece.piece_type
    mapping = []
    if piece_type == chess.PAWN:
        mapping = pawnEvalWhite if piece.color == chess.WHITE else pawnEvalBlack
    elif piece_type == chess.KNIGHT:
        mapping = knightEval
    elif piece_type == chess.BISHOP:
        mapping = bishopEvalWhite if piece.color == chess.WHITE else bishopEvalBlack
    elif piece_type == chess.ROOK:
        mapping = rookEvalWhite if piece.color == chess.WHITE else rookEvalBlack
    elif piece_type == chess.QUEEN:
        mapping = queenEval
    elif piece_type == chess.KING:
        if end_game:
            mapping = kingEvalEndGameWhite if piece.color == chess.WHITE else kingEvalEndGameBlack
        else:
            mapping = kingEvalWhite if piece.color == chess.WHITE else kingEvalBlack
    return mapping[square]

def evaluate_board(board: chess.Board) -> float:
    total = 0
    end_game = check_end_game(board)
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is not None:
            value = piece_value[piece.piece_type] + evaluate_piece(piece, square, end_game)
            total += value if piece.color == chess.WHITE else -value
    return total

def check_end_game(board: chess.Board) -> bool:
    queens = 0
    minors = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.piece_type == chess.QUEEN:
            queens += 1
        if piece and (piece.piece_type == chess.BISHOP or piece.piece_type == chess.KNIGHT):
            minors += 1
    if queens == 0 or (queens == 2 and minors <= 1):
        return True
    return False

def is_valid_move(source, destination, board):
    try:
        move = chess.Move.from_uci(source + destination)
        return move in board.legal_moves
    except ValueError:
        return False

def minimax(board, depth, maximizing_player, eval_table):
    if depth == 0 or board.is_game_over():
        eval_value = evaluate_board(board)
        eval_table.append((depth, maximizing_player, None, eval_value))
        return eval_value, chess.Move.null()
    
    if maximizing_player:
        max_eval = float('-inf')
        best_move = None
        for move in board.legal_moves:
            board.push(move)
            eval, _ = minimax(board, depth - 1, False, eval_table)
            board.pop()
            if eval > max_eval:
                max_eval = eval
                best_move = move
            eval_table.append((depth, maximizing_player, move, eval))
        return max_eval, best_move
    else:
        min_eval = float('inf')
        best_move = None
        for move in board.legal_moves:
            board.push(move)
            eval, _ = minimax(board, depth - 1, True, eval_table)
            board.pop()
            if eval < min_eval:
                min_eval = eval
                best_move = move
            eval_table.append((depth, maximizing_player, move, eval))
        return min_eval, best_move


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/board', methods=['GET'])
def get_board():
    return jsonify({'board': chess.svg.board(board, size=300)})

@app.route('/move', methods=['POST'])
def move():
    source = request.form.get('source')
    destination = request.form.get('destination')
    depth = int(request.form.get('depth'))
    
    eval_table = []  # Table to store evaluation values

    if is_valid_move(source, destination, board):
        move = chess.Move.from_uci(source + destination)
        board.push(move)
        
        if board.is_game_over():
            result = board.result()
            return jsonify({'board': chess.svg.board(board, size=300), 'game_over': True, 'result': result})

        time.sleep(1)
        
        _, ai_move = minimax(board, depth, False, eval_table)
        board.push(ai_move)
        
        # Print the evaluation table
        print_eval_table(eval_table)

        if board.is_game_over():
            result = board.result()
            return jsonify({'board': chess.svg.board(board, size=300), 'game_over': True, 'result': result})
    else:
        return jsonify({'error': 'Invalid move!'})

    return jsonify({'board': chess.svg.board(board, size=300)})


def print_eval_table(eval_table):
    # Sort the eval_table by depth
    eval_table.sort(key=lambda x: x[0])
    
    print("Evaluation Table:")
    print("------------------")
    print("| Depth | Maximizer | Move   | Evaluation |")
    print("------------------")
    for depth in range(max(entry[0] for entry in eval_table) + 1):  # Iterate through depths
        depth_entries = [entry for entry in eval_table if entry[0] == depth]  # Filter entries for current depth
        for depth_entry in depth_entries:
            depth, maximizing_player, move, eval_value = depth_entry
            maximizer_str = "Max" if maximizing_player else "Min"
            move_str = str(move) if move else ""
            print(f"|   {depth}   |    {maximizer_str}     | {move_str.ljust(6)} | {eval_value}".ljust(35) + " |")
    print("------------------")



if __name__ == '__main__':
    app.run(debug=True)
