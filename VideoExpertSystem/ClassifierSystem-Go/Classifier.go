package main

import (
	"io"
	"net/http"
)

// Handles GET request for classifying a specified image
func handleClassify(w http.ResponseWriter, req *http.Request) {

	// Get the image path query
	var imagePath = req.URL.Query().Get("image")

	// Make sure image path is specified
	if imagePath != "" {
		io.WriteString(w, imagePath)
	}

}

// Main function
func main() {

	// Handler for classify function
	http.HandleFunc("/classify", handleClassify)

	// Server HTTP server on specified port, without a defined MUX
	http.ListenAndServe(":8081", nil)
}
