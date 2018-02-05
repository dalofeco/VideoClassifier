# Video Expert System

The Video Expert System incorporates TensorFlow's machine learning capabilities to actively analyze video streams for actionable content. Precisely, our system will be trained to detect on-going robberies, assaults, and similar anomalies to provide quick video intelligence capabilities. 




## Setup Instructions

##### Pre-requisites

- Node.js
- Python 3
- TensorFlow Python Libraries

##### Instructions for Running Classifier Server for Trained Model

1. Clone the repository to your local machine.
2. Copy the `tf_files` folder with your model to `VideoExpertSystem/tf_files`.
3. Navigate into the `WebInterface` directory using the command line.
4. Run `npm install` to install all project dependencies.
5. Run `node server.js` to initiate the server.****

**Note:** The server listens for requests at `http://localhost:8080/classify` to test the classification.



##### Instructions for Training New Image Recognition Model 
1. Clone the repository to your local machine.
2. Copy the training images onto the `VideoExpertSystem/tf_files/dataset` directory. Make sure all image files are divided into different folders, each named with the associated category/label.
3. Navigate into the `VideoExpertSystem` folder with the command line.
4. Run the following command to initiate the training process: 
  `python3 -m scripts.retrain --bottleneck_dir=tf_files/bottlenecks --how_many_training_steps=100 --model_dir=tf_files/models/ --sumarries_dir=tf_files/training_summaries/inception_v3 --output_graph=tf_files/retrained_graph.pb --output_labels=tf_files/retrained_labels.txt --architecture=inception_v3 --image_dir=tf_files/dataset`. 

**Note:** Depending on your setup, you can replace `python3` with your command to execute Python 3. Also, the training steps parameter can be modified as desired.

**Disclaimer:** The `VideoExpertSystem/scripts` folder is sourced from the official TensorFlow repo. It contains helper scripts for training and classifying, and is provided within for convenience, to avoid having to clone the entire repository. 



## Components

#### Model

Models are saved under the Model folder.

#### WebInterface

Node.js back-end providing web-based interface for communicating with the VideoExpertSystem.

#### VideoExpertSystem

Python scripts for classifying images into their distinctive categories and training new models.

#### DatasetToolkit

Python based tools to manage video, image frames, and classify into respective categories for effective generation of organized training and validation data sets. 




## Video Datasets

- UCF Crime Dataset - http://crcv.ucf.edu/cchen/