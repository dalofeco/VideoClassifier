package main

import (
	"fmt"
	"io"
	"io/ioutil"
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

// Define time interval in milliseconds to request new frame from client
const TICKER_INTERVAL int = 500

type ClassifierServer struct {
	channels []*Channel
}

// Create a new server instance
func NewClassifierServer() *ClassifierServer {

	// Declare classifier server
	classifierServer := ClassifierServer{}

	return &classifierServer
}

// –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––– \\
// –––––––––––––––––––––– SOCKET HELPERS –––––––––––––––––––––– \\
// –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––– \\

// Web socket upgrader for handler below
var upgrader = websocket.Upgrader{
	ReadBufferSize:  1024,
	WriteBufferSize: 1024,
	CheckOrigin:     func(r *http.Request) bool { return true },
}

// Binds socket to active classification server
func (cs *ClassifierServer) bindSocket(w http.ResponseWriter, req *http.Request) {

	// Upgrade the connection to websocket
	conn, err := upgrader.Upgrade(w, req, nil)
	if err != nil {
		log.Println("Couldn't upgrade to websocket")
		log.Println(err)
		return
	}

	// Create a new channel for handling connections and append to
	newChannel := NewChannel(conn)
	cs.channels = append(cs.channels, newChannel)

	log.Println("Started new client channel!")
}

func (cs *ClassifierServer) serve() {

	// Serving static files (js/css)
	jsFs := http.FileServer(http.Dir("js"))
	cssFs := http.FileServer(http.Dir("css"))

	// Handlers for static files
	http.Handle("/js/", http.StripPrefix("/js/", jsFs))
	http.Handle("/css/", http.StripPrefix("/css/", cssFs))

	// Handlers for html pages
	http.HandleFunc("/classify", cs.serveClassifyPage)

	// Socket handler
	http.HandleFunc("/ws/bind", cs.bindSocket)

	// Log server listening msg
	fmt.Println("Starting server listening on port 8081")

	// Server HTTP server on specified port, without a defined MUX
	http.ListenAndServe(":8081", nil)

}

// Sends file specified by path to requestor
func (cs *ClassifierServer) sendFile(path string, w http.ResponseWriter, req *http.Request) {

	// Read file checking for errors
	pageData, err := ioutil.ReadFile(path)
	if err != nil {
		log.Printf("Requested file does not exist: %s", path)
		io.WriteString(w, "404 Not Found")
	}

	// Send to requestor via http.ResponseWriter
	io.WriteString(w, string(pageData))

}

// Serves classify webpage
func (cs *ClassifierServer) serveClassifyPage(w http.ResponseWriter, req *http.Request) {

	// Define path and send it to client
	pageLocation := "html/classify.html"
	cs.sendFile(pageLocation, w, req)
}

///////////// |||| \\\\\\\\\\\\\\\
///////////// MAIN \\\\\\\\\\\\\\\
///////////// |||| \\\\\\\\\\\\\\\

// Main function
func main() {

	// Create an initialized and loaded classifier server
	var classifierServer *ClassifierServer = NewClassifierServer()
	classifierServer.serve()

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
