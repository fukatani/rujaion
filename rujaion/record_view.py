from collections import defaultdict
import datetime
import json
from pathlib import Path

import pandas
import plotly.express

from rujaion.recorder import record_log_path


def visualize():
    log_file = Path(record_log_path)
    with log_file.open("r") as f:
        json_data = json.load(f)

    tasks = defaultdict(list)
    for record in json_data:
        tasks[record["problem"]].append((record["timestamp"], record["action"]))

    dictonaries = []
    for problem, task in tasks.items():
        problem = problem.split("/")[-1]
        for timestamp, action in task:
            date = datetime.datetime.fromtimestamp(timestamp)
            dictonaries.append(
                dict(
                    Task=problem,
                    Problem=problem,
                    Start=date,
                    Finish=date + datetime.timedelta(seconds=20),
                    Action=action,
                )
            )
    df = pandas.DataFrame(dictonaries)
    fig = plotly.express.timeline(
        df, x_start="Start", x_end="Finish", y="Problem", color="Action"
    )
    fig.update_layout(font={"family": "Meiryo", "size": 20})
    fig.show()


if __name__ == "__main__":
    visualize("record.log")
