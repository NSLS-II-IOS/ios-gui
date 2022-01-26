import argparse

from bluesky_widgets.qt import gui_qt

from .viewer import Viewer
from .settings import SETTINGS


def main(argv=None):
    parser = argparse.ArgumentParser(description="ios-gui")
    parser.add_argument("--zmq", help="0MQ address")
    parser.add_argument(
        "--kafka-servers",
        help="Kafka servers, comma-separated string, e.g. "
        "kafka1.nsls2.bnl.gov:9092,kafka2.nsls2.bnl.gov:9092,kafka3.nsls2.bnl.gov:9092",
    )
    parser.add_argument(
        "--kafka-topics",
        help="Kafka servers, comma-separated string, e.g. ios.bluesky.runengine.documents",
    )
    args = parser.parse_args(argv)

    with gui_qt("IOS Streaming"):
        if args.zmq:
            SETTINGS.subscribe_to.append({"protocol": "zmq", "zmq_addr": args.zmq})
        if args.kafka_servers and args.kafka_topics:
            kafka_servers = args.kafka_servers
            kafka_topics = args.kafka_topics.split(",")
            kafka_topics = [_.strip() for _ in kafka_topics]
            source = {
                "protocol": "kafka",
                "servers": kafka_servers,
                "topics": kafka_topics,
            }
            SETTINGS.subscribe_to.append(source)

        viewer = Viewer()  # noqa: 401


if __name__ == "__main__":
    main()
