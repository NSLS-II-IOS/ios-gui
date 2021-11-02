"""
In a terminal, start a message bus that will forward us Bluesky documents.

bluesky-0MQ-proxy -v 5577 5578

Start the example

python -m ios_gui.qt_streaming localhost:5578
"""  # noqa E501

from bluesky_widgets.utils.streaming import stream_documents_into_runs
from bluesky_widgets.qt.zmq_dispatcher import RemoteDispatcher
from bluesky_widgets.models.auto_plot_builders import AutoLines
from bluesky_widgets.qt.figures import QtFigures
from bluesky_widgets.qt import gui_qt
import sys


def main():
    with gui_qt("IOS Streaming"):
        message_bus_address = sys.argv[-1]
        dispatcher = RemoteDispatcher(message_bus_address)

        model = AutoLines(max_runs=3)
        dispatcher.subscribe(stream_documents_into_runs(model.add_run))
        view = QtFigures(model.figures)
        view.show()
        dispatcher.start()


if __name__ == "__main__":
    main()
