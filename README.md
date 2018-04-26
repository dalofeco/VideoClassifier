# Video Expert System

The Video Expert System (will) incorporate TensorFlow's machine learning capabilities to actively analyze video streams for actionable content. Precisely, our system will be trained to detect on-going robberies, assaults, and similar anomalies to provide quick video intelligence capabilities. 




## Setup Instructions

##### Pre-requisites

- Python 3
- TensorFlow 
- OpenCV 


#### Instructions for Running Tornado Classifier Server for Trained Model

1. Clone the repository to your local machine.
2. Copy the `tf_files` folder with your model to `/Models/tf_files-v{1.0}` replacing the brackets with your own version number.
3. Navigate into the `VideoExpertSystem` directory using the command line.
4. Run `python3 ClassifierServer.py [model_version]`, replacing the brackets with your model version number to execute the server. 
5. Navigate to `http://localhost:8081/classify` to get the test the web application for classification.



#### Instructions for Training New CNN Image Recognition Model 
1. Clone the repository to your local machine.
2. Copy the training images onto the `Models/tf_files-v{1.0}/cnn/dataset` directory. Make sure all image files are divided into different folders, each folder named with the associated category/label.
3. Navigate into the `VideoExpertSystem` folder with the command line.
4. Execute the `Trainer.py` script with `cnn` option followed by your version number. Ex: `python Trainer.py cnn 1.0`
5. The script will start the retraining process and save your model under `tf_files-v{1.0}/retrained_graph.pb`.

**Disclaimer:** The `VideoExpertSystem/tf_scripts` folder is sourced from the official TensorFlow repo. It contains helper scripts for training and classifying, and is provided within for convenience, to avoid having to clone the entire repository. 

#### Instructions for Training RNN LSTM Models

1. Clone the repository to your local machine.
2. Copy the training video frames onto the `VideoExpertSystem/Models/tf_files-v{1.0}/rnn/dataset` directory.
3. Run the `Trainer.py` script using the `rnn` option followed by your model version number. Ex: `python Trainer.py rnn 1.0`
4. The script will start pre-processing the data, and then initiate the training process, saving your model under `tf_files-v{1.0}/rnn-model/lstm-model`.

**Note**: The training process may take extremely long time periods depending on the size of your dataset. It is recommended to run on powerful machines, preferrably using NVIDIA GPUs with an optimized version of TensorFlow.



#### Instructions for Dataset Construction using VideoClassifier

1. Organize all videos into different folders, each with a unique category name to be recognized.
2. Copy all videos to be classified onto `Models/tf_files-v1.0/videos` using the version number desired.
3. Navigate into `DatasetToolkit/` using the command line and execute `python3 VideoClassifier.py (category) (model_version) (mode) [interval]`, replacing `(category) `with the unique category name of videos to classify, `model_version` with the model value on your `tf_files-v1.0` folder, and `mode` with `cnn` or `rnn`, depending on the purpose of the dataset.

Usage: `python3 VideoClassifier.py (category) (model_version) [mode][state] [interval]`

##### Keyboard Controls

​	**P**- Pause

​	**Space** - Toggle Adding Frames to Dataset

​	**+**  Increase Playback Speed

​	**-**  Decrease Playback Speed

​	**S** - Save

​	**Q **- Quit





#### Instructions for Dataset Construction using VideoFragmenter

1. Organize all videos into different folders, each with a unique category name to be recognized.

2. Copy all videos to be classified onto `Models/tf_files-v1.0/videos` using the version number desired.

3. Navigate onto `DatasetToolkit` using a command line and execute `python3 VideoFragmenter.py (category) (mode)`, replacing category with the desired category to fragment into frames, and `cnn` or `rnn` for mode, depending on the usage for the dataset.

   ​
   The toolkit will go through every frame for the defined category (category must be present as a folder in `Models/tf_files-v1.0/videos` folder) and extract each frame into a `.jpg` file to the `Models/tf_files-v1.0/dataset/(MODE)/` folder, mode being either `cnn` or `rnn`.

   ​

## Components

#### Model

Models are saved as `tf_files-v1.0` folders under the Model parent folder.

#### VideoExpertSystem

Python-based TensorFlow programs with socket and HTTP servers for classifying images and videos into their distinctive categories and training new CNN and RNN models.

#### DatasetToolkit

Python based tools to manage video, image frames, and classify into respective categories for effective generation of structured training and validation data sets. 



## Libraries Used

#### Python Dependencies

To install the dependencies, use the **requirements.txt** file supplied. Running `pip install -r requirements.txt` will install all necessary dependencies for the system.

- TensorFlow
- TFLearn
- Scikit-learn
- OpenCV
- Numpy
- Scipy
- tqdm - Progress bar support



## Video Datasets

- UCF Crime Dataset - http://crcv.ucf.edu/cchen/



## Helpful Links

- TensorFlow for Poets 2 Repo: https://github.com/googlecodelabs/tensorflow-for-poets-2