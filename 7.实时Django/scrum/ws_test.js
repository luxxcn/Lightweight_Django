// websocket 测试代码
// 复制到浏览器的console中执行

var socket = new WebSocket('ws://localhost:8080/123');
socket.onopen = function() {
    console.log('Connection is open!');
    socket.send('ping');
};
socket.onmessage = function (message) {
    console.log('New message: ' + message.data);
    if(message.data == 'ping') {
        socket.send('pong');
    }
};