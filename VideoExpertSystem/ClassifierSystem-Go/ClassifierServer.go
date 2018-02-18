package main

import (
	"log"
	"math/rand"
	"net/http"
	"time"

	"github.com/gorilla/websocket"
	// "golang.org/x/net/websocket"
)

func init() {
	rand.Seed(time.Now().UnixNano())
}

// Define time interval in seconds to request new frame from client
const TICKER_INTERVAL float32 = 0.5

type ClassifierServer struct {
	classifier              *Classifier
	clientSocketConnections map[string]*websocket.Conn
	activeClientIndex       string
	clientQueue             []string
}

// Create a new server instance
func NewClassifierServer() *ClassifierServer {

	// Declare classifier server
	classifierServer := ClassifierServer{}

	// Create new classifier with loaded model
	classifierServer.classifier = NewClassifier()

	// Create client socket connections
	classifierServer.clientSocketConnections = make(map[string]*websocket.Conn)

	// Start handling regsitered clients
	go classifierServer.handleRegisteredClients()

	return &classifierServer
}

func (cs *ClassifierServer) generateClientID() string {

	var idLength = 20
	var characters = []rune("1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
	b := make([]rune, idLength)
	for i := range b {
		b[i] = characters[rand.Intn(len(characters))]
	}

	return string(b)

}

// Web socket upgrader for handler below
var upgrader = websocket.Upgrader{
	ReadBufferSize:  1024,
	WriteBufferSize: 1024,
	CheckOrigin:     func(r *http.Request) bool { return true },
}

func (cs *ClassifierServer) unbindSocket(clientID string) {

	// Make sure client id has a registered socket
	if val, ok := cs.clientSocketConnections[clientID]; ok {

		err := val.Close()
		if err != nil {
			log.Print("Error closing connection when unbinding socket for client: ", clientID)
			log.Print(err)
		}

		// Delete the entry in socket connections map
		delete(cs.clientSocketConnections, clientID)

	}

	clientIndex := -1

	// Find index of ClientID from queue if present
	for i, val := range cs.clientQueue {
		if val == clientID {
			clientIndex = i
			break
		}
	}

	// Client ID was found
	if clientIndex != -1 {
		// Eliminate it with splice
		cs.clientQueue = append(cs.clientQueue[:clientIndex], cs.clientQueue[clientIndex+1:]...)

		// Client ID not found
	} else {
		log.Print("ClientQueue had no record of Client ID: ", clientID)
	}

}

// Binds socket to active classification server
func (cs *ClassifierServer) bindSocket(w http.ResponseWriter, req *http.Request) {

	conn, err := upgrader.Upgrade(w, req, nil)
	if err != nil {
		log.Println("Couldn't upgrade to websocket")
		log.Println(err)
		return
	}

	// Generate new client ID
	newClientID := cs.generateClientID()

	// Check if there is at least one collection
	if len(cs.clientSocketConnections) > 0 {
		if _, ok := cs.clientSocketConnections[newClientID]; ok {
			// If ok, client ID already exists
			log.Fatal("Whoah. Key repeated.")
			return

		} else {
			// Save websocket conn object with client id and append to client queue
			cs.clientSocketConnections[newClientID] = conn
			cs.clientQueue = append(cs.clientQueue, newClientID)
			// Let the timed queue handler handle the queue
		}
	} else {

		// Save websocket conn object with client id and append to client queue
		cs.clientSocketConnections[newClientID] = conn
		cs.clientQueue = append(cs.clientQueue, newClientID)
		// Let the timed queue handler handle the queue
	}
}

// Handles socket requests for classifying a specified image
func (cs *ClassifierServer) handleRegisteredClients() {

	// Create a ticker channel every X seconds
	ch := time.Tick(time.Duration(TICKER_INTERVAL) * time.Second)

	for range ch {
		if len(cs.clientQueue) == 0 {
			log.Print("No active users...")
			continue
		}

		// Performance metrics
		startTime := time.Now()

		// Get next client ID to serve
		nextClientID := cs.clientQueue[0]

		// Remove top element of queue and add to end
		cs.clientQueue = cs.clientQueue[1:]
		cs.clientQueue = append(cs.clientQueue, nextClientID)

		// If client id is in client socket connections pool
		if val, ok := cs.clientSocketConnections[nextClientID]; ok {

			// Get connection
			conn := val

			// Send FRAME message to client, requesting a FRAME
			conn.WriteMessage(websocket.TextMessage, []byte("FRAME"))
			log.Print("Sent FRAME request text message")

			msgType, data, err := conn.ReadMessage()
			if err != nil {
				log.Print("Couldn't read FRAME message reply from client: ", nextClientID)
				go cs.unbindSocket(nextClientID)
				continue
			}

			// If binary message, image bytes are being sent
			if msgType == websocket.BinaryMessage {

				// Make sure data is not nil
				if data != nil {
					log.Print("Recieved Image from ", nextClientID)

					// Get result string from image classifier
					resultString := cs.classifier.ClassifyImage(data)

					// Send results over websocket to client
					conn.WriteMessage(websocket.TextMessage, []byte(resultString))

				} else {
					log.Print("Recieved empty socket binary message")
					continue
				}

			} else if msgType == websocket.TextMessage {
				log.Print("Recieved Text Message:")
				log.Print(data)
			}

			duration := time.Since(startTime)
			log.Println("Handled socket request in {} seconds", duration)

		}

	}
}

// type FrameData struct {
// 	name      string
// 	data      string
// 	timestamp int64
// }

// type Message struct {
// 	msg       string
// 	timestamp string
// 	result    string
// }
