package main

import (
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
	classifier *Classifier
}

// Create a new server instance
func NewClassifierServer() *ClassifierServer {

	// Declare classifier server
	classifierServer := ClassifierServer{}

	// Create new classifier with loaded model
	classifierServer.classifier = NewClassifier()

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

	conn, err := upgrader.Upgrade(w, req, nil)
	if err != nil {
		log.Println("Couldn't upgrade to websocket")
		log.Println(err)
		return
	}

	_ = NewChannel(conn)
	log.Println("Started new client channel!")
}

////////// MAIN
//
//
//
//
// MAIN STUFFS BELOW WARNING

func serveIndexPage(w http.ResponseWriter, req *http.Request) {

	pageLocation := "html/index.html"
	pageData, err := ioutil.ReadFile(pageLocation)
	if err != nil {
		log.Fatal(err)
	}

	io.WriteString(w, string(pageData))
}

// Main function
func main() {

	// Create an initialized and loaded classifier server
	var classifierServer *ClassifierServer = NewClassifierServer()

	// Serving static files (js/css)
	jsFs := http.FileServer(http.Dir("js"))
	cssFs := http.FileServer(http.Dir("css"))

	// Handlers for static files
	http.Handle("/js/", http.StripPrefix("/js/", jsFs))
	http.Handle("/css/", http.StripPrefix("/css/", cssFs))

	// Handlers for html pages
	http.HandleFunc("/", serveIndexPage)

	// Socket handlers
	http.HandleFunc("/ws/bind", classifierServer.bindSocket)

	// Server HTTP server on specified port, without a defined MUX
	http.ListenAndServe(":8081", nil)

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
