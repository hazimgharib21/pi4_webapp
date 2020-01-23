var socket = io.connect('http://' + document.domain + ':' + location.port);

socket.on('connect', function(){
  socket.emit('client_connected', {data: 'New Client!'});
})

socket.on('dynamic_system_data', function(msg){
  console.log(msg);
  $('#cpu-usage').html(msg.CPU.Usage);
  $('#cpu-freq').html(msg.CPU.Frequency);
})

socket.on('static_system_data', function(msg){
  $('#cpu-min-freq').html(msg.CPU.min_freq);
  $('#cpu-max-freq').html(msg.CPU.max_freq);
})
