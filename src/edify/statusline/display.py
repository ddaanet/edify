"""ANSI colored text formatter for statusline display."""

from typing import ClassVar

from edify.statusline.models import GitStatus, PlanUsageData, PythonEnv


class StatuslineFormatter:
    """Formats text with ANSI color codes for terminal display."""

    # ANSI color codes
    COLORS: ClassVar[dict[str, str]] = {
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
    }
    BRGREEN: ClassVar[str] = "\033[92m"  # Bright green
    BRRED: ClassVar[str] = "\033[91m"  # Bright red
    BOLD: ClassVar[str] = "\033[1m"  # Bold modifier
    RESET: ClassVar[str] = "\033[0m"
    BLINK: ClassVar[str] = "\033[5m"  # Blink modifier

    # Model tier to emoji mapping
    MODEL_EMOJI: ClassVar[dict[str, str]] = {
        "opus": "🥇",
        "sonnet": "🥈",
        "haiku": "🥉",
    }

    # Model tier to color mapping
    MODEL_COLORS: ClassVar[dict[str, str]] = {
        "opus": "magenta",
        "sonnet": "yellow",
        "haiku": "green",
    }

    # Model tier to abbreviated name mapping
    MODEL_NAMES: ClassVar[dict[str, str]] = {
        "opus": "Opus",
        "sonnet": "Sonnet",
        "haiku": "Haiku",
    }

    def _extract_model_tier(self, display_name: str) -> str | None:
        """Extract model tier from display name.

        Args:
            display_name: Model display name (e.g., "Claude Opus 4")

        Returns:
            Model tier ("opus", "sonnet", "haiku") or None if not found
        """
        lower_name = display_name.lower()
        if "opus" in lower_name:
            return "opus"
        if "sonnet" in lower_name:
            return "sonnet"
        if "haiku" in lower_name:
            return "haiku"
        return None

    def format_model(self, display_name: str, *, thinking_enabled: bool = True) -> str:
        """Format model with emoji and color coding.

        Args:
            display_name: Model display name (e.g., "Claude Opus 4")
            thinking_enabled: Whether thinking mode is enabled (used in cycle 1.3)

        Returns:
            Formatted string with medal emoji, color, and abbreviated name
        """
        tier = self._extract_model_tier(display_name)
        if tier is None:
            return display_name

        emoji = self.MODEL_EMOJI[tier]
        color = self.MODEL_COLORS[tier]
        name = self.MODEL_NAMES[tier]

        # Add thinking indicator if thinking is disabled
        thinking_indicator = "😶" if not thinking_enabled else ""

        # Opus gets bold+magenta (matches shell: ${BOLD}${MAGENTA})
        if tier == "opus":
            color_code = f"{self.BOLD}{self.COLORS[color]}"
            colored_name = f"{color_code}{name}{self.RESET}"
        else:
            colored_name = self.colored(name, color)
        return f"{emoji}{thinking_indicator} {colored_name}"

    def format_directory(self, path: str) -> str:
        """Format directory with emoji and CYAN color.

        Args:
            path: Directory path (basename will be extracted)

        Returns:
            Formatted string with directory emoji and colored basename
        """
        # Extract basename from path (matches shell: ${CURRENT_DIR##*/})
        basename = path.rstrip("/").rsplit("/", 1)[-1] if "/" in path else path
        colored_name = self.colored(basename, "cyan")
        return f"📁 {colored_name}"

    def format_git_status(self, status: GitStatus) -> str:
        """Format git status with emoji and colored branch name.

        Args:
            status: GitStatus model with branch name and dirty flag

        Returns:
            Formatted string with emoji and colored branch name
        """
        branch = status.branch or "unknown"
        if status.dirty:
            # Dirty state: yellow + bold
            emoji = "🟡"
            colored_branch = f"\033[33m\033[1m{branch}\033[0m"
        else:
            # Clean state: green
            emoji = "✅"
            colored_branch = self.colored(branch, "green")

        return f"{emoji} {colored_branch}"

    def format_cost(self, amount: float) -> str:
        """Format cost with emoji and dollar amount.

        Args:
            amount: Cost amount as float

        Returns:
            Formatted string with 💰 emoji prefix and dollar amount (2 decimals)
        """
        return f"💰 ${amount:.2f}"

    def format_python_env(self, env: PythonEnv) -> str:
        """Format Python environment with emoji.

        Args:
            env: PythonEnv model with environment name

        Returns:
            Formatted string with 🐍 emoji and env name, or empty if no env
        """
        if env.name is None:
            return ""
        return f"🐍 {env.name}"

    def colored(self, text: str, color: str) -> str:
        """Wrap text in ANSI color codes.

        Args:
            text: The text to colorize
            color: Color name (red, green, yellow, blue, magenta, cyan, white)

        Returns:
            Text wrapped with ANSI color codes
        """
        color_code = self.COLORS.get(color, "")
        return f"{color_code}{text}{self.RESET}"

    def token_bar(self, tokens: int, max_tokens: int) -> str:
        """Generate Unicode block progress bar for token usage.

        Args:
            tokens: Current token count
            max_tokens: Maximum token limit

        Returns:
            Progress bar using Unicode block characters
        """
        if max_tokens <= 0:
            return ""

        percentage = (tokens / max_tokens) * 100
        block_chars = "▁▂▃▄▅▆▇█"

        # Calculate which block character to use (0-8)
        block_index = int((percentage / 100) * len(block_chars))
        block_index = min(block_index, len(block_chars) - 1)

        return block_chars[block_index]

    def vertical_bar(self, percentage: int) -> str:
        """Generate vertical bar character for usage percentage display.

        Args:
            percentage: Usage percentage (0-100)

        Returns:
            Colored vertical bar character based on percentage
        """
        block_chars = "▁▂▃▄▅▆▇█"

        # Calculate which block character to use (0-8)
        block_index = int((percentage / 100) * len(block_chars))
        block_index = min(block_index, len(block_chars) - 1)
        block_index = max(block_index, 0)

        char = block_chars[block_index]

        # Color based on percentage
        if percentage < 50:
            color = "green"
        elif percentage < 80:
            color = "yellow"
        else:
            color = "red"

        return self.colored(char, color)

    def format_plan_limits(self, data: PlanUsageData) -> str:
        """Format plan usage limits for 5h and 7d on one line.

        Args:
            data: PlanUsageData with hour5_pct, hour5_reset, day7_pct

        Returns:
            Formatted string with "5h {pct}% {bar} {reset} / 7d {pct}% {bar}"
        """
        hour5_bar = self.vertical_bar(int(data.hour5_pct))
        day7_bar = self.vertical_bar(int(data.day7_pct))
        hour5_str = f"5h {int(data.hour5_pct)}% {hour5_bar} {data.hour5_reset}"
        day7_str = f"7d {int(data.day7_pct)}% {day7_bar}"
        return f"{hour5_str} / {day7_str}"

    def format_tokens(self, tokens: int) -> str:
        """Convert token count to human-readable string.

        Args:
            tokens: Token count to format

        Returns:
            Human-readable string (e.g., "1k", "1.5M", "100")
        """
        if tokens < 1000:
            return str(tokens)
        if tokens < 1000000:
            # Display as thousands
            k = tokens // 1000
            return f"{k}k"
        # Display as millions
        m = tokens / 1000000
        if m == int(m):
            return f"{int(m)}M"
        return f"{m:.1f}M"

    def format_mode(self, mode: str) -> str:
        """Format mode with emoji and color.

        Args:
            mode: Mode name ("plan" or "api")

        Returns:
            Formatted string with emoji and colored mode name
        """
        if mode == "plan":
            emoji = "🎫"
            mode_name = "Plan"
            color = "green"
        elif mode == "api":
            emoji = "💳"
            mode_name = "API"
            color = "yellow"
        else:
            # Fallback for unknown modes
            return mode

        colored_mode = self.colored(mode_name, color)
        return f"{emoji} {colored_mode}"

    def horizontal_token_bar(self, token_count: int) -> str:
        """Generate horizontal token bar with per-block color progression.

        Args:
            token_count: Number of tokens to display

        Returns:
            Bar string with format "[{color1}█{color2}█...{reset}]" where each block
            is individually colored based on its position threshold.
        """
        if token_count == 0:
            return ""

        # Each full block represents 25k tokens
        full_blocks = token_count // 25000
        remainder = token_count % 25000

        # 8-level Unicode block characters (matches shell case 0-7)
        unicode_levels = ["▏", "▎", "▍", "▌", "▋", "▊", "▉", "█"]

        # Color thresholds based on block position
        colors = [
            self.BRGREEN,  # Block 0: 0-25k
            self.COLORS["green"],  # Block 1: 25k-50k
            self.COLORS["blue"],  # Block 2: 50k-75k
            self.COLORS["yellow"],  # Block 3: 75k-100k
            self.COLORS["red"],  # Block 4: 100k-125k
            self.BRRED,  # Block 5+: >= 125k
        ]

        # Build bar with per-block coloring
        bar_parts = []

        # Add full blocks with appropriate colors
        for i in range(full_blocks):
            color_idx = min(i, len(colors) - 1)
            color = colors[color_idx]
            # Add blink modifier for critical (block 5+)
            if color_idx >= 5:
                color += self.BLINK
            bar_parts.append(f"{color}█")

        # Add partial block if remainder exists
        if remainder > 0:
            # Shell formula: (partial * 8 + 12500) / 25000
            partial_idx = (remainder * 8 + 12500) // 25000
            partial_idx = min(partial_idx, 7)  # Cap at 7
            # Partial block uses color of its position (same as next full block)
            color_idx = min(full_blocks, len(colors) - 1)
            color = colors[color_idx]
            if color_idx >= 5:
                color += self.BLINK
            bar_parts.append(f"{color}{unicode_levels[partial_idx]}")

        # Join all parts and add reset code (no brackets, matches shell)
        return "".join(bar_parts) + self.RESET

    def format_context(self, token_count: int) -> str:
        """Format context with threshold-colored token count and bar.

        Args:
            token_count: Number of tokens in context

        Returns:
            Formatted string with 🧠 emoji, threshold-colored count, and bar
        """
        # Format token count with kilos/millions logic (integer kilos, matches shell)
        if token_count < 1000:
            formatted_count = str(token_count)
        elif token_count < 1000000:
            # Kilos: integer only (shell uses printf "%3.0fk")
            k = token_count // 1000
            formatted_count = f"{k}k"
        else:
            # Millions: always 1 decimal
            m = token_count / 1000000
            formatted_count = f"{m:.1f}M"

        # Apply threshold-based coloring to token count
        if token_count < 25000:
            count_color = self.BRGREEN
        elif token_count < 50000:
            count_color = self.COLORS["green"]
        elif token_count < 75000:
            count_color = self.COLORS["blue"]
        elif token_count < 100000:
            count_color = self.COLORS["yellow"]
        elif token_count < 150000:
            count_color = self.COLORS["red"]
        else:
            count_color = self.BRRED + self.BLINK

        # Build colored count string
        colored_count = f"{count_color}{formatted_count}{self.RESET}"

        # Get bar visualization
        bar = self.horizontal_token_bar(token_count)

        # Compose final string: emoji, colored count, bar
        return f"🧠 {colored_count} {bar}"
