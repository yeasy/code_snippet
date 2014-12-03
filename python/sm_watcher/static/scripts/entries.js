<script>
    var ws = new WebSocket('ws://192.168.56.101:9000/ws');
    var $message = $('#message');
    ws.onopen = function(){
      $message.attr("class", 'label label-success');
      $message.text('open');
    };

    ws.onmessage = function(ev){
      var json = JSON.parse(ev.data);
      var content='';
     $.each(json, function(i,item){
        var newRow = "<tr>" +
        "<td><a href="+item.url+">"+item.title+"</a></td>" +
        "<td>"+item.ts+"</td>" +
        "</tr>";
        content += newRow;
    });
      $('#tbody_entries').html(content);
    };

    ws.onclose = function(ev){
      $message.attr("class", 'label label-important');
      $message.text('closed');
    };

    ws.onerror = function(ev){
      $message.attr("class", 'label label-warning');
      $message.text('error occurred');
    };
  </script>
