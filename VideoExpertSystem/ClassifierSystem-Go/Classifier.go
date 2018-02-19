package main

import (
	"bufio"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"time"

	tf "github.com/tensorflow/tensorflow/tensorflow/go"
	op "github.com/tensorflow/tensorflow/tensorflow/go/op"
)

type Classifier struct {
	session *tf.Session
	graph   *tf.Graph
	labels  []string
}

func NewClassifier() *Classifier {

	start := time.Now()

	var c Classifier

	// Load graph and labels
	c.graph = c.loadModel()
	c.labels = c.loadLabels()

	// Create a session for running classifications
	session, err := tf.NewSession(c.graph, nil)
	if err != nil {
		fmt.Println("Error creating new session")
		log.Fatal(err)
	}

	c.session = session

	log.Printf("Loaded Classifier in %.2f seconds!", time.Since(start).Seconds())

	return &c

}

func (c *Classifier) ClassifyImage(imageData []byte) (result string) {

	// Load graph and labels
	c.graph = c.loadModel()
	c.labels = c.loadLabels()

	// Generate the path for image
	// imagePath := "../../VideoCache/" + imageName

	// Load image as tensor
	imageTensor, err := c.imageDataToTensor(imageData)
	if err != nil {
		fmt.Println("Error loading image as tensor")
		log.Fatal(err)
	}

	// Create a session for running classifications
	c.session, err = tf.NewSession(c.graph, nil)
	if err != nil {
		fmt.Println("Error creating new session")
		log.Fatal(err)
	}

	// Run the graph with the image tensor
	output, err := c.session.Run(
		map[tf.Output]*tf.Tensor{
			c.graph.Operation("Mul").Output(0): imageTensor,
		},
		[]tf.Output{
			c.graph.Operation("final_result").Output(0),
		},
		nil)

	if err != nil {
		fmt.Println("Error running graph")
		log.Fatal(err)
	}

	probabilities := output[0].Value().([][]float32)[0]

	var highestProb float32 = 0
	highestIndex := 0

	// Loop through probablities, find highest
	for i, probability := range probabilities {
		if probability > highestProb {
			highestProb = probability
			highestIndex = i
		}
	}

	return fmt.Sprintf("%s: %.2f", c.labels[highestIndex], probabilities[highestIndex])

}

func (c *Classifier) loadModel() (graph *tf.Graph) {
	// Load pre-trained model
	// Define the graph directory
	var graphDir = "../../Models/tf_files-v0.3/retrained_graph.pb"

	// Read the graph (model) file
	model, err := ioutil.ReadFile(graphDir)
	if err != nil {
		fmt.Println("Error reading graph file")
		log.Fatal(err)
	}

	// Create new graph
	graph = tf.NewGraph()

	// Import model into graph checking for err
	err = graph.Import(model, "")
	if err != nil {
		fmt.Println("Error importing model into graph")
		log.Fatal(err)
	}

	return graph
}

func (c *Classifier) loadLabels() (labels []string) {

	var labelsDir = "../../Models/tf_files-v0.3/retrained_labels.txt"

	// Load labels
	labelsFile, err := os.Open(labelsDir)
	if err != nil {
		fmt.Println("Error reading labels file")
		log.Fatal(err)
	}

	// Close labels file once parent function is done
	defer labelsFile.Close()

	// Create new scanner
	scanner := bufio.NewScanner(labelsFile)

	for scanner.Scan() {
		labels = append(labels, scanner.Text())
	}

	if err := scanner.Err(); err != nil {
		fmt.Println("Scanner produced an error")
		log.Fatal(err)
	}

	return labels
}

func (c *Classifier) imageDataToTensor(imageData []byte) (*tf.Tensor, error) {

	// // Read image file
	// bytes, err := ioutil.ReadFile(imageFilename)
	// if err != nil {
	// 	return nil, err
	// }

	// DecodeJpeg uses a scalar String-valued tensor as input.
	tensor, err := tf.NewTensor(string(imageData))
	if err != nil {
		return nil, err
	}

	// Construct a graph to normalize the image
	graph, input, output, err := c.constructGraphToNormalizeImage()
	if err != nil {
		return nil, err
	}

	// Execute graph to normalize image
	session, err := tf.NewSession(graph, nil)
	if err != nil {
		return nil, err
	}

	defer session.Close()

	// Run the graph
	normalized, err := session.Run(
		map[tf.Output]*tf.Tensor{input: tensor},
		[]tf.Output{output},
		nil)

	if err != nil {
		return nil, err
	}

	// Return first normalized result
	return normalized[0], nil
}

// The inception model takes as input the image described by a Tensor in a very
// specific normalized format (a particular image size, shape of the input tensor,
// normalized pixel values etc.).
//
// This function constructs a graph of TensorFlow operations which takes as
// input a JPEG-encoded string and returns a tensor suitable as input to the
// inception model.
func (c *Classifier) constructGraphToNormalizeImage() (graph *tf.Graph, input, output tf.Output, err error) {
	// Some constants specific to the pre-trained model at:
	// https://storage.googleapis.com/download.tensorflow.org/models/inception5h.zip
	//
	// - The model was trained after with images scaled to 224x224 pixels.
	// - The colors, represented as R, G, B in 1-byte each were converted to
	//   float using (value - Mean)/Scale.
	const (
		H, W  = 299, 299
		Mean  = float32(128)
		Scale = float32(128)
	)
	// - input is a String-Tensor, where the string the JPEG-encoded image.
	// - The inception model takes a 4D tensor of shape
	//   [BatchSize, Height, Width, Colors=3], where each pixel is
	//   represented as a triplet of floats
	// - Apply normalization on each pixel and use ExpandDims to make
	//   this single image be a "batch" of size 1 for ResizeBilinear.
	s := op.NewScope()
	input = op.Placeholder(s, tf.String)
	output = op.Div(s,
		op.Sub(s,
			op.ResizeBilinear(s,
				op.ExpandDims(s,
					op.Cast(s,
						op.DecodeJpeg(s, input, op.DecodeJpegChannels(3)), tf.Float),
					op.Const(s.SubScope("make_batch"), int32(0))),
				op.Const(s.SubScope("size"), []int32{H, W})),
			op.Const(s.SubScope("mean"), Mean)),
		op.Const(s.SubScope("scale"), Scale))
	graph, err = s.Finalize()
	return graph, input, output, err
}
