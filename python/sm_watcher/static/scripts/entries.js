<script>
    var ws = new WebSocket('ws://localhost:8000');
    var $message = $('#message');
    ws.onopen = function(){
      $message.attr("class", 'label label-success');
      $message.text('open');
    };
    ws.onmessage = function(ev){
      alert(ev.data)
      $message.attr("class", 'label label-info');
      $message.hide();
      $message.fadeIn("slow");
      $message.text('recieved message');
      var json = JSON.parse(ev.data);
      $('#' + json.id).hide();
      $('#' + json.id).fadeIn("slow");
      $('#' + json.id).text(json.value);
      var $rowid = $('#row' + json.id);
      if(json.value > 500){
        $rowid.attr("class", "error");
      }
      else if(json.value > 200){
        $rowid.attr("class", "warning");
      }
      else{
        $rowid.attr("class", "");
      }
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
