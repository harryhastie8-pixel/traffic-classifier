



# TCP Anomaly Detection Server

This project contains an asynchronous TCP server for detecting anomalous network traffic using a pre-trained Isolation Forest model.

Data is batched and converted to json format. At certian intervials these batches are parsed to the server to detect 
any nefarious network activity. 

The server runs the data through the machine learning pipeline, and returns whether any instances record was identified as anomalous.

This reposotry also contains the .... used to train the model ,thuis notebook ... 

## How it works

The server waits for a client to connect and then reads JSON records. These records are converted into a pandas DataFrame and reduced to the features expected by the model. Thses featues where found to be the mose predictive 

The saved pipeline then handles the preprocessing and anomaly detection. Isolation Forest returns `1` for normal traffic and `-1` for anomalous traffic. The server converts this into a simple JSON response.

In general, the data flows through the server as:

```text
Client
  |
  | JSON record
  v
TCP Server
  |
  | Feature selection
  v
ML Pipeline
  |
  | Isolation Forest
  v
Anomaly result
  |
  v
Client
```

## Requirements

The server requires Python 3.8+ and the following packages:

```bash
pip install joblib numpy pandas scikit-learn
```

`asyncio` is included with Python.

## Model files

Two files are required in the same directory as the server:

```text
inferencePipeline.pkl
predictive_features.pkl
```

`inferencePipeline.pkl` contains the trained preprocessing and Isolation Forest pipeline.

`predictive_features.pkl` contains the list of features that the model expects. Keeping this list separate means the server can ensure incoming records contain the same features that were used when training the model.

The feature list might contain:

```python
[
    "service",
    "flag",
    "dst_bytes",
    "logged_in",
    "count",
    "srv_count",
    "dst_host_count",
    "dst_host_srv_diff_host_rate"
]
```

## Running the server

The server takes the IP address and port as command-line arguments:

```bash
python server.py <ip> <port>
```

For example:

```bash
python server.py 127.0.0.1 5000
```

You should then see:

```text
TCP server listening on 127.0.0.1:5000
```

To listen on all network interfaces:

```bash
python server.py 0.0.0.0 5000
```

## Sending data

Records are sent as JSON, with each record terminated by a newline.

For example:

```json
{"service":22,"flag":9,"dst_bytes":5450,"logged_in":1,"count":9,"srv_count":9,"dst_host_count":9,"dst_host_srv_diff_host_rate":0.0}
```

Multiple records can be sent over the same connection.

## Responses

When the model identifies an anomaly, the server returns:

```json
{"anomaly":true}
```

If something goes wrong while processing a record, an error is returned instead:

```json
{"error":"error description"}
```

The server handles errors for individual records without stopping the entire server.

## Training the model

The model is trained separately from the server. Once training is complete, the fitted pipeline and feature list can be saved using `joblib`:

```python
joblib.dump(pipeline, "inferencePipeline.pkl")
joblib.dump(predictive_features, "predictive_features.pkl")
```

The server only loads these files; it does not retrain the model when it starts.

## Project structure

A typical directory looks like this:

```text
.
├── server.py
├── inferencePipeline.pkl
├── predictive_features.pkl
└── README.md
```

## Notes

The input data needs to use the same feature names and representation expected by the saved pipeline. In particular, any encoding or scaling used during training should already be part of `inferencePipeline.pkl`.

The server uses newline-delimited JSON so that several records can be processed over a single TCP connection without requiring a new connection for every prediction.