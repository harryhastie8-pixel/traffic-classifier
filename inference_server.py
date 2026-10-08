import asyncio
import argparse
import json
import joblib
import numpy as np
import pandas as pd


# Load model and features
prediction_pipeline = joblib.load("inferencePipeline.pkl")
predictive_features = joblib.load("predictive_features.pkl")


async def handle_client(reader, writer):

    address = writer.get_extra_info("peername")
    print(f"Connection from {address}")

    try:
        while True:
            data = await reader.readline()
            if not data:
                break

            try:
                # Decode JSON
                records = json.loads(
                    data.decode("utf-8")
                )

                # The JSON is expected to have the format:
                #
                # {
                #     "time_1": {data},
                #     "time_2": {data},
                #     ...
                # }
                #
                # We only need the data, so ignore the keys.
                X = pd.DataFrame(
                    records.values()
                )

                # Ensure expected features are present
                X = X[predictive_features]

                # Run the entire batch through the model pipeline
                predictions = prediction_pipeline.predict(X)

                # Isolation Forest:
                #  1  = normal
                # -1  = anomaly
                anomalies = predictions == -1

                result = {
                    "anomaly": bool(np.any(anomalies)),
                }

                # Send response
                response = json.dumps(result) + "\n"

                writer.write(
                    response.encode("utf-8")
                )

                await writer.drain()

            except Exception as e:

                print(
                    f"Error processing data "
                    f"from {address}: {e}"
                )

                response = json.dumps({
                    "error": str(e)
                }) + "\n"

                writer.write(
                    response.encode("utf-8")
                )

                await writer.drain()

    except ConnectionError:

        print(f"Connection lost: {address}")

    finally:

        writer.close()
        await writer.wait_closed()

        print(f"Connection closed: {address}")


async def main(host, port):

    server = await asyncio.start_server(
        handle_client,
        host,
        port
    )

    print(
        f"TCP server listening on "
        f"{host}:{port}"
    )

    async with server:

        await server.serve_forever()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Async TCP anomaly detection server"
    )

    parser.add_argument(
        "ip",
        help="IP address to bind the server to"
    )

    parser.add_argument(
        "port",
        type=int,
        help="Port to listen on"
    )

    args = parser.parse_args()

    asyncio.run(
        main(
            args.ip,
            args.port
        )
    )
