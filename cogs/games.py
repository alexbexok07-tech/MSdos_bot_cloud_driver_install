import discord
from discord.ext import commands
import chess
import random
import string

class Games(commands.Cog):
    # Allows games to be initialized across any channel sector
    ignore_global_check = True

    def __init__(self, bot):
        self.bot = bot
        # Storage schema: { match_code: { "board": chess.Board(), "player_w": id, "player_b": id, "mode": "ai"/"player", "difficulty": "easy"/"medium" } }
        self.active_chess = {}

    def generate_match_code(self) -> str:
        """Generates a unique 5-character alphanumeric uppercase key."""
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
            if code not in self.active_chess:
                return code

    def render_board(self, board: chess.Board) -> str:
        """Renders the chess board state into a retro MS-DOS text grid."""
        rows = []
        board_str = str(board)
        lines = board_str.split("\n")
        
        rows.append("   A B C D E F G H")
        rows.append("  +----------------")
        for idx, line in enumerate(lines):
            rank_num = 8 - idx
            rows.append(f"{rank_num} | {line}")
        rows.append("  +----------------")
        rows.append("   A B C D E F G H")
        
        # Determine who is next to move
        turn = "White (User)" if board.turn == chess.WHITE else "Black (Opponent/AI)"
        rows.append(f"\nSTATUS: {turn} to act.")
        if board.is_check():
            rows.append("⚠️ WARNING: King is under direct check!")
            
        return "```\n" + "\n".join(rows) + "\n```"

    def execute_ai_move(self, board: chess.Board, difficulty: str):
        """Calculates and executes a move for the internal AI engine."""
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return

        if difficulty == "easy" or len(legal_moves) == 1:
            chosen_move = random.choice(legal_moves)
        else:
            # Medium/Hard: Prioritize captures and checks, otherwise fallback to random
            scored_moves = []
            for move in legal_moves:
                score = 0
                if board.is_capture(move): score += 3
                board.push(move)
                if board.is_check(): score += 2
                board.pop()
                scored_moves.append((score, move))
            
            # Sort by highest score first
            scored_moves.sort(key=lambda x: x[0], reverse=True)
            chosen_move = scored_moves[0][1]

        board.push(chosen_move)

    # --- CHESS CORE COMMANDS ---

    @commands.command(name="play_chess", help="Initialize a tactical chess terminal. Syntax: *play_chess <ai/player> [easy/medium]")
    async def play_chess(self, ctx, mode: str, difficulty: str = "easy"):
        mode = mode.lower()
        difficulty = difficulty.lower()

        if mode not in ["ai", "player"]:
            return await ctx.send("❌ **[SYS_ERR]** Invalid mode. Choose either `ai` or `player`.")

        match_code = self.generate_match_code()
        
        if mode == "ai":
            self.active_chess[match_code] = {
                "board": chess.Board(),
                "player_w": ctx.author.id,
                "player_b": "AI",
                "mode": "ai",
                "difficulty": difficulty
            }
            await ctx.send(f"🤖 **[KERNEL]** Local AI Engine instance initialized. **Difficulty: {difficulty.upper()}**.")
            await ctx.send(self.render_board(self.active_chess[match_code]["board"]) + f"\nUse `*move_chess {match_code} <coordinates>` (e.g., `*move_chess {match_code} e2e4`) to play.")
        
        elif mode == "player":
            self.active_chess[match_code] = {
                "board": chess.Board(),
                "player_w": ctx.author.id,
                "player_b": None,
                "mode": "player",
                "difficulty": None
            }
            await ctx.send(
                f"🎲 **[MULTI_LOBBY]** Match session generated successfully.\n"
                f"Target opponent must execute: `*accept_chess {match_code}` to bridge connections."
            )

    @commands.command(name="accept_chess", help="Connect to an open multiplayer matchmaking terminal slot.")
    async def accept_chess(self, ctx, code: str):
        code = code.upper()
        if code not in self.active_chess:
            return await ctx.send("❌ **[SYS_ERR]** Specified match execution matrix could not be resolved.")

        game = self.active_chess[code]
        if game["mode"] != "player":
            return await ctx.send("❌ **[SYS_ERR]** Target terminal instance is configured for solitary execution (AI mode).")
        if game["player_b"] is not None:
            return await ctx.send("❌ **[SYS_ERR]** Target multiplayer terminal is already fully occupied.")
        if game["player_w"] == ctx.author.id:
            return await ctx.send("❌ **[SYS_ERR]** Loopback error: You cannot register as your own opponent.")

        game["player_b"] = ctx.author.id
        await ctx.send(f"⚔️ **[LINK_ESTABLISHED]** {ctx.author.mention} has linked into session **{code}** as Black!")
        await ctx.send(self.render_board(game["board"]) + f"\nUse `*move_chess {code} <coordinates>` to play.")

    @commands.command(name="move_chess", help="Transmit positional coordinate updates to a live game instance.")
    async def move_chess(self, ctx, code: str, move_str: str):
        code = code.upper()
        if code not in self.active_chess:
            return await ctx.send("❌ **[SYS_ERR]** Session context missing or terminated.")

        game = self.active_chess[code]
        board = game["board"]

        # Authority Validation Gate
        current_turn_player = game["player_w"] if board.turn == chess.WHITE else game["player_b"]
        if ctx.author.id != current_turn_player:
            return await ctx.send("🛑 **[ACCESS_DENIED]** It is currently your opponent's processing window.")

        # Parse standard chess coordinate syntax (e.g. e2e4)
        try:
            move = chess.Move.from_uci(move_str.lower())
        except ValueError:
            return await ctx.send("❌ **[PARSE_ERR]** Syntax invalid. Use standard string formats like `e2e4` or `g1f3`.")

        if move not in board.legal_moves:
            return await ctx.send("❌ **[ILLEGAL_OPERATION]** That movement violation breaches core rules.")

        # Commit player move
        board.push(move)

        # Check for immediate end of game conditions
        if self.evaluate_game_over(ctx, code, board):
            return

        # Handle AI Turn if applicable
        if game["mode"] == "ai" and not board.is_game_over():
            await ctx.send("⚙️ *MSdos Kernel calculating optimal countermeasures...*")
            self.execute_ai_move(board, game["difficulty"])
            if self.evaluate_game_over(ctx, code, board):
                return

        # Re-render active environment
        await ctx.send(self.render_board(board) + f"\n**Match Instance ID:** `{code}`")

    def evaluate_game_over(self, ctx, code: str, board: chess.Board) -> bool:
        """Evaluates whether the board has reached a terminal operational state."""
        if board.is_game_over():
            result = "MATCH TERMINATED: "
            if board.is_checkmate():
                result += "💥 Checkmate validated."
            elif board.is_stalemate():
                result += "🤝 Stalemate encountered."
            elif board.is_insufficient_material():
                result += "📉 Draw via insufficient materials."
            else:
                result += "🏳️ Draw declared."
            
            self.bot.loop.create_task(ctx.send(f"🏁 **[SYSTEM_OVER]** {result}\n{self.render_board(board)}"))
            self.active_chess.pop(code, None)
            return True
        return False

async def setup(bot):
    await bot.add_cog(Games(bot))
