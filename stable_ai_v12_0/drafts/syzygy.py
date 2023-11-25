"""
just a concept
"""
import chess.syzygy
from typing import Dict, Table, Type

# Set the path to the directory containing the tablebases
tablebase_path = "/path/to/syzygy/tablebases"

# Create a Tablebase object
tablebase = chess.syzygy.Tablebase()

hashtable: Dict[str, Table] = ""
table: Type[Table] = ""
path: str = ""

tablebase._open_table(hashtable, table, path)

# Now you can probe positions
board = chess.Board("8/8/8/8/8/8/4k3/4K3 w - - 0 1")  # Example position
result = tablebase.probe_wdl(board)
