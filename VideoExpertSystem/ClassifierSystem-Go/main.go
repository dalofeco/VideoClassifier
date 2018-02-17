package main

import (
	"io"
	"io/ioutil"
	"log"
	"net/http"
)

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
