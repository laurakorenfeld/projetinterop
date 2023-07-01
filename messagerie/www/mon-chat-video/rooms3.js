var app = require("express")();
var http = require('http').Server(app);
var io = require('socket.io')(http);

app.get('/', function (req, res) {
    res.sendFile(__dirname + '/indexRooms.html');
});

var rooms = [];
var maxUsersPerRoom = 2;

io.on('connection', function (socket) {
    var joinedRoom = false;

    // Find a room with available space or create a new room
    for (var i = 0; i < rooms.length; i++) {
        if (rooms[i].length < maxUsersPerRoom) {
            socket.join(rooms[i].name);
            rooms[i].push(socket.id);
            joinedRoom = true;
            break;
        }
    }

    // If no available room found, create a new room
    if (!joinedRoom) {
        var newRoom = {
            name: "room-" + (rooms.length + 1),
            users: [socket.id]
        };
        socket.join(newRoom.name);
        rooms.push(newRoom);
    }

    // Update room user count and send to all users in the room
    var currentRoom = rooms.find(room => room.users && room.users.includes(socket.id));
    var userCount = currentRoom.users.length;
    io.sockets.in(currentRoom.name).emit('userCount', userCount);

    // Handle user disconnection
    socket.on('disconnect', function () {
        var index = currentRoom.users.indexOf(socket.id);
        if (index !== -1) {
            currentRoom.users.splice(index, 1);
            userCount = currentRoom.users.length;
            io.sockets.in(currentRoom.name).emit('userCount', userCount);

            // Repopulate the room if all users left
            if (userCount === 0) {
                var roomIndex = rooms.indexOf(currentRoom);
                rooms.splice(roomIndex, 1);
            }
        }
    });
});

http.listen(3000, function () {
    console.log('listening on localhost:3000');
});
