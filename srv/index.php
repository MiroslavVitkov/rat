<?php


require 'Parsedown.php';  # A markdown parser.


$h = date('H');
if( $h < 5 )
{
    $pic = 'res/cyber_rat.png';
}
elseif( $h < 11 )
{
    $pic = 'res/day_rat.png';
}
elseif( $h < 20 )
{
    $pic = 'res/saint_rat.png';
}
else
{
    $pic = 'res/asm_rat.png';
}

$readme = file_get_contents('/opt/rat/README.md');

# As a text file
#$readme_html = nl2br(htmlspecialchars($readme));  # Convert line breaks and escape HTML

# Or as parsed markdown.
$Parsedown = new Parsedown();
$readme_html = $Parsedown->text($readme);  # Convert Markdown to HTML


?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>rat</title>
    <link rel="icon" type="image/png" href="res/icon.png">
    <style>
        body {
            background-color: black;
            color: white;
            font-family: monospace;
        }
        #chat {
            border: 1px solid #888;
            padding: 8px;
            margin-top: 20px;
            max-width: 600px;
        }
        #messages {
            max-height: 200px;
            overflow-y: auto;
            margin-bottom: 10px;
        }
        input[type="text"] {
            width: 80%;
            padding: 4px;
        }
        button {
            padding: 4px;
        }
    </style>
</head>
<body>
    <img src="<?php echo $pic; ?>" alt="Saint Rat" style="max-width: 100%; height: auto;" />
    <pre><span class="inner-pre" style="font-size: 14px"><?php echo $readme_html; ?></span></pre>

    <noscript><p>JavaScript is required for chat functionality.</p></noscript>

    <div id="chat">
        <div id="messages"></div>
        <input type="text" id="input" placeholder="Say something...">
        <button onclick="sendMessage()">Send</button>
    </div>

    <script>
        const messagesDiv = document.getElementById('messages');
        const input = document.getElementById('input');

        function sendMessage() {
            const text = input.value.trim();
            if (text === '') return;
            const line = document.createElement('div');
            line.textContent = '> ' + text;
            messagesDiv.appendChild(line);
            input.value = '';
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    </script>
</body>
</html>
