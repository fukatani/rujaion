from datetime import datetime
from pathlib import Path
import json

import appdirs

user_data_dir = Path(appdirs.user_data_dir("rujaion"))
record_log_path = user_data_dir / "record.log"


class Recorder:
    def __init__(self):
        self.log_file = Path(record_log_path)

    def push(self, problem, action, result="NA"):
        if self.log_file.exists():
            with self.log_file.open("r") as f:
                try:
                    json_data = json.load(f)
                except Exception:
                    json_data = []
        else:
            json_data = []
        json_data.append(
            {
                "timestamp": datetime.now().timestamp(),
                "problem": problem,
                "action": action,
                "result": result,
            }
        )

        with self.log_file.open("w") as f:
            json.dump(json_data, f, indent=4)
