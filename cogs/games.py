import discord
from discord.ext import commands
import chess
import random
import urllib.parse

class Games(commands.Cog):
    ignore_global_check = True

    def __init__(self, bot):
        self.bot = bot
        # Maps a user's ID directly to their active game data
        self.active_users = {}

    def render_board_embed(self, game) -> discord.Embed:
        """Renders the chess board into a high-quality graphic embed."""
        board = game["board"]
        
        # URL encode the FEN string to generate a dynamic image
        fen = urllib.parse.quote(board.fen())
        image_url = f"https://www.chess.com/dynboard?fen={fen}&board=green&piece=neo&size=3"
        
        # Determine player names
        p_w = self.bot.get_user(game["player_w"])
        name_w = p_w.name if p_w else "White"
        
        if game["player_b"] == "AI":
            name_b = f"MSdos AI ({game['difficulty'].upper()})"
        else:
            p_b = self.bot.get_user(game["player_b"]) if game["player_b"] else None
            name_b = p_b.name if p_b else "Waiting for Opponent..."

        turn = "⚪ White's Turn" if board.turn == chess.WHITE else "⚫ Black's Turn"
        
        embed = discord.Embed(title="♟️ Tactical Chess Matrix", color=0x2B2D31)
        embed.add_field(name="White", value=f"🛡️ {name_w}", inline=True)
        embed.add_field(name="Black", value=f"🗡️ {name_b}", inline=True)
        embed.add_field(name="Status", value=f"**{turn}**", inline=False)
        
        if board.is_check():
            embed.add_field(name="⚠️ WARNING", value="**KING IS IN CHECK!**", inline=False)
            embed.color = 0xE74C3C # Turn embed red on check
            
        embed.set_image(url=image_url)
        embed.set_footer(text="Type: chessmove e2e4 | *exitchess to surrender")
        return embed

    def end_game(self, game):
        """Cleans up the memory cache to allow players to start new games."""
        if game["player_w"] in self.active_users:
            del self.active_users[game["player_w"]]
        if game["player_b"] != "AI" and game["player_b"] in self.active_users:
            del self.active_users[game["player_b"]]

    def execute_ai_move(self, board: chess.Board, difficulty: str):
        legal_moves = list(board.legal_moves)
        if not legal_moves: return

        if difficulty == "easy" or len(legal_moves) == 1:
            chosen_move = random.choice(legal_moves)
        else:
            scored_moves = []
            for move in legal_moves:
                score = 0
                if board.is_capture(move): score += 3
                board.push(move)
                if board.is_check(): score += 2
                board.pop()
                scored_moves.append((score, move))
            scored_moves.sort(key=lambda x: x[0], reverse=True)
            chosen_move = scored_moves[0][1]

        board.push(chosen_move)

    # --- SESSION MANAGEMENT ---

    @commands.command(name="play_chess")
    async def play_chess(self, ctx, mode: str, difficulty: str = "easy"):
        mode = mode.lower()
        if ctx.author.id in self.active_users:
            return await ctx.send("❌ **[SYS_ERR]** You are already in an active chess session. Finish it or use `*exitchess`.")
        
        if mode not in ["ai", "player"]:
            return await ctx.send("❌ **[SYS_ERR]** Invalid mode. Use `ai` or `player`.")

        game = {
            "board": chess.Board(),
            "player_w": ctx.author.id,
            "mode": mode,
            "exit_requested_by": None
        }

        if mode == "ai":
            game["player_b"] = "AI"
            game["difficulty"] = difficulty.lower()
            self.active_users[ctx.author.id] = game
            
            await ctx.send(f"🤖 **[KERNEL]** AI Engine initialized.", embed=self.render_board_embed(game))
        
        elif mode == "player":
            game["player_b"] = None
            self.active_users[ctx.author.id] = game
            
            await ctx.send(f"🎲 **[MULTI_LOBBY]** {ctx.author.mention} opened a chess lobby!\nTo join, an opponent must type: `*accept_chess {ctx.author.mention}`")

    @commands.command(name="accept_chess")
    async def accept_chess(self, ctx, host: discord.Member):
        if ctx.author.id in self.active_users:
            return await ctx.send("❌ **[SYS_ERR]** You are already in a match.")
            
        if host.id not in self.active_users:
            return await ctx.send("❌ **[SYS_ERR]** That user is not hosting a match.")
            
        game = self.active_users[host.id]
        
        if game["mode"] != "player":
            return await ctx.send("❌ **[SYS_ERR]** That user is playing against the AI.")
        if game["player_b"] is not None:
            return await ctx.send("❌ **[SYS_ERR]** That match is already full.")
        if host.id == ctx.author.id:
            return await ctx.send("❌ **[SYS_ERR]** You cannot play against yourself.")

        # Lock player 2 into the session
        game["player_b"] = ctx.author.id
        self.active_users[ctx.author.id] = game
        
        await ctx.send(f"⚔️ **[LINK_ESTABLISHED]** {ctx.author.mention} joined as Black!", embed=self.render_board_embed(game))

    # --- THE EXIT SYSTEM ---

    @commands.command(name="exitchess")
    async def exitchess(self, ctx):
        if ctx.author.id not in self.active_users:
            return await ctx.send("❌ **[SYS_ERR]** You are not in an active chess session.")
            
        game = self.active_users[ctx.author.id]
        
        if game["mode"] == "ai":
            self.end_game(game)
            return await ctx.send("🏳️ **[SURRENDER]** You disbanded the match against the AI.")
            
        # Multiplayer request handling
        opponent_id = game["player_b"] if game["player_w"] == ctx.author.id else game["player_w"]
        
        if opponent_id is None: # Lobby was open but nobody joined yet
            self.end_game(game)
            return await ctx.send("🛑 **[LOBBY_CLOSED]** Open matchmaking lobby cancelled.")

        game["exit_requested_by"] = ctx.author.id
        await ctx.send(f"⚠️ <@{opponent_id}>, your opponent wishes to disband the match. Type `*allow` to end it, or `*stop` to deny the request and continue playing.")

    @commands.command(name="allow")
    async def allow(self, ctx):
        if ctx.author.id not in self.active_users: return
        game = self.active_users[ctx.author.id]
        
        req_by = game.get("exit_requested_by")
        if req_by and req_by != ctx.author.id:
            self.end_game(game)
            await ctx.send("🤝 **[MATCH_DISBANDED]** Both players agreed to terminate the session.")

    @commands.command(name="stop")
    async def stop(self, ctx):
        if ctx.author.id not in self.active_users: return
        game = self.active_users[ctx.author.id]
        
        req_by = game.get("exit_requested_by")
        if req_by and req_by != ctx.author.id:
            game["exit_requested_by"] = None
            await ctx.send("🛑 **[REQUEST_DENIED]** The disband request was denied. The match continues!")

    # --- INVISIBLE MOVE LISTENER ---

    @commands.Cog.listener()
    async def on_message(self, message):
        # Prevent bot loops and check if it's our exact custom command structure
        if message.author.bot: return
        content = message.content.lower().strip()
        
        if not content.startswith("chessmove "):
            return
            
        user_id = message.author.id
        if user_id not in self.active_users:
            return await message.channel.send("❌ **[SYS_ERR]** You are not in an active chess match.")
            
        game = self.active_users[user_id]
        board = game["board"]
        
        if game["player_b"] is None:
            return await message.channel.send("⏳ **[WAITING]** No opponent has joined your lobby yet.")

        # Authority check
        current_turn_player = game["player_w"] if board.turn == chess.WHITE else game["player_b"]
        if user_id != current_turn_player:
            return await message.channel.send("🛑 **[ACCESS_DENIED]** It is currently your opponent's turn.")

        # Extract the move (e.g. "e2e4" from "chessmove e2e4")
        move_str = content.split(" ")[1]
        
        try:
            move = chess.Move.from_uci(move_str)
        except ValueError:
            return await message.channel.send("❌ **[PARSE_ERR]** Invalid format. Use coordinate string (e.g., `chessmove e2e4`).")

        if move not in board.legal_moves:
            return await message.channel.send("❌ **[ILLEGAL_MOVE]** That piece cannot make that movement.")

        # Execute player move
        board.push(move)
        
        # Check game state
        if await self.check_game_over(message.channel, game): return

        # AI Response
        if game["mode"] == "ai":
            self.execute_ai_move(board, game["difficulty"])
            if await self.check_game_over(message.channel, game): return

        # Re-render the board for the next turn
        await message.channel.send(embed=self.render_board_embed(game))

    async def check_game_over(self, channel, game) -> bool:
        board = game["board"]
        if board.is_game_over():
            result = "MATCH TERMINATED: "
            if board.is_checkmate(): result += "💥 **Checkmate!**"
            elif board.is_stalemate(): result += "🤝 **Stalemate.**"
            else: result += "🏳️ **Draw declared.**"
            
            # Send final board and clean up memory
            await channel.send(f"🏁 **[SYSTEM_OVER]** {result}", embed=self.render_board_embed(game))
            self.end_game(game)
            return True
        return False

async def setup(bot):
    await bot.add_cog(Games(bot))
