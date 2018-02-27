package main

import (
	"log"
	"time"

	"github.com/gorilla/websocket"
)

// PACKETDATA DEFINITIONS
// Packet data defining data to send to client
type PacketData struct {
	cid       string
	data      []byte
	timestamp time.Time
}

func (p *PacketData) toBytes() []byte {
	stringValue := `{ "cid": "` + p.cid + `", "data":"` + string(p.data) + `"}`
	return []byte(stringValue)
}

// Channel class is initialized with a websocket connection, and maintains the
// 		connection active, recieving and transmitting data asynchronously with
// 		go routines and a classifier instance.

// CHANNEL DEFINITIONS
// Channel contains websocket connection, classifier, and a data buffer
type Channel struct {
	conn       *websocket.Conn
	classifier *Classifier
	send       chan PacketData
}

// Create a new channel with the specified websocket connection
func NewChannel(conn *websocket.Conn) *Channel {

	c := &Channel{
		conn: conn,
		send: make(chan PacketData, 10), // buffered queue of size 10 for send
	}

	c.classifier = NewClassifier()

	// Spawn reader and writer processes
	go c.reader()
	go c.writer()

	return c
}

func (c *Channel) Close() {
	err := c.conn.Close()
	if err != nil {
		log.Print(err)
	}

	c.conn = nil
	c.classifier = nil
	c.send = nil
}

// Define channel reading routine
func (c *Channel) reader() {
	for {
		// Make sure connection is active
		if c.conn != nil {
			packet, msgType := c.readFromSocket(c.conn)
			go c.handleIncomingPacket(packet, msgType)
		} else {
			break
		}
	}
}

// Define channel writing routine
func (c *Channel) writer() {

	for data := range c.send {
		err := c.writeToSocket(c.conn, websocket.TextMessage, data.toBytes())
		if err != nil {
			log.Print("Could not write packet, closing channel...")
			c.Close()
		}
		log.Printf("Sent results in %.2f seconds!", time.Since(data.timestamp).Seconds())
	}
}

func (c *Channel) readFromSocket(conn *websocket.Conn) ([]byte, int) {
	msgType, msg, err := conn.ReadMessage()
	if err != nil {
		log.Println("Could not read message, closing channel...")
		c.Close()
		return nil, msgType
	} else {
		return msg, msgType
	}
}

func (c *Channel) writeToSocket(conn *websocket.Conn, msgType int, data []byte) error {
	return conn.WriteMessage(msgType, data)
}

func (c *Channel) handleIncomingPacket(data []byte, msgType int) {

	startTime := time.Now()

	// If binary message, image bytes are being sent
	if msgType == websocket.BinaryMessage {
		log.Printf("Recieved Image at %s", startTime.String())

		// Get result string from image classifier
		resultString := c.classifier.ClassifyImage(data)

		packetData := &PacketData{
			cid:       "RESULTS",
			data:      []byte(resultString),
			timestamp: startTime,
		}

		// Send results over websocket to client
		c.send <- *packetData

	} else if msgType == websocket.TextMessage {
		log.Print("Recieved Text Message:")
		log.Print(data)
	}
}
