from bluesky_widgets.models.auto_plot_builders import AutoLines
from bluesky_widgets.qt import Window
from bluesky_widgets.qt.figures import QtFigures

from .settings import SETTINGS


class ViewerModel:
    """
    This encapsulates on the models in the application.
    """

    def __init__(self):
        self.auto_plot_builder = AutoLines(max_runs=3)


class Viewer(ViewerModel):
    """
    This extends the model by attaching a Qt Window as its view.

    This object is meant to be exposed to the user in an interactive console.
    """

    def __init__(self, *, show=True, title="IOS Streaming"):
        # TODO Where does title thread through?
        super().__init__()
        for source in SETTINGS.subscribe_to:
            if source["protocol"] == "zmq":
                from bluesky_widgets.qt.zmq_dispatcher import RemoteDispatcher
                from bluesky_widgets.utils.streaming import (
                    stream_documents_into_runs,
                )

                zmq_addr = source["zmq_addr"]
                dispatcher = RemoteDispatcher(zmq_addr)
                dispatcher.subscribe(
                    stream_documents_into_runs(self.auto_plot_builder.add_run)
                )
                dispatcher.start()

            elif source["protocol"] == "kafka":
                from bluesky_kafka import RemoteDispatcher
                from bluesky_widgets.utils.streaming import stream_documents_into_runs
                from qtpy.QtCore import QThread

                bootstrap_servers = source["servers"]
                topics = source["topics"]

                consumer_config = {
                    "auto.commit.interval.ms": 100,
                    "auto.offset.reset": "latest",
                    "security.protocol": "SASL_SSL",
                    "sasl.mechanisms": "PLAIN",
                    "sasl.username": "beamline",
                    "sasl.password": "irRM9KiJgvQe7s",
                }

                self.dispatcher = RemoteDispatcher(
                    topics=topics,
                    bootstrap_servers=bootstrap_servers,
                    group_id="ios_widgets",
                    consumer_config=consumer_config,
                )

                self.dispatcher.subscribe(
                    stream_documents_into_runs(self.auto_plot_builder.add_run)
                )

                class DispatcherStart(QThread):
                    def __init__(self, dispatcher):
                        super().__init__()
                        self._dispatcher = dispatcher

                    def run(self):
                        self._dispatcher.start()

                self.dispatcher_thread = DispatcherStart(self.dispatcher)
                self.dispatcher_thread.start()

            else:
                print(f"Unknown protocol: {source['protocol']}")

        widget = QtFigures(self.auto_plot_builder.figures)
        self._window = Window(widget, show=show)

    @property
    def window(self):
        return self._window

    def show(self):
        """Resize, show, and raise the window."""
        self._window.show()

    def close(self):
        """Close the window."""
        self._window.close()
