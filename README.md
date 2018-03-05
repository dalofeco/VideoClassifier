# Video Expert System

The Video Expert System (will) incorporate TensorFlow's machine learning capabilities to actively analyze video streams for actionable content. Precisely, our system will be trained to detect on-going robberies, assaults, and similar anomalies to provide quick video intelligence capabilities. 




## Setup Instructions

##### Pre-requisites

- Golang

- TensorFlow ("github.com/tensorflow/tensorflow/tensorflow/go")

- Gorilla's WebSocket ("github.com/gorilla/websocket")

  **Install all dependencies listed above by running `go get [url]` on your machine.**

  ​

#### Instructions for running Go Classifier Server for Trained Model

1. Clone the `go` branch from the repository to your local machine.
2. Copy the `tf_files` folder with your model to `/Models/tf_files-v{1.0}` replacing the brackets with your own version number.
3. Navigate into the `VideoExpertSystem` directory using the command line.
4. Run `go run *.go` to execute the server.

**Note:** The Go server listens for requests at `http://localhost:8080/classify` to test the classification.





## Video Datasets

- UCF Crime Dataset - http://crcv.ucf.edu/cchen/



## Helpful Links

- TensorFlow for Poets 2 Repo: https://github.com/googlecodelabs/tensorflow-for-poets-2