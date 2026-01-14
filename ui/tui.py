from rich.console import Console
from rich.theme import Theme

AGENT_THEME = Theme({
    "info" : "cyan",
    "error" : "bright_red bold",
    "success" : "green",
    "warning" : "yellow",
    "dim" : "dim",
    "muted" : "grey50",
    "border" : "grey35",
    "highlight" : "bold cyan",
    # Roles
    "user" : "bright_blue bold",
    "assistant" : "bright_white",

    #tools
    "tool":"bright_magenta bold",
    "tool.read":"cyan",
    "tool.write":"yellow",
    "tool.shell":"magenta",
    "tool.network":"bright_blue",
    "tool.memory": "green",
    "tool.mcp": "bright_cyan",

    #code_blocks
    "code_block":"bright_white",


})

_console = Console | None = None

def get_console()->Console:
    global _console
    if _console is None:
        _console = Console(theme=AGENT_THEME,highlight=True)
    return _console

class TUI:
    def __init__(
        self,
        console:Console | None = None
     ) -> None:

        self.console = console or get_console()

    def stream_assistant_delta(self,content:str):

        self.console.print(content,end="",markup=False)