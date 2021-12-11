
// var checkDMs = setInterval(recieveDM, 3000); - when not using websockets
var curUser = "";

var firstRead=true;

// Establish a WebSocket connection with the server
const socket = new WebSocket('ws://' + 'localhost:8000' + '/websocket');



// Call the addMessage function whenever data is received from the server over the WebSocket
socket.onmessage = readMessage;
function readMessage(message) {
  if (firstRead==true){
    theData = JSON.parse(message.data);
    //thelist=theData["users"];
    generateUserList(theData)
  }
  firstRead=false;
}

/*
// Allow users to send messages by pressing enter instead of clicking the Send button
document.addEventListener("keypress", function (event) {
   if (event.code === "Enter") {
       sendMessage();
   }
});

// Read the name/comment the user is sending to chat and send it to the server over the WebSocket as a JSON string
// Called whenever the user clicks the Send button or pressed enter
function sendMessage() {
   const chatName = document.getElementById("chat-name").value;
   const chatBox = document.getElementById("chat-comment");
   const comment = chatBox.value;
   chatBox.value = "";
   chatBox.focus();
   if(comment !== "") {
       socket.send(JSON.stringify({'username': chatName, 'comment': comment}));
   }
}

// Called when the server sends a new message over the WebSocket and renders that message so the user can read it
function addMessage(message) {
   const chatMessage = JSON.parse(message.data);
   let chat = document.getElementById('chat');
   chat.innerHTML += "<b>" + chatMessage['username'] + "</b>: " + chatMessage["comment"] + "<br/>";
}

*/


















function getUsers(){
  var x = new XMLHttpRequest();
  var url = "/users";

  x.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
        var jsonStuff = JSON.parse(this.responseText);
        console.log("we got : " + this.responseText + " from the server");
        generateUserList(jsonStuff);

  }}
  x.open("POST", url, true);
  x.send();
}



// {"user1": "imagenameinserver", "user2": "anotherimage"}
function generateUserList(json) {

  userDiv = document.getElementById("userList");

  // remove everything from userlist and regenerate it if a login status changes

  var i=0;

  for (let key in json) {
    console.log("This should not be a number: "+key);
    // display user on the userlist
    i+=1;
    // include user's profile picture
    var img = document.createElement("IMG");
    img.setAttribute("class", "profilePic");
    var imgSrc = "/image/"+json[key];
    img.setAttribute("src", imgSrc);
    var imgAlt = "profile pic for "+key;
    img.setAttribute("alt", imgAlt);
    userDiv.appendChild(img);

    // include user and text field
    var userForm = document.createElement("FORM");
    var path = "/homepage/"+key; // this path allows us to get a username from message
    userForm.setAttribute("action", path);
    userForm.setAttribute("method", "POST");
    userForm.setAttribute("enctype", "multipart/form-data");
    idFor = "mess"+i.toString()

    var lab = document.createElement("LABEL");
    lab.setAttribute("for", idFor);
    lab.appendChild( document.createTextNode(key) );
    userForm.appendChild(lab);

    var inp = document.createElement("INPUT");
    inp.setAttribute("type", "text");
    inp.setAttribute("id", idFor);
    inp.setAttribute("name", "message");
    userForm.appendChild(inp);

    var inp2 = document.createElement("INPUT");
    inp2.setAttribute("type", "submit");
    inp2.setAttribute("value", "Send");
    userForm.appendChild(inp2);

    document.getElementById("userList").appendChild(userForm);

    // sending a message with this will send a post request to path /homepage/user
    // we should keep track of logged in users with a dictionary of users mapped to their address
  }
}

// unused if using websockets
function recieveDM(){
  // this will ask the server for any dms waiting to be seen by this client
  // when the dm is sent, the server stops holding the dm
  // will get empty dict if there are no dm's

    // this gets all the meals from the server in a JSON
    var x = new XMLHttpRequest();
    var url = "/dm"; // we could probably just find the username through the client dict

    x.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
          var jsonStuff = JSON.parse(this.responseText);
          console.log("we got : " + this.responseText + " from the server");
          if (jsonStuff.keys().length() != 0) {
            gotDM(jsonStuff);
          }

    }}
    x.open("POST", url, true);
    x.send();

}


function gotDM(someJSON){
  // {"user": "message"}
  keys = someJSON.keys()[0];
  mess = someJSON[keys[0]];
  alert(("user: "+someJSON[keys[0]]+" message: " + mess));
}
